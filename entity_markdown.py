"""
entity_markdown.py

Reusable, dependency-free parser and serializer for Qenki-Mind canonical
entity Markdown files.

Scope (deliberately narrow):
- Entities are Markdown files composed of second-level headers ("## Section")
  followed by freeform content (plain text and/or "- " bullet lists) until
  the next "## " header or end of file.
- An optional top-level title ("# Entity Name") may precede the first section.
- No support for arbitrary Markdown (no nested headers below "##", no tables,
  no inline HTML parsing). This is intentional: the format is owned by
  Qenki-Mind, not by external Markdown consumers.

This module has no external dependencies. It uses only string operations
that are deterministic and reversible: parse(serialize(x)) == x for any
entity built from the canonical section structure.
"""
from __future__ import annotations
from collections import OrderedDict
from typing import Optional


class EntityParseError(Exception):
    """Raised when a Markdown file does not conform to the canonical entity structure."""


def parse_entity_markdown(text: str) -> "OrderedDict[str, str]":
    """
    Parse canonical entity Markdown into an ordered mapping of
    section title -> raw section content (stripped, may contain
    plain text and/or "- " bullet lines).

    The optional leading "# Title" line, if present, is stored under
    the special key "__title__".

    Sections are identified strictly by lines starting with "## "
    (exactly two hashes followed by a space). Lines with a different
    number of hashes are treated as regular content, not as sections.
    """
    lines = text.splitlines()
    sections: "OrderedDict[str, str]" = OrderedDict()

    i = 0
    n = len(lines)

    if i < n and lines[i].startswith("# ") and not lines[i].startswith("## "):
        sections["__title__"] = lines[i][2:].strip()
        i += 1

    current_title: Optional[str] = None
    current_buffer: list[str] = []

    def flush():
        if current_title is not None:
            content = "\n".join(current_buffer).strip("\n")
            content = content.strip()
            if current_title in sections:
                raise EntityParseError(f"Duplicate section header: '## {current_title}'")
            sections[current_title] = content

    while i < n:
        line = lines[i]
        if line.startswith("## "):
            flush()
            current_title = line[3:].strip()
            current_buffer = []
        else:
            if current_title is None:
                if line.strip() != "":
                    raise EntityParseError(
                        f"Content found before any '## ' section header: {line!r}"
                    )
            else:
                current_buffer.append(line)
        i += 1

    flush()

    if not sections or (len(sections) == 1 and "__title__" in sections):
        raise EntityParseError("No '## ' section headers found in entity Markdown.")

    return sections


def get_section(sections: "OrderedDict[str, str]", title: str, required: bool = True) -> str:
    """
    Retrieve a section's content by exact title.
    Raises EntityParseError if required and missing.
    Returns "" if not required and missing.
    """
    if title in sections:
        return sections[title]
    if required:
        raise EntityParseError(f"Required section '## {title}' not found.")
    return ""


def parse_bullet_list(section_content: str) -> list[str]:
    """
    Parse a section's content as a flat bullet list.
    Lines must start with '- '. Non-bullet lines are ignored (not raised),
    since some sections mix a short intro line with bullets.
    """
    items = []
    for line in section_content.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            items.append(stripped[2:].strip())
    return items


def serialize_entity_markdown(
    sections: "OrderedDict[str, str]",
    section_order: Optional[list[str]] = None,
) -> str:
    """
    Serialize an ordered mapping of section title -> content back into
    canonical entity Markdown.

    If section_order is provided, sections are emitted in that order;
    any sections present in `sections` but absent from `section_order`
    are appended afterward in their original relative order.
    If section_order is None, the insertion order of `sections` is used.

    Guarantee: parse_entity_markdown(serialize_entity_markdown(s)) == s
    for any `s` produced by parse_entity_markdown on a well-formed file.
    """
    working = OrderedDict(sections)
    title = working.pop("__title__", None)

    ordered_keys: list[str]
    if section_order is not None:
        ordered_keys = [k for k in section_order if k in working]
        remaining = [k for k in working.keys() if k not in ordered_keys]
        ordered_keys.extend(remaining)
    else:
        ordered_keys = list(working.keys())

    parts: list[str] = []
    if title is not None:
        parts.append(f"# {title}")
        parts.append("")

    for key in ordered_keys:
        parts.append(f"## {key}")
        parts.append("")
        content = working[key]
        if content:
            parts.append(content)
            parts.append("")
        else:
            parts.append("")

    text = "\n".join(parts)
    while text.endswith("\n\n\n"):
        text = text[:-1]
    if not text.endswith("\n"):
        text += "\n"
    return text


def build_bullet_section(items: list[str]) -> str:
    """Build section content as a bullet list from a list of strings."""
    return "\n".join(f"- {item}" for item in items)


# --- File I/O helpers (mechanical, no semantics) ---

from pathlib import Path
from typing import Union


def load_entity(path: Union[str, "Path"]) -> "OrderedDict[str, str]":
    """
    Read a canonical entity Markdown file from disk and parse it.
    Purely mechanical: delegates to parse_entity_markdown.
    Raises FileNotFoundError if the path does not exist, or
    EntityParseError if the content does not conform to the
    canonical section structure.
    """
    p = Path(path)
    text = p.read_text(encoding="utf-8")
    return parse_entity_markdown(text)


def save_entity(
    path: Union[str, "Path"],
    sections: "OrderedDict[str, str]",
    section_order: Optional[list[str]] = None,
) -> None:
    """
    Serialize sections into canonical entity Markdown and write to disk.
    Purely mechanical: delegates to serialize_entity_markdown.
    Creates parent directories if they do not already exist.
    Overwrites any existing file at `path`.
    """
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    text = serialize_entity_markdown(sections, section_order=section_order)
    p.write_text(text, encoding="utf-8")


# --- Structural validation (contract supplied externally, not assumed) ---

class EntityValidationError(Exception):
    """Raised when parsed sections do not satisfy an externally supplied contract."""


def validate_entity_structure(
    sections: "OrderedDict[str, str]",
    required_sections: list[str],
) -> None:
    """
    Verify that `sections` contains every section title listed in
    `required_sections`.

    This function makes no assumption about what a "complete" entity
    looks like. The caller supplies the contract explicitly, since
    different entity domains may have different required sections
    (this has only been confirmed for Decisions and Expressions so far;
    it is not assumed to be universal).

    Raises EntityValidationError listing all missing sections if any
    required section is absent. Does not check content of sections,
    only presence.
    """
    missing = [title for title in required_sections if title not in sections]
    if missing:
        raise EntityValidationError(
            f"Missing required section(s): {missing}"
        )

