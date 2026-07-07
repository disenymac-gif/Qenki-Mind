# ADR 004: Consequence Contract Completion Semantics

## Status
Closed

## Context
Contract 07, the Consequence Contract, promised "eventual arrival" of
outcome data without bounding what "eventual" means. This left the
contract's own guarantee unverifiable by any implementation: one system
could wait indefinitely for outcome data, while another could time out,
producing materially different observable calibration behavior in the
Learning & Reflection Organ. The gap was in the contract's semantics
itself, not in a private implementation choice beneath a complete promise.

## Decision
Every prediction tied to a Decision or Expression carries a maximum
waiting period for Consequence data, owned and set by the Learning &
Reflection Organ as a tunable Reasoning Parameter. A prediction exceeding
this period without data arriving is permanently recorded as "unresolved —
no data received," a terminal state distinct from both confirmation and
disconfirmation.

## Architectural Invariants
1. Every prediction must eventually reach a terminal state.
2. Pending is a transient state only.
3. Confirmation, disconfirmation, and unresolved due to missing data are
   three distinct terminal outcomes.
4. Absence of Consequence data must never be interpreted as
   disconfirmation.
5. Calibration rhythms never block waiting for unresolved predictions.
6. Every prediction carries a maximum waiting period.
7. That waiting period is a tunable Reasoning Parameter owned by the
   Learning & Reflection Organ.
8. Resolution due to timeout permanently preserves the prediction's
   historical record.

## Consequences
- QENKI_MIND_COGNITIVE_CONTRACT_LAYER_v1.md is clarified: Contract 07's
  guarantee of "eventual arrival" is now a complete, checkable promise,
  bounded by a Reasoning Parameter rather than left open-ended.
- QENKI_MIND_ORGANS_v1.md is clarified: the Learning & Reflection Organ's
  ownership scope explicitly includes the maximum waiting period as a
  Reasoning Parameter it owns and tunes.
- REASONING_PARAMETERS/ becomes the canonical home for the specific waiting
  period value, which may evolve continuously without requiring a new ADR,
  provided it does not violate the invariants above.
- DECISIONS/ and EXPRESSIONS/ permanently retain the historical record of
  every prediction's terminal resolution, including those resolved by
  timeout, ensuring no distinction between missing and negative evidence is
  ever lost.

## Affected Canonical Documents
- QENKI_MIND_COGNITIVE_CONTRACT_LAYER_v1.md (Contract 07 completion)
- QENKI_MIND_ORGANS_v1.md (Learning & Reflection Organ ownership scope)
- REASONING_PARAMETERS/ (maximum waiting period value)
