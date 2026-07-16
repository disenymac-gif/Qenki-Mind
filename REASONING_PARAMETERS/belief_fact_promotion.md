# Reasoning Parameter: Belief-to-Fact Promotion

## Identity
Name: Belief-to-Fact Promotion
Owning Organ: Learning & Reflection

## Canonical Basis
QENKI_MIND_ONTOLOGY_v1.md (Fact — Promotion Invariant)
QENKI_MIND_ORGANS_v1.md (Learning & Reflection Organ ownership boundary)
ADR-001 (Closed)

## Parameter Definition
Governs the confidence threshold and source-independence criteria that
determine when a Belief, supported by converging independently-sourced
Evidence, is promoted to a Fact.

## Current Value

### promotion_threshold
0.80

A Belief whose `Confidence` field meets or exceeds this value is
eligible for promotion to Fact by the `BeliefToFact` operator.
Calibration basis: conservative default chosen for first operational
activation (2026-07-16). A threshold of 0.80 requires strong convergent
Evidence before committing to Fact status, consistent with ADR-001's
requirement for independently-sourced, converging Evidence.

### minimum_independent_sources
1

Minimum number of distinct Evidence sources referenced in the Belief's
`Supporting Evidence` section for promotion to be valid. Initial value
of 1 is permissive; it records the invariant structurally while
acknowledging that the current system does not yet track Evidence source
independence in machine-readable form. Future calibration will raise
this value once Evidence provenance tracking is implemented.

### regression_threshold
0.50

A promoted Fact whose `Confidence` drops below this value is eligible
for regression to Belief by a future `BeliefRegression` operator.
Not yet operationally active (operator not yet implemented).

## Change History
- 2026-07-16: Initial calibration. `promotion_threshold` set to 0.80;
  `minimum_independent_sources` set to 1 (permissive initial value);
  `regression_threshold` set to 0.50 (not yet active). Enacted by
  implementation of `BeliefToFact` operator.

## Last Updated
2026-07-16
