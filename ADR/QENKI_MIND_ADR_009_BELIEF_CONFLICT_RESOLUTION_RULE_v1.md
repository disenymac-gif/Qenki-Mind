# ADR 009: Belief Conflict Resolution Rule

## Status
Closed

## Context
ADR-008 establishes the 'Conflicted' Belief state and Invariant 8, which
prohibits the promotion of a Conflicted Belief to Fact until conflict is
explicitly resolved. The `BeliefToFact` operator enforces this gate via
`ConflictedBeliefError`. However, neither ADR-008 nor any prior ADR
specifies how a Conflicted Belief is adjudicated: which organ resolves it,
by what algorithm, and with what outcome. Without a canonical decision on
the resolution rule, the 'Conflicted' state is a dead end — a Belief can
enter it but cannot exit it without violating or bypassing ADR-008
Invariant 8.

The conflict in question is always evidential: a Belief is in 'Conflicted'
state because it carries both Supporting and Contradicting Evidence, and
the resulting confidence signal is ambiguous or contested. The resolution
rule must therefore be evidence-grounded and must not introduce a new
subjective authority separate from the existing Evidence-to-Belief update
mechanism already established by ADR-008.

This ADR does not address semantic conflict between two distinct Belief
entities with incompatible claims. It governs only the resolution of a
single Belief entity whose own Evidence corpus is internally divided.

## Decision
A Conflicted Belief is resolved by re-evaluating its net confidence from
its entire corpus of Applied Evidence, without applying any new Evidence
or altering the Evidence entities themselves.

The resolution algorithm, owned by the Learning & Reflection Organ and
enacted by the `BeliefConflictResolution` operator, is:

1. Read all Applied Evidence entities linked in the Belief's Supporting
   Evidence and Conflicting Evidence sections.
2. Sum the strengths of all Supporting Evidence entries and subtract the
   sum of all Contradicting Evidence strengths to produce a net confidence
   value. Clamp the result to [0.0, 1.0].
3. Compare the net confidence against the canonical `promotion_threshold`
   held in `REASONING_PARAMETERS/belief_fact_promotion.md`.
4. Set Belief.Confidence to the net confidence value.
5. Transition Belief.Epistemic State to 'Active' in both outcomes:
   - If net confidence >= promotion_threshold: Belief is Active and
     immediately eligible for promotion via `BeliefToFact`.
   - If net confidence < promotion_threshold: Belief is Active at its
     revised confidence, eligible for further Evidence accumulation or
     Archival.
6. The operator never directly promotes the Belief to Fact; `BeliefToFact`
   remains the sole promotion gate, and `ConflictedBeliefError` remains
   the sole promotion guard.
7. Append a Change History entry to the Belief recording the resolution
   date, the net confidence, and the previous 'Conflicted' state.
8. Emit a `BeliefConflictResolved` event.

## Architectural Invariants
1. A Conflicted Belief exits the 'Conflicted' state exclusively through
   the `BeliefConflictResolution` operator, owned by Learning & Reflection.
2. Resolution is evidence-grounded: the net confidence is derived solely
   from the strengths of Applied Evidence entities already linked to the
   Belief. No additional Evidence is applied during resolution itself.
3. Resolution always transitions the Belief to 'Active', never to any
   other state. The operator is not a promotion gate.
4. `BeliefToFact` and its `ConflictedBeliefError` guard remain the sole
   mechanism for blocking promotion of a Conflicted Belief. Resolution
   via this ADR re-enables eligibility only by transitioning to 'Active'.
5. The resolution algorithm is deterministic: given the same Evidence
   corpus and threshold, the operator always produces the same outcome.
6. Evidence entities are not mutated during conflict resolution. Their
   'Applied' state is read-only within this operator.

## Consequences
- QENKI_MIND_ONTOLOGY_v1.md: Belief section requires a Conflict
  Resolution Invariant binding this decision.
- QENKI_MIND_ORGANS_v1.md: Learning & Reflection ownership boundary
  requires extension to reference ADR-009 conflict resolution authority.
- `BeliefConflictResolution` operator: implementable directly against
  ADR-001 + ADR-008 + ADR-009 with no further canonical decisions required.
- The full Belief lifecycle is now complete: Active -> Promoted ->
  Regressed -> Conflicted -> Active (resolved) -> Archived.

## Affected Canonical Documents
- QENKI_MIND_ONTOLOGY_v1.md (Belief section: Conflict Resolution Invariant)
- QENKI_MIND_ORGANS_v1.md (Learning & Reflection: conflict resolution
  authority boundary)

## Absorption Record
- QENKI_MIND_ONTOLOGY_v1.md: absorbed 2026-07-16
- QENKI_MIND_ORGANS_v1.md: absorbed 2026-07-16
- BeliefConflictResolution operator implemented and test-covered: 2026-07-16

## Relationships
Depends on ADR-001 (Belief-to-Fact promotion threshold and independence
criteria), ADR-008 (Conflicted state definition, Invariant 8, and
Learning & Reflection ownership of the epistemic layer). Supersedes no
prior ADR. Is superseded by no subsequent ADR.
