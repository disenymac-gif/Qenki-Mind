# ADR 003: Critic Rejection Semantics

## Status
Closed

## Context
The Critic Organ reviews Insights, Decisions, and Expressions at defined
checkpoints, but no canonical document specified what happens to an
artifact the Critic rejects. This left ambiguous whether rejection meant
permanent discard, unbounded revision, or something else, permitting
materially different implementations of the organism's capacity for
self-correction versus abandonment.

## Decision
A Critic rejection returns the artifact, with an explicit stated reason, to
the organ that produced it, for exactly one bounded revision attempt at
that checkpoint. A second rejection at the same checkpoint results in
permanent, retrievable archival as rejected-and-abandoned rather than
further resubmission.

## Architectural Invariants
1. A Critic rejection never results in silent loss.
2. Every rejection includes an explicit reason.
3. A rejected artifact always returns to the organ that produced it.
4. Every checkpoint permits exactly one revision attempt.
5. A second rejection at the same checkpoint permanently terminates that
   revision path.
6. Rejected artifacts remain permanently retrievable.
7. Every rejection, revision and final disposition is permanently recorded.
8. No artifact may bypass the Critic at any defined checkpoint.

## Consequences
- QENKI_MIND_ORGANS_v1.md is clarified: the Critic Organ's checkpoint
  function now has a defined outcome space (approve, reject-with-revision,
  reject-and-abandon) rather than an unspecified rejection behavior.
- QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md is clarified: the daily loop's
  Critic checkpoints (at Insight, Decision, and Expression stages) are
  guaranteed to terminate within a bounded number of passes, preserving
  the loop's same-day resolution expectations.
- ORGANS/CRITIC/ becomes the canonical location where every rejection,
  revision attempt, and final disposition is permanently recorded, per
  the Critic Organ's existing critique-log responsibility.
- No further architectural ambiguity remains regarding whether rejected
  work is discarded, looped indefinitely, or preserved; all three
  possibilities are now resolved in favor of bounded revision with
  permanent retrievable archival on final rejection.

## Affected Canonical Documents
- QENKI_MIND_ORGANS_v1.md (Critic Organ checkpoint outcomes)
- QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md (loop termination guarantee at
  Critic checkpoints)
