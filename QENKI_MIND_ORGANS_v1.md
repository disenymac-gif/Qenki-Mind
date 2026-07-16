# QENKI_MIND_ORGANS_v1

## Purpose
Defines the mission, faculties, and authority boundaries of each of the
eight cognitive organs of Qenki-Mind.

## Owner
Qenki-Mind (normative canonical document)

## Lifecycle
Stable. Organ missions are frozen; authority boundaries between organs
have been made explicit through accepted Architectural Decision Records.

## Organs

### Perception Organ
Mission: continuously notice the external world and populate the
Observation Inbox. Operates as a continuous activity, uninterrupted by
any other organ's cycle state (binding, from ADR-006).

### Memory Organ
Mission: consolidate Semantic, Episodic, and Pattern knowledge into
permanent, retrievable form. Owns the Memory Repository.

### Sense-Making Organ
Mission: explain — form Evidence, Beliefs, Hypotheses, Insights, and
propose Mental Models, by applying explanatory frameworks to Observations.

**Authority boundary (binding, from ADR-002):** Sense-Making's default
behavior is to forward every Insight it forms to Opportunity. It may
withhold an Insight only for insufficient confidence or explicit
redundancy with an Insight already pending evaluation — no broader
relevance judgment belongs to Sense-Making. Sense-Making's role is
explanatory, not evaluative; relevance and timeliness authority belong
exclusively to Opportunity.

**Authority boundary (binding, from ADR-005):** Sense-Making may propose
deprecation of a Mental Model it originated, based on observed application
difficulties, but holds no authority to enact deprecation. A proposal only
takes effect once the Learning & Reflection Organ acts on it.

**Cycle boundary (binding, from ADR-006):** Each Sense-Making cycle
operates on a fixed snapshot of the Observation Inbox taken at the moment
the cycle is triggered. Observations arriving after that moment are
deferred to the next cycle.

**Epistemic proposal boundary (binding, from ADR-008):** Sense-Making may
produce Beliefs as new epistemic objects, but creation of a Belief's
authoritative entry in the persistent epistemic layer requires Learning &
Reflection to enact it. Sense-Making’s formed Beliefs are proposals until
acted upon by the owning organ.

### Opportunity Organ
Mission: score Insights against World State and Objectives to produce
ranked Opportunities.

**Authority boundary (binding, from ADR-002):** Opportunity is the sole
organ with authority to determine opportunity relevance. It evaluates
every Insight that reaches it and is never required to reconstruct or
rediscover Insights withheld upstream by Sense-Making.

**Epistemic consumption boundary (binding, from ADR-008):** Opportunity
may consume Beliefs from the persistent epistemic layer to inform
opportunity scoring, but may not authoritatively mutate the epistemic
layer. Opportunity may propose Belief creation or revision as a side
effect of its evaluation, but such proposals take effect only once
Learning & Reflection acts on them.

### Decision Organ
Mission: resolve ranked Opportunities into committed Decisions, checked
against the Constitution and Decision Policies.

**Epistemic consumption boundary (binding, from ADR-008):** Decision may
consume Beliefs from the persistent epistemic layer to inform committed
Decisions, but may not authoritatively mutate the epistemic layer.

### Expression Organ
Mission: translate committed Decisions into externalized artifacts,
checked against Brand Expression Constraints.

### Critic Organ
Mission: review Insights, Decisions, and Expressions at defined
checkpoints before they proceed to the next stage.

**Rejection semantics (binding, from ADR-003):** A Critic rejection
returns the artifact, with an explicit stated reason, to the organ that
produced it, for exactly one bounded revision attempt at that checkpoint.
A second rejection at the same checkpoint results in permanent, retrievable
archival as rejected-and-abandoned. No artifact may bypass the Critic at
any defined checkpoint. Every rejection, revision, and final disposition
is permanently recorded in the Critic's critique log. Rejection never
results in silent loss.

### Learning & Reflection Organ
Mission: compare predictions against outcomes, recalibrate confidence,
revise Beliefs in the persistent epistemic layer, and produce periodic
Reflection at weekly, monthly, and quarterly rhythms.

**Ownership boundary (binding, from ADR-001):** Learning & Reflection is
the sole owner of the Belief-to-Fact promotion confidence threshold and
independence criteria, held as tunable Reasoning Parameters.

**Ownership boundary (binding, from ADR-004):** Learning & Reflection is
the sole owner of the maximum waiting period for Consequence data,
held as a tunable Reasoning Parameter. It ensures every prediction reaches
a terminal state — confirmed, disconfirmed, or unresolved due to missing
data — and never blocks its periodic rhythms waiting for outstanding
predictions.

**Ownership boundary (binding, from ADR-005):** Learning & Reflection is
the sole authority permitted to deprecate or reinstate a Mental Model,
based on accumulated performance. This authority may not be exercised by
any other organ.

**Epistemic layer ownership (binding, from ADR-008):** Learning &
Reflection is the sole organ authorized to enact any change to a Belief's
authoritative state in the persistent epistemic layer: creation, confidence
revision, promotion to Fact, regression from Fact to Belief, archival, and
conflict resolution. Other organs may consume Beliefs and may propose
creation or revision through their own artifacts; such proposals take effect
only once Learning & Reflection acts on them. Proposal and authority are
permanently distinct. This ownership is not bounded by any specific
persistence substrate; it applies regardless of whether the layer is
materialized as a repository directory, a datastore, or another form.

## Architectural Decisions Incorporated
- ADR-001: Belief to Fact Promotion Invariant — Status: Closed
- ADR-002: Insight Handoff Authority — Status: Closed
- ADR-003: Critic Rejection Semantics — Status: Closed
- ADR-004: Consequence Contract Completion Semantics — Status: Closed
- ADR-005: Mental Model Deprecation Authority — Status: Closed
- ADR-008: Persistent Epistemic Layer — Status: Accepted and absorbed

## Relationships
Consulted alongside QENKI_MIND_ONTOLOGY_v1.md and
QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md.
