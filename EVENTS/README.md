# Typed Events

## Purpose
Defines stable event schemas emitted by the cognitive runtime. Typed events are the communication layer between operators and the session envelope.

## Event Shape
- event_id
- timestamp
- operator
- source_entity
- target_entity
- payload

## Example Events
- DecisionCreated
- DecisionRejected
- ExpressionPublished
- PredictionConfirmed
- PredictionDisconfirmed
- LearningCreated
- MemoryUpdated
- ReasoningInvalidated

## Lifecycle
Events are emitted by operators and captured by the Event Bus during a Cognitive Session.
