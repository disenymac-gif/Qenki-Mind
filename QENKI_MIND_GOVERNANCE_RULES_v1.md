# ADR Lifecycle Governance

## Purpose
This section defines the governance lifecycle of Architectural Decision
Records (ADRs) within Qenki-Mind. It establishes what an ADR is, what
"Accepted" means, how ADRs relate to the six canonical documents, and how
authority flows from decision to canonical truth.

## Rule 1: ADRs Are Normative, Not Merely Historical Proposals
An ADR that reaches Accepted status is a normative architectural decision.
It is not a suggestion, a discussion record, or optional guidance. Once
Accepted, its invariants are binding on any implementation of Qenki-Mind.

## Rule 2: Accepted ADRs Become Part of the Canonical Architecture
The invariants stated in an Accepted ADR are, from the moment of
acceptance, part of the canonical architecture of Qenki-Mind, with the same
binding force as the six canonical documents themselves.

## Rule 3: The Six Canonical Documents Remain the Sole Authoritative Source
The ADR directory is historical, not authoritative. Its purpose is to
preserve the reasoning and context behind each decision. The authoritative
architecture is, and remains, the six canonical documents
(QENKI_MIND_GOVERNANCE_RULES_v1.md, QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md,
QENKI_MIND_ONTOLOGY_v1.md, QENKI_MIND_ORGANS_v1.md,
QENKI_MIND_COGNITIVE_CONTRACT_LAYER_v1.md,
QENKI_MIND_INTERFACE_BOUNDARY_SPECIFICATION_v1.md) once they have absorbed
every Accepted ADR's invariants.

## Rule 4: Canonical Documents Must Absorb an ADR Before Implementation Begins
An Accepted ADR does not by itself complete the architecture. Every
canonical document listed in that ADR's "Affected Canonical Documents"
section must be updated to reflect the ADR's invariants before any
implementation may rely on that decision. Until this absorption occurs,
the ADR is Accepted but not yet Closed.

## Rule 5: An ADR Is Closed Once Absorption Is Complete
An ADR transitions from Accepted to Closed once all canonical documents it
affects have been updated to reflect its invariants. Closed is the terminal
status of a properly absorbed ADR. The ADR document itself is not deleted
or edited to reflect this transition beyond an update to its own Status
field; the substantive decision recorded in the ADR remains unchanged.

## Rule 6: ADRs Are Never Edited After Acceptance
Once an ADR reaches Accepted status, its Context, Decision, and
Architectural Invariants sections are permanent and immutable. If
circumstances require a change to a previously Accepted decision, this
must occur through a new ADR that explicitly supersedes the prior one.

## Rule 7: Superseding Authority
A later ADR may supersede an earlier one only by explicit declaration
within its own Context and Decision sections, naming the specific ADR it
supersedes and the specific invariants it replaces. Superseding authority
rests with whichever architectural review process is in force at the time
the new ADR is proposed; no ADR may be silently overridden by
implementation practice or by a canonical document edit alone.

## Rule 8: ADRs May Never Contradict One Another Simultaneously
At any point in time, the set of all Accepted and Closed ADRs, together
with the six canonical documents, must be internally consistent. If a new
ADR would contradict an existing one without explicitly superseding it,
the new ADR cannot be Accepted until the contradiction is resolved through
explicit supersession.

## Rule 9: Meaning of "Accepted"
"Accepted" means the architectural decision itself has been reviewed and
approved as binding. It does not mean the canonical documentation has yet
been updated to reflect it. The distinct status "Closed" (Rule 5) marks
that further step. An ADR may exist in Accepted status for a period of
time before reaching Closed, but may never be treated as optional or
provisional during that interval — its invariants are binding immediately
upon Acceptance, regardless of documentation absorption status.

## ADR Lifecycle Diagram

# Repository Topology Derivation

## Purpose
This section defines how canonical architecture may be translated into
repository topology (top-level directories and persistent filesystem
domains). It was absorbed from ADR-007 to close a governance ambiguity
distinct from the behavioral ambiguities addressed by ADR-001 through
ADR-006: this principle governs how architecture becomes filesystem
structure, not how the organism reasons.

## Rule 1: Topology Is Never Inferred From Semantics
The semantic properties of architectural concepts — permanence,
importance, centrality, durability, or any other ontological or
organizational property — shall never be interpreted as implicitly
requiring a corresponding repository domain, directory, or persistent
storage.

## Rule 2: Explicit Topological Basis Is Required
A repository domain may be materialized only when the canonical
architecture explicitly establishes: that such a domain exists; its
architectural purpose; its ownership; and its role within the organism.

## Rule 3: New Concepts Do Not Create New Directories By Default
The introduction of a new concept into the Ontology does not, by itself,
create or require a new repository domain. Only explicit architectural
topology creates directories.

## Rule 4: ADR Scope Clarification
This principle also clarifies when an ADR is required across the
project generally:
- Behavioral ambiguities require an ADR.
- Governance ambiguities require an ADR.
- Editorial clarifications with no normative effect do not require an
  ADR.
- Operational documents (`README.md`, `REPOSITORY_MAP.md`,
  `MATURITY_STATUS.md`, etc.) do not require an ADR.

## Rule 5: Epistemic Discipline in Absence of Canonical Basis
Absence of an identified canonical basis for a capability or its
repository topology is an epistemic statement about the current state of
review, not an ontological claim that no such basis exists. Operational
documents reporting such a capability must distinguish between:
- capability and topology canonically defined;
- capability canonically supported, topology not defined; and
- capability not currently canonically identified.
None of these classifications may be treated as permanent or as
foreclosing future canonical revision.

## Rule 6: Contingent, Not Permanent, Scope
This principle governs how topology is derived, not which topology must
exist forever. A repository domain currently lacking sufficient
architectural basis for materialization may become materializable in
the future, if a subsequent canonical document revision or a future
Accepted ADR, once absorbed, explicitly establishes that domain's
existence, purpose, ownership, and role.

## Origin
Absorbed from QENKI_MIND_ADR_007_REPOSITORY_TOPOLOGY_DERIVATION_v1.md.
