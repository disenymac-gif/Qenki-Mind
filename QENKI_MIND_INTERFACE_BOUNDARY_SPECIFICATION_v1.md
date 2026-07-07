# QENKI_MIND_INTERFACE_BOUNDARY_SPECIFICATION_v1

## Purpose
Declares the organism-wide external dependencies of Qenki-Mind and how
each relates to the Cognitive Contract Layer, without presuming knowledge
of how the rest of Qenki® OS fulfills them.

## Owner
Qenki-Mind (normative canonical document)

## Lifecycle
Stable. Dependency declarations change only when a new organism-wide
dependency is identified or a contract is added; live synchronization
status for each dependency is tracked separately in HEALTH/, not here.

## Organism-Wide Dependency Declarations

### Dependency: Constitution
- Canonical Owner: Qenki-Frame
- Canonical Source: to be defined at integration
- Local Role: organism-wide behavioral constraint
- Contract Satisfied: Contract 01 — Constitution Contract
- Consumed by: Sense-Making, Decision, Expression, Critic

### Dependency: Objectives
- Canonical Owner: external strategic domain, to be defined at integration
- Canonical Source: to be defined at integration
- Local Role: organism-wide strategic intent
- Contract Satisfied: Contract 02 — Intent Contract
- Consumed by: Opportunity, Decision

### Dependency: Brand Expression Constraints
- Canonical Owner: Qenki-Frame
- Canonical Source: to be defined at integration
- Local Role: organism-wide expression constraint
- Contract Satisfied: Contract 05 — Brand Expression Constraint Contract
- Consumed by: Expression, Critic

## Single-Consumer Dependency (Not Organism-Wide)

### Dependency: Situational Facts
- Canonical Owner: external observing domain, to be defined at integration
- Local Role: input to Opportunity's World State synthesis
- Contract Satisfied: Contract 04 — Situational Awareness Contract
- Consumed by: Opportunity only
- Declared locally in ORGANS/OPPORTUNITY/, not in this document, since it
  is not an organism-wide dependency.

## Note on Synchronization Status
Live synchronization status (current/stale/unknown) for each dependency
declared above is tracked in HEALTH/, not in this document, since
freshness is a live operational state rather than a stable architectural
declaration.

## Relationships
Consulted alongside QENKI_MIND_COGNITIVE_CONTRACT_LAYER_v1.md, which
defines the semantic guarantees each declared dependency must satisfy.
