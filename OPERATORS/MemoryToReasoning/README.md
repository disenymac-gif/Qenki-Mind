# Operator: Memory → Reasoning

## Purpose
Projects epistemic content from a persisted Memory entity into the active
CognitiveSession, making it available to downstream operators as
`session.memory_loaded`. Simultaneously persists a dated reasoning-context
snapshot in `REASONING_PARAMETERS/` for traceability.

## Owned By
Memory Organ. Consumed read-only by downstream operators.
Mutable only by Learning & Reflection, per ADR-008 invariant 3.

## Inputs
- `entity` — path to a Memory entity file (`MEMORY/*.md`), produced by
  the `LearningToMemory` operator.

## Output Artifact
`REASONING_PARAMETERS/reasoning-context-<memory-stem>.md`

A reasoning-context snapshot structured per the `REASONING_PARAMETERS/`
domain contract (Identity, Ownership, Canonical Basis, projected epistemic
fields, Links, Change History, Last Updated).

## Session Side Effect
If a `CognitiveSession` is active, `session.memory_loaded` is populated
with the projected Learning items extracted from the Memory entity. Items
already present in `session.memory_loaded` are not duplicated (dedup by
value). This makes Memory content available to `EvidenceRanker` in
`OpportunityToDecision` without any additional wiring.

## Validation Contract
- Memory entity must exist at the given path.
- Sections `Identity` and `Learning` must be present.
- `Learning` must contain usable content (not empty, not the canonical
  empty-state strings). Raises `NoUsableLearningError` otherwise — the
  operator does not silently produce an empty reasoning context.

## Pipeline Position

```
LearningToMemory → [MEMORY/*.md] → MemoryToReasoning → [REASONING_PARAMETERS/reasoning-context-*.md]
                                                       ↓ session.memory_loaded
                                          OpportunityToDecision → EvidenceRanker
```

## Events Emitted
`MemoryProjected` — carries `projected_items_count` and `session_id`.

## Architectural Notes
- Traceability per ADR-008 invariant 5: every projection is persisted as a
  dated snapshot with full provenance (`Canonical Basis`, `Change History`).
- ADR-008 status is `Proposed`; this operator pre-materializes the
  Memory→Reasoning pathway without creating a `BELIEFS/` domain, which
  requires accepted ADR-008 before it can exist in topology.
- The snapshot’s `Current State: Active` means it is the current operative
  context for the session that produced it. Multiple snapshots may coexist
  in `REASONING_PARAMETERS/` — one per Memory source, timestamped in
  `Change History`.
