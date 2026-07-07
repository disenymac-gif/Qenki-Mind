# QENKI_MIND_COGNITIVE_CONTRACT_LAYER_v1

## Purpose
Defines the nine implementation-independent semantic contracts governing
the stable boundary between Qenki-Mind and the rest of Qenki® OS. These
nine contracts collectively constitute Mind's domain-level agreement with
the ecosystem: what Mind requires to reason, and what it guarantees in
return.

## Owner
Qenki-Mind (normative canonical document)

## Lifecycle
Stable. Contract semantics are frozen; one contract's completion semantics
have been made explicit through an accepted Architectural Decision Record.

## Contract 01: Constitution — Mandatory
Guarantees a coherent, current statement of Identity, Values, Philosophy,
and Communication Contract. Failure suspends Decision and Expression
activity.

## Contract 02: Intent — Partial
Guarantees a bounded, current set of active strategic aims. Failure leaves
Opportunities unscored rather than falsely ranked.

## Contract 03: Perceptible World — Mandatory
Guarantees continuous raw signal. Failure halts all forward cognitive
progress.

## Contract 04: Situational Awareness — Optional
Guarantees discrete, verifiable facts about present conditions. Failure
widens Opportunity scoring uncertainty margins.

## Contract 05: Brand Expression Constraint — Mandatory
Guarantees checkable brand voice and visual constraints. Failure holds all
pending Expressions in draft state indefinitely.

## Contract 06: Externalization — Mandatory
Guarantees delivery confirmation and traceability for released Expressions.
Failure leaves Expressions in an unresolved state.

## Contract 07: Consequence — Optional (short-term), critical (long-term)

**Completion semantics (binding, from ADR-004):** Every prediction tied to
a Decision or Expression carries a maximum waiting period for Consequence
data, owned and set by the Learning & Reflection Organ as a tunable
Reasoning Parameter. A prediction exceeding this period without data
arriving is permanently recorded as "unresolved — no data received," a
terminal state distinct from both confirmation and disconfirmation.
Absence of data must never be interpreted as disconfirmation. Calibration
rhythms proceed using whatever has resolved at the time each rhythm fires
and never block waiting on outstanding predictions.

## Contract 08: Human Judgment — Mandatory
Guarantees non-silent, authoritative human adjudication for every gated
item. Failure means gated items accumulate visibly rather than silently
defaulting.

## Contract 09: Persistence — Mandatory
Guarantees write durability and detectable loss for committed knowledge.
Failure is flagged explicitly rather than reasoned around silently.

## Architectural Decisions Incorporated
- ADR-004: Consequence Contract Completion Semantics — Status: Closed

## Relationships
Consulted alongside QENKI_MIND_INTERFACE_BOUNDARY_SPECIFICATION_v1.md,
which declares the organism-wide dependencies satisfying Contracts 01, 02,
and 05.
