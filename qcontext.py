#!/usr/bin/env python3
"""
qcontext.py
Objective, read-only repository inspection utility.
Reports facts only. Performs no interpretation, classification, or content analysis.
Run from repository root: python3 qcontext.py

Composition rule: each inspection capability is an independent function.
main() only orchestrates. No capability is embedded as an ad hoc block.

Exit code contract (public API — do not change meanings, only add new codes):
  0  report generated successfully
  1  fatal error (e.g. path is not a Git repository)
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent
README_HEADER_DUMP_THRESHOLD = 6


def run(cmd):
    try:
        r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, timeout=10)
        out = r.stdout.strip()
        err = r.stderr.strip()
        return out if out else (err if err else "(empty)")
    except Exception as e:
        return f"[error running {' '.join(cmd)}: {e}]"


def section(title):
    print(f"\n{'='*70}\n{title}\n{'='*70}")


def check_git_repo():
    r = subprocess.run(
        ["git", "rev-parse", "--is-inside-work-tree"],
        cwd=REPO, capture_output=True, text=True, timeout=10
    )
    if r.returncode != 0 or r.stdout.strip() != "true":
        print("Error: current directory is not a Git repository.")
        print("Expected repository root:")
        print(f"  {REPO}")
        sys.exit(1)


def report_repository_path():
    section("REPOSITORY PATH")
    print(str(REPO))


def report_git_identity():
    section("CURRENT BRANCH")
    print(run(["git", "rev-parse", "--abbrev-ref", "HEAD"]))

    section("HEAD COMMIT")
    print(run(["git", "log", "-1", "--format=%H %ci %s"]))

    section("LATEST TAG (by creation)")
    print(run(["git", "describe", "--tags", "--abbrev=0"]))

    section("ALL TAGS")
    print(run(["git", "tag", "-l"]))


def report_git_status():
    section("GIT STATUS (short, branch info)")
    print(run(["git", "status", "-sb"]))

    section("RECENT COMMITS (last 15)")
    print(run(["git", "log", "--oneline", "-15"]))

    section("MODIFIED FILES (tracked, unstaged or staged)")
    print(run(["git", "diff", "HEAD", "--name-only"]))

    section("UNTRACKED FILES")
    print(run(["git", "ls-files", "--others", "--exclude-standard"]))


def report_top_level_entries():
    section("TOP-LEVEL ENTRIES (directories and files, depth 1)")
    entries = sorted(REPO.iterdir(), key=lambda p: (not p.is_dir(), p.name))
    for p in entries:
        if p.name.startswith(".git"):
            continue
        kind = "DIR " if p.is_dir() else "FILE"
        print(f"  [{kind}] {p.name}")


def report_remotes():
    section("REMOTE(S)")
    print(run(["git", "remote", "-v"]))


def report_python_version():
    section("PYTHON VERSION")
    print(sys.version)


def _top_level_dirs():
    return [
        p for p in sorted(REPO.iterdir(), key=lambda x: x.name)
        if p.is_dir() and not p.name.startswith(".git")
    ]


def report_readme_headers():
    section("README.md HEADER INVENTORY (per top-level directory)")
    print("Objective structural fact: lines starting with '## ' in each directory's")
    print("top-level README.md, in file order. No semantic interpretation performed.")
    for p in _top_level_dirs():
        readme = p / "README.md"
        if not readme.exists():
            print(f"\n  {p.name}/README.md -> MISSING")
            continue
        try:
            lines = readme.read_text(encoding="utf-8", errors="replace").splitlines()
        except Exception as e:
            print(f"\n  {p.name}/README.md -> [error reading: {e}]")
            continue
        headers = [l[3:].strip() for l in lines if l.startswith("## ")]
        print(f"\n  {p.name}/README.md -> {len(headers)} '## ' headers:")
        for h in headers:
            print(f"    - {h}")


def report_small_readmes(threshold=README_HEADER_DUMP_THRESHOLD):
    section(f"FULL RAW CONTENT: README.md files with <= {threshold} sections (verbatim)")
    print("Objective fact: complete, unmodified file content. No interpretation.")
    print("Threshold chosen for volume control only (avoids dumping large files);")
    print("does not imply any judgment about the files' architectural role.")
    for p in _top_level_dirs():
        readme = p / "README.md"
        if not readme.exists():
            continue
        try:
            text = readme.read_text(encoding="utf-8", errors="replace")
        except Exception:
            continue
        header_count = len([l for l in text.splitlines() if l.startswith("## ")])
        if header_count <= threshold:
            print(f"\n  --- BEGIN {p.name}/README.md (verbatim) ---")
            print(text)
            print(f"  --- END {p.name}/README.md ---")


def report_end():
    section("END OF REPORT")
    print("Objective facts only. No content interpreted. No files modified. No git write operations executed.")


def main():
    check_git_repo()
    report_repository_path()
    report_git_identity()
    report_git_status()
    report_top_level_entries()
    report_remotes()
    report_python_version()
    report_readme_headers()
    report_small_readmes()
    report_end()
    sys.exit(0)


if __name__ == "__main__":
    main()
