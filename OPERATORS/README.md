# Operators Runtime

## Purpose
Provides the cognitive runtime that executes operators as plugins inside a common engine.

## Components
- registry.py: operator registration and lookup
- engine.py: CognitiveEngine, CognitiveOperator interface, EventBus
- plugin operator directories: one per cognitive transformation

## Execution Model
- engine.run(operator, entity): execute a single operator by name
- engine.run_pipeline(entity, pipeline): execute a sequence of operators

## Operator Interface
Every operator implements:
- inputs()
- validate()
- execute()
- persist()
- emit_events()

## Event Bus
Operators emit events after execution so the system can react to state changes.

## Invariants
- The engine must not need to know operator-specific logic.
- Operators must be registered before execution.
- Every execution must be traceable through emitted events.
