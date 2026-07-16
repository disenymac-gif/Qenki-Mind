# QENKI_MIND_ONTOLOGY_v1

## Purpose
Defines the canonical vocabulary of cognitive objects used by every organ
inside Qenki-Mind, and the transformation graph describing how one object
becomes another.

## Owner
Qenki-Mind (normative canonical document)

## Lifecycle
Stable. Changes only through architectural review; several object
transitions have been made normative through accepted Architectural
Decision Records (see Architectural Decisions Incorporated).

## Cognitive Objects

### Raw Signal
Unprocessed contact with the outside world. Created by the Sensory
System. Transient. Becomes Observation or is discarded.

### Observation
A noticed fragment tagged with salience and novelty. Created by the
Perception Organ. Becomes Evidence or a component of a Question.

**Cycle Membership Invariant (binding, from ADR-006):** An Observation
belongs to exactly one Sense-Making cycle's snapshot. Once a Sense-Making
cycle begins, its set of considered Observations is fixed and immutable
for the duration of that cycle. Observations arriving after the snapshot
moment are deferred, never injected into the active cycle, and remain
queued for a future cycle. No Observation may be silently discarded due to
cycle timing. Perception continues writing new Observations to the
Observation Inbox continuously, without interruption, regardless of
Sense-Making's cycle state.

### Question
An explicit gap in understanding. Created by the Sense-Making Organ.
Becomes Hypothesis or resolves directly into Insight.

### Evidence
An Observation formally linked to a claim it supports or challenges.
Created by the Sense-Making Organ. Permanent, immutable once created.

### Belief
A claim held with meaningful but not absolute confidence. Belief is a
first-class persistent epistemic entity stored in the persistent epistemic
layer owned by the Learning & Reflection Organ — not merely an implicit
view materialized from Memory, Evidence, Decision, or World State.

**Epistemic Layer Invariants (binding, from ADR-008):**
- Qenki-Mind maintains exactly one authoritative persistent epistemic layer
  for Beliefs and related lifecycle state.
- Learning & Reflection is the sole organ authorized to enact any change
  to a Belief's authoritative state: creation, confidence revision,
  promotion to Fact, regression from Fact, archival, and conflict
  resolution. Other organs may propose creation or revision; proposal and
  authority are permanently distinct.
- Every authoritative Belief state change must be traceable to supporting
  and/or contradicting Evidence, Learning, or Reflection inputs.
- A Belief may exist with incomplete Evidence, but its confidence and
  revision history must make that epistemic incompleteness explicit.
- Conflicting Beliefs may coexist transiently only if the conflict is
  explicitly represented and unresolved; no implementation may silently
  collapse conflict by deletion or overwrite.
- Belief archival never erases epistemic history; inactive or superseded
  Beliefs remain permanently retrievable.
- Decisions may consume the persistent epistemic layer but may not
  authoritatively mutate it.

A Belief becomes Fact (see Promotion Invariant below), Insight,
or is archived upon disconfirmation.

### Fact
A claim considered settled beyond reasonable doubt. Fact is a first-class
epistemic object residing inside the persistent epistemic layer; promotion
and regression occur inside that layer, not outside it.

**Promotion Invariant (binding, from ADR-001):** A Belief promotes to
Fact if and only if independently-sourced Evidence converges above a
confidence threshold owned and set by the Learning & Reflection Organ as a
tunable Reasoning Parameter. A Fact always represents strictly higher
epistemic commitment than a Belief; no implementation may allow a Fact to
carry equal or lower confidence than an unpromoted Belief. A Fact remains
reversible: it regresses to Belief upon the arrival of contradicting
Evidence, with the regression enacted inside the persistent epistemic layer
by Learning & Reflection (binding, from ADR-008, Invariant 7). Promotion
may never occur from volume alone, elapsed time, or absence of
disconfirmation — only from convergent, independent Evidence crossing the
owned threshold.

### Hypothesis
A proposed but untested explanation. Created by the Sense-Making Organ.
Becomes Belief (if supported) or is archived (if disconfirmed).

### Experiment
A deliberate, structured test of a Hypothesis. Created by Sense-Making,
approved by Opportunity, resolved by Learning & Reflection. Becomes
Learning.

### Mental Model
A reusable explanatory template abstracted from Insights.

**Lifecycle Authority Invariant (binding, from ADR-005):** Every Mental
Model has exactly one authoritative lifecycle owner: the Learning &
Reflection Organ, which alone holds authority to deprecate or reinstate a
Mental Model, based on accumulated performance across its applications.
Sense-Making, as the originating organ, may propose deprecation but may
never enact it; a proposal takes effect only once Learning & Reflection
acts on it. A Mental Model remains active until Learning & Reflection
explicitly changes its status. Deprecation never deletes a Mental Model;
every deprecated Mental Model remains permanently retrievable as part of
the organism's cognitive history.

### Insight
A causal explanation produced by applying a Mental Model to current
Knowledge. Created by the Sense-Making Organ.

**Handoff Invariant (binding, from ADR-002):** Sense-Making forwards
every Insight it forms to the Opportunity Organ by default. Sense-Making
may withhold an Insight only under two narrow, bounded exceptions:
insufficient confidence for meaningful evaluation, or explicit redundancy
with an Insight already pending evaluation. All other relevance and
timeliness judgment belongs exclusively to the Opportunity Organ. A
withheld Insight is never discarded; it remains permanently retrievable
through the organism's memory. Opportunity evaluates every Insight that
reaches it and is never required to reconstruct or rediscover Insights
withheld upstream.

### Objective
A current, time-bound aim set externally to Qenki-Mind. Referenced, not
owned, by Mind. Consumed by Opportunity and Decision.

### Opportunity
A framed, scored possibility for action. Created by the Opportunity
Organ. Becomes Decision (pursued) or archived (declined).

### Decision
A committed course of action. Created by the Decision Organ. Permanent
record once made. Becomes Expression or a recorded "not now."

### Expression
An externalized artifact translated from a Decision. Created by the
Expression Organ. Permanent record once released.

### Learning
An update produced by comparing a prediction against an actual outcome.
Created by the Learning & Reflection Organ. Learning is a first-class
cognitive object; it feeds Belief revision inside the persistent epistemic
layer (binding, from ADR-008) and may trigger promotion, regression, or
archival of Beliefs.

**Terminal State Invariant (binding, from ADR-004):** Every prediction
tied to a Decision or Expression must eventually reach a terminal state.
Pending is a transient state only. Confirmation, disconfirmation, and
"unresolved — no data received" are three distinct terminal outcomes.
Absence of Consequence data must never be interpreted as disconfirmation.
Every prediction carries a maximum waiting period, owned as a tunable
Reasoning Parameter by the Learning & Reflection Organ; a prediction
exceeding this period without data is permanently recorded as "unresolved
— no data received." Calibration rhythms never block waiting for
unresolved predictions.

### Reflection
A higher-order synthesis across many Learning events. Created by the
Learning & Reflection Organ at weekly, monthly, and quarterly rhythms.

### Principle
A distilled, durable operating rule. Proposed by Learning & Reflection,
ratified by a human.

### World State
The organism's current synthesized picture of the external environment.
Owned by the Opportunity Organ.

### Context
A moment-specific reasoning frame. Dissolves at the end of its cycle.

### Assumption
An unverified premise knowingly proceeded on. Becomes Belief, Question, or
is discarded.

## Architectural Decisions Incorporated
- ADR-001: Belief to Fact Promotion Invariant — Status: Closed
- ADR-002: Insight Handoff Authority — Status: Closed
- ADR-005: Mental Model Deprecation Authority — Status: Closed
- ADR-006: Observation Snapshot Semantics — Status: Closed
- ADR-008: Persistent Epistemic Layer — Status: Accepted and absorbed

## Relationships
Consumed by every organ. Consulted alongside QENKI_MIND_ORGANS_v1.md and
QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md.
