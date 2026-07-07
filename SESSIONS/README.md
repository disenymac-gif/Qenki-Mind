# Cognitive Sessions

## Purpose
A Cognitive Session is the first-class execution envelope for a complete Qenki-Mind run. It groups the root trigger, the root entity, all snapshots, operators executed, events emitted, artifacts created, and the final state of the run.

## Ownership
Owned operationally by the Engine runtime. The engine creates and closes sessions; operators enrich the session through emitted events and created artifacts.

## Session Structure
- Session ID
- Trigger
- Root Entity
- World State Snapshot
- Objectives Snapshot
- Loaded Memory
- Operators Executed
- Events Emitted
- Artifacts Created
- Start Time
- End Time
- Final State

## Lifecycle
A session begins when the engine receives a trigger entity and ends when the pipeline terminates. Sessions are operational records, not canonical architecture.
