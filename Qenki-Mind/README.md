# Qenki-Mind

## What This Is
Qenki-Mind is the cognitive domain of Qenki® OS — an autonomous, local-first
reasoning organism whose purpose is to continuously deepen Qenki's
understanding of its customers, products, communication, sustainability,
and business. This README is an orientation document only. It is not
canonical architecture and does not duplicate the authoritative content
found in the documents it points to.

## Where the Canonical Architecture Is Defined
The canonical architecture of Qenki-Mind is defined by the following six
root-level documents, as governed by `QENKI_MIND_GOVERNANCE_RULES_v1.md`:

- `QENKI_MIND_GOVERNANCE_RULES_v1.md` — ownership, change control, and the
  ADR lifecycle governing how architectural decisions become canonical.
- `QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md` — the cognitive loop and the
  organism's natural rhythms.
- `QENKI_MIND_ONTOLOGY_v1.md` — the canonical vocabulary of cognitive
  objects and their transformation graph.
- `QENKI_MIND_ORGANS_v1.md` — the mission and authority boundaries of each
  of the eight cognitive organs.
- `QENKI_MIND_COGNITIVE_CONTRACT_LAYER_v1.md` — the nine implementation-
  independent semantic contracts with the rest of Qenki® OS.
- `QENKI_MIND_INTERFACE_BOUNDARY_SPECIFICATION_v1.md` — the organism-wide
  external dependency declarations.

## Where Architectural History Lives
`ADR/` contains the Architectural Decision Records that resolved the
organism's remaining behavioral ambiguities. Closed ADRs are historical
record only — their invariants have already been absorbed into the six
canonical documents above, which remain the sole authoritative source.

## Operational Repository
Everything outside the root canonical documents and `ADR/` represents the
organism's operational state. See `REPOSITORY_MAP.md` for the current
repository layout and `MATURITY_STATUS.md` for the current architectural
and operational maturity.

## How to Read This Repository
Start with the six canonical documents to understand what Qenki-Mind is.
Then consult `REPOSITORY_MAP.md` to understand where its current state
lives. Nothing in this repository should be understood by executing code —
every concept here is meant to be legible by reading Markdown alone.

## Ownership
This repository belongs exclusively to Qenki. It is not a generic AI
framework and does not compete with any other domain of Qenki® OS. Where
Qenki-Mind depends on knowledge owned elsewhere in the ecosystem (Identity,
Objectives, Brand Constraints), that dependency is declared explicitly in
`QENKI_MIND_INTERFACE_BOUNDARY_SPECIFICATION_v1.md` and never duplicated
here.
