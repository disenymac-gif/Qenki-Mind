# ADR 006: Observation Snapshot vs. Live Processing Semantics

## Status
Closed

## Context
Perception operates continuously throughout the day, populating the
Observation Inbox, while Sense-Making operates as a triggered activity,
firing once sufficient material has accumulated. Neither the Cognitive
Architecture nor the Ontology specified whether an Observation arriving
mid-Sense-Making-cycle is included in that cycle's interpretation or
deferred to the next one. This left open the possibility of live,
mid-cycle incorporation of new Observations, which would make a cycle's
conclusions dependent on the exact timing of its own execution, producing
outputs that could not be reliably traced to a fixed, reproducible input
set.

## Decision
Each Sense-Making cycle operates on a fixed snapshot of the Observation
Inbox taken at the moment the cycle is triggered. Observations arriving
after that moment are not included in the current cycle and remain queued
in the Inbox for the next triggered cycle. Perception continues populating
the Inbox continuously and without interruption, regardless of Sense-
Making's current cycle state.

## Architectural Invariants
1. Every Sense-Making cycle operates on a fixed snapshot of the
   Observation Inbox.
2. Every Insight is traceable to a finite, immutable set of Observations.
3. Observation membership within a Sense-Making cycle never changes once
   the cycle begins.
4. Observations arriving after the snapshot are deferred, never injected
   into the active cycle.
5. Deferred Observations remain queued until consumed by a future
   Sense-Making cycle.
6. Perception continues uninterrupted regardless of any active
   Sense-Making cycle.
7. No Observation may be silently discarded because of cycle timing.
8. Sense-Making outputs remain reproducible from their recorded inputs.

## Consequences
- QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md is clarified: the relationship
  between Perception's continuous activity and Sense-Making's triggered
  activity now has a defined boundary, guaranteeing deterministic,
  reproducible Sense-Making cycles.
- QENKI_MIND_ONTOLOGY_v1.md is clarified: the Observation object's
  transition into a Sense-Making cycle is now bound by a fixed-snapshot
  invariant rather than left ambiguous regarding live updates.
- ORGANS/PERCEPTION/ continues writing to the Observation Inbox without
  regard to Sense-Making's cycle state, preserving Perception's frozen
  status as a continuous activity.
- ORGANS/SENSE_MAKING/ operational records now reflect a fixed, traceable
  input set per cycle, enabling every Insight to be explained after the
  fact by reference to exactly what it considered.

## Affected Canonical Documents
- QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md (Perception and Sense-Making
  interaction boundary)
- QENKI_MIND_ONTOLOGY_v1.md (Observation object transformation rules)
