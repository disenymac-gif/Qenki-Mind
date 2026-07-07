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


## Dependency Inversion for Canonical Levels
Higher-level canonical documents define contracts and properties; they do not name or depend on concrete implementation identities. Lower-level implementation documents satisfy the contracts defined above them. No canonical document may require knowledge of a specific repository directory, runtime class, or organ name unless that identity is itself part of the relevant level's explicit contract.

## Canonical Change Constraint Matrix
Each canonical level is constrained by the kind of change that may legitimately force an update. Changes outside the listed causes are architectural leakage.

| Level | May change by | Must not change by |
|---|---|---|
| Ontology | Evolution of the cognitive model | Organ reorganization, runtime changes, storage changes |
| ADR | New architectural decision | Implementation changes |
| Cognitive Architecture | New functional organization | Technology changes |
| Organs | Redistribution of responsibilities | Directory names or infrastructure changes |
| Runtime / Repository | Technology, persistence, deployment | Conceptual changes |

## Governance Test
If a change to a lower-level implementation forces an update to a higher-level canonical level, the design contains architectural leakage. Higher-level documents only change when their own level's abstraction changes.

## Canonical Level Dependency Principle
Canonical levels depend only on abstractions defined at their own level or above. Concrete implementations depend on canonical contracts, never the reverse.

## Stability Gradient
Higher canonical levels should change less frequently than lower ones. Stability is a deliberate architectural property, not an accident of history.

| Level | Expected stability |
|---|---|
| Ontology | Very high (years) |
| Governance | Very high |
| ADR | High |
| Cognitive Architecture | Medium |
| Organs | Medium-high |
| Runtime / Repository | Low (frequent changes) |

## Architectural Health
Architectural health improves when changes concentrate in lower levels while higher levels remain stable. Frequent Ontology or ADR churn is a sign of architectural volatility. Runtime and repository changes are expected to be the most common.

## Volatility vs Leakage
Architectural leakage occurs when a lower-level change forces an unnecessary higher-level change. Architectural volatility occurs when a higher-level document changes too frequently for its level. These are distinct pathologies and must be evaluated separately.

## Canon Introduction Constraint
No new principle may be added to the canon unless it resolves a class of problems not already expressible by existing principles. This protects the canon from redundant growth and preserves explanatory economy.

## Canon Completeness Test
For any change, the lowest applicable level should be identified first. The canonical questions are: what concept changes (Ontology), what decision changes (ADR), what contract changes (Cognitive Architecture), what implementation changes (Organs), and what technology changes (Runtime / Repository). The correct answer should always be the lowest level that fully resolves the change.

## Independence Check
Before a new governance principle is added, test whether removing it would reduce the canon's ability to decide real cases. If not, the principle is likely a corollary of an existing rule and should not exist as an independent canon rule.

## Canon State
A canon is complete when it can explain all relevant changes. A canon is closed when any new principle must justify why existing principles are insufficient.

## Principle Validation
Each governance principle must declare: Purpose, Scope, Validation, and Failure Mode. Validation states what evidence would show the principle is no longer sufficient. Failure Mode states what happens when the principle no longer predicts or governs real cases correctly.

## Empirical Modification Rule
Any proposal to add or modify a canon principle must be accompanied by at least one real case that existing principles cannot resolve unambiguously. If no such case exists, the burden of proof remains on the proposer and the canon should not expand.

## Canon as Falsifiable System
The canon is treated as a falsifiable system of governance hypotheses. Principles persist because they continue to explain and predict real architectural decisions; they fail when they no longer do so.

## Governance Scope
This document governs Qenki-Mind only. Rules that govern how canons, ADRs, specifications, or registries are validated across the broader Qenki ecosystem belong to Qenki-Core Governance, not to Qenki-Mind. Qenki-Mind may reference such rules only as external constraints, not as its own architectural content.

## Scope Leakage Test
If a rule would still make sense after Qenki-Mind is removed, that rule likely does not belong in Qenki-Mind Governance. Such rules are candidates for Qenki-Core Governance.

## Rule Type Classification
Governance rules determine who decides, what is owned, how scope is bounded, how change is processed, and how exceptions are handled. Standards define what artifacts must satisfy. System-specific architecture describes how a concrete system implements the governing contracts and standards.

## Classification Test
Ask three questions: who decides (Governance), what must be satisfied (Standard), and how is it implemented (System-specific architecture). If a rule does not determine decision authority, it is not Governance.

## Standards Boundary
Principles such as Principle Validation, Canon Completeness, Independence Check, Canon Closed, Falsifiability, and Canon Introduction Constraint are standards of canon quality, not Governance rules of Qenki-Mind. Qenki-Mind may reference them as external standards if required, but they belong to the broader Qenki-Core standards layer.

## Normative Knowledge Dimensions
Normative knowledge in the ecosystem is divided into four orthogonal dimensions: Governance, Standards, Processes, and Policies. Governance answers who has authority over what object. Standards answer what properties the object must satisfy. Processes answer how the object changes over time. Policies answer what restrictions and exceptions apply.

## Object-Governance Matrix
Each object can be governed, standardized, processed, and constrained independently. A document may participate in more than one dimension, but each dimension must be explicitly declared rather than mixed implicitly.

| Object | Governance | Standards | Processes | Policies |
|---|---|---|---|---|
| Canon | ✓ | ✓ | ✓ | ✓ |
| ADR | ✓ | ✓ | ✓ | ✓ |
| Specification | ✓ | ✓ | ✓ | ✓ |
| Registry | ✓ | ✓ | ✓ | ✓ |

## Document Purity
Canonical and operational documents should avoid mixing authority, requirements, workflows, and restrictions unless they explicitly declare the mixed role. If a document carries more than one normative dimension, the dimensions must be separated into named sections.
