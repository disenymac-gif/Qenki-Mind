# ADR-007: Repository Topology Derivation

## Status
Accepted

## Context
During materialization of Qenki-Mind's repository structure, a recurring
question emerged: when does a canonical architectural concept justify
the creation of a persistent repository domain (a top-level directory)?

Two candidate cases surfaced this ambiguity directly:

1. **Operational State** — `MATURITY_STATUS.md` names this as an
   operational-maturity capability. No canonical document explicitly
   defines a persistent repository requirement for reasoning-in-progress
   state, its owning organ, or its topology.
2. **Persistent Knowledge / Fact storage** — the Ontology establishes
   that a Fact, once promoted from a Belief, is permanent (the Promotion
   Invariant, absorbed via ADR-001). This is a strong semantic signal,
   but no canonical document explicitly establishes a repository domain,
   its ownership, or its architectural purpose for storing Facts.

In both cases, the underlying concept has durable or important semantic
properties, but no canonical text explicitly mandates a corresponding
filesystem domain. This is an architectural ambiguity, not an editorial
one: two architects following the same six canonical documents could
legitimately produce materially different repository topologies.

- One architect could infer that semantic permanence or centrality of a
  concept implies the concept requires its own repository domain (e.g.,
  "Fact is permanent, therefore `MEMORY_REPOSITORY/` must exist").
- Another architect could require an explicit topological declaration —
  purpose, ownership, and role — before materializing any domain.

These are not equivalent implementations. They produce different
filesystem architectures from the same canonical specification, which is
precisely the kind of externally observable behavioral/structural
divergence that warrants an ADR under this project's existing criteria.

### Architectural Rationale
Ontology defines concepts. Architecture defines responsibilities.
Governance defines how architecture becomes topology. This decision
belongs to the third category: it does not alter what any concept means
or which organ is responsible for it, only how canonical architecture is
permitted to be translated into filesystem structure.

## Decision
Repository topology shall be derived only from explicit architectural
declarations, never inferred from the semantic properties of the
concepts it contains.

- The semantic properties of architectural concepts (permanence,
  importance, centrality, durability, or any other ontological or
  organizational property) shall never be interpreted as implicitly
  requiring a corresponding repository domain, directory, or persistent
  storage.
- A repository domain may be materialized only when the canonical
  architecture explicitly establishes: that such a domain exists; its
  architectural purpose; its ownership; and its role within the
  organism.
- New concepts introduced into the Ontology do not, by default, create
  new directories. Only explicit architectural topology creates
  directories.
- ADR scope is clarified as follows: behavioral ambiguities require an
  ADR; governance ambiguities require an ADR; editorial clarifications
  with no normative effect do not require an ADR; operational documents
  (`README.md`, `REPOSITORY_MAP.md`, `MATURITY_STATUS.md`, etc.) do not
  require an ADR.

## Affected Canonical Documents
- QENKI_MIND_GOVERNANCE_RULES_v1.md

No other canonical document must absorb this decision. The rule governs
architectural governance itself, not ontology, organs, contracts, or
cognitive behavior.

## Consequences
- Under the current canonical architecture, neither
  `OPERATIONAL_STATE/` nor `MEMORY_REPOSITORY/` has sufficient
  architectural basis for materialization. Both capabilities remain
  reported only in `MATURITY_STATUS.md`, pending explicit canonical
  topology requirements. This is a statement about the current
  architecture, not a permanent prohibition — if a future canonical
  document, or a future Accepted ADR absorbed into the canonical
  documents, explicitly establishes such a domain, materialization
  becomes permissible without conflicting with this ADR.
- Future repository materialization work must verify explicit canonical
  topology declarations before creating any new top-level domain, rather
  than deriving domains from ontological or architectural semantics.
- This principle, once absorbed, will appear in
  `QENKI_MIND_GOVERNANCE_RULES_v1.md` as a permanent governance
  principle titled "Repository Topology Derivation," after which this
  ADR transitions to Closed, consistent with the lifecycle of ADR-001
  through ADR-006.
- `MATURITY_STATUS.md` continues to report the canonical architecture as
  Frozen throughout this process, since Frozen means changes occur only
  through the defined governance process, not that no change is
  possible.
