# QENKI_MIND_COGNITIVE_ARCHITECTURE_v1

## Purpose
Defines the cognitive loop connecting the eight organs, and the natural
rhythms — continuous, scheduled, triggered, periodic, human-requested,
and human-review — that govern Qenki-Mind's daily and long-term operation.

## Owner
Qenki-Mind (normative canonical document)

## Lifecycle
Stable. The loop sequence and rhythms are frozen; boundary conditions
between adjacent stages have been made explicit through accepted
Architectural Decision Records.

## The Cognitive Loop
Perception (continuous) -> Sense-Making (triggered) -> Opportunity
(scheduled, daily) -> Decision (triggered) -> Expression (triggered,
optional) -> Learning & Reflection (continuous daily calibration; periodic
weekly/monthly/quarterly reflection).

**Epistemic feedback path (binding, from ADR-008):** Learning & Reflection
operates a persistent epistemic layer as a first-class component of the
cognitive loop. After each calibration cycle, Learning & Reflection may
enact Belief revisions inside this layer. These revisions are available to
all subsequent Sense-Making, Opportunity, and Decision cycles, enabling
learning to change future reasoning through Belief state — not only
through historical records. The epistemic feedback path is architecturally
distinct from Memory, Evidence, World State, and Consequence: it
represents the organism's current internal claims about what is believed to
be true beyond direct observation, with explicit confidence and revision
history. No organ other than Learning & Reflection may enact changes to
this layer.

## Perception to Sense-Making Boundary

**Binding invariant (from ADR-006):** Each Sense-Making cycle operates on
a fixed snapshot of the Observation Inbox taken at the moment the cycle is
triggered. Observation membership within a cycle never changes once the
cycle begins. Observations arriving after the snapshot are deferred, never
injected into the active cycle, and remain queued for a future cycle. No
Observation may be silently discarded due to cycle timing. Perception
continues writing to the Observation Inbox continuously and without
interruption, regardless of Sense-Making's current cycle state. This
guarantees every Insight is traceable to a finite, immutable set of
Observations, and that Sense-Making outputs remain reproducible from their
recorded inputs.

## Sense-Making to Opportunity Boundary

**Binding invariant (from ADR-002):** Sense-Making forwards every Insight
to Opportunity by default, withholding only for insufficient confidence or
explicit redundancy with an Insight already pending evaluation. Opportunity
holds exclusive authority over relevance and timeliness judgment for
everything it receives.

## Critic Checkpoints

**Binding invariant (from ADR-003):** The Critic Organ reviews artifacts
at three checkpoints in the loop: Insight formation, Decision commitment,
and Expression drafting. At each checkpoint, a rejection returns the
artifact to its producing organ for exactly one bounded revision attempt.
A second rejection at the same checkpoint results in permanent archival as
rejected-and-abandoned. This guarantees the loop terminates within a
bounded number of passes at every checkpoint, consistent with the daily
rhythm's same-day resolution expectations.

## Natural Rhythms

### Hourly
No structurally significant cognitive activity; Perception samples
passively without escalating to conscious attention.

### Daily
The full loop: listen, interpret, weigh, decide, express (if warranted),
calibrate, consolidate. Learning & Reflection may enact Belief revisions
inside the persistent epistemic layer after the daily calibration pass.

### Weekly
Learning & Reflection reviews patterns across the week's Decisions and
Learning events, including any predictions that reached terminal
"unresolved — no data received" status per the Consequence Contract
completion rule (ADR-004). Belief revision and conflict resolution in the
epistemic layer may be enacted at this rhythm.

### Monthly
Deeper reflection; proposed Mental Model or Decision Policy revisions
surface here, respecting the Mental Model deprecation authority boundary
(ADR-005). Epistemic layer audit: conflicting or stale Beliefs may be
explicitly resolved or archived by Learning & Reflection.

### Quarterly
Deepest review; proposed Philosophy or Objectives revisions, always
routed through Human Review, never self-applied.

## Architectural Decisions Incorporated
- ADR-002: Insight Handoff Authority — Status: Closed
- ADR-003: Critic Rejection Semantics — Status: Closed
- ADR-006: Observation Snapshot Semantics — Status: Closed
- ADR-008: Persistent Epistemic Layer — Status: Accepted and absorbed

## Relationships
Consulted alongside QENKI_MIND_ORGANS_v1.md and
QENKI_MIND_ONTOLOGY_v1.md.
