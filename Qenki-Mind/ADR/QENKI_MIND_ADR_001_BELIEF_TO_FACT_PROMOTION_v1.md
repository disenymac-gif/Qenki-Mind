# ADR 001: Belief to Fact Promotion Invariant

## Status
Closed

## Context
The canonical Ontology defines Belief and Fact as distinct cognitive objects,
with Fact representing settled epistemic commitment and Belief representing
a revisable, confidence-scored claim. The Ontology stated that Belief
promotes to Fact when "Evidence accumulates to a threshold of consistency
and volume," without specifying what constitutes sufficient consistency,
what constitutes sufficient volume, or which organ holds authority over
this determination. This left the promotion boundary architecturally
undefined, permitting materially different implementations to classify
identical accumulated Evidence differently, with direct downstream effects
on Decision confidence and Expression phrasing.

## Decision
Belief promotes to Fact if and only if independently-sourced Evidence
converges above a confidence threshold owned and set by the Learning &
Reflection Organ. The specific threshold value and the criteria for
evaluating source independence are Reasoning Parameters, not fixed
architectural constants, and remain tunable over time.

## Architectural Invariants
1. Fact represents a strictly higher epistemic commitment than Belief. No
   implementation may allow a Fact to carry equal or lower confidence than
   an unpromoted Belief.
2. Promotion is driven exclusively by accumulated independent Evidence,
   never by elapsed time, organ preference, or absence of disconfirmation
   alone.
3. Promotion is gated by a confidence threshold; no implicit or thresholdless
   promotion path may exist.
4. The threshold itself is not architectural. It is a tunable Reasoning
   Parameter, adjustable without requiring architectural review.
5. The Learning & Reflection Organ is the sole owner of this parameter. No
   other organ may independently set or override it.
6. Fact remains reversible. Any Fact must regress to Belief upon the arrival
   of contradicting Evidence; no implementation may treat Fact status as
   permanently locked once granted.

## Consequences
- QENKI_MIND_ONTOLOGY_v1.md is clarified by this ADR: the Belief-to-Fact
  transition is now bound by the invariants above rather than left as an
  unspecified threshold.
- QENKI_MIND_ORGANS_v1.md is clarified by this ADR: the Learning &
  Reflection Organ's ownership scope explicitly includes the Belief-to-Fact
  promotion threshold as a Reasoning Parameter it owns.
- REASONING_PARAMETERS/ becomes the canonical home for the specific
  threshold value and independence criteria referenced by this ADR. These
  values may evolve continuously without requiring a new ADR, provided they
  do not violate the invariants above.
- Any future implementation must reject promotion paths based purely on
  volume without independence, or purely on elapsed time without evidence.

## Affected Canonical Documents
- QENKI_MIND_ONTOLOGY_v1.md (Belief, Fact object definitions)
- QENKI_MIND_ORGANS_v1.md (Learning & Reflection Organ ownership scope)
- REASONING_PARAMETERS/ (tunable threshold and independence criteria)

## Relationships
Supersedes no prior ADR. No other ADR currently depends on this one.
