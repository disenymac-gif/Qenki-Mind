# Decision Repository

## Purpose
Decision entities live here as first-class persistent knowledge objects. Each entity is maintained in its own file, with global views used only as indexes or summaries.

## Ownership
Owned by the appropriate organ per the canonical architecture. Only that organ may write the authoritative entity file.

## Entity-First Rule
- One file per decision entity is the preferred source of truth.
- Global logs, when present, are secondary views and must not be treated as the source of truth.
- Each entity may include context, hypotheses, predictions, consequences, learning, world-state links, memory links, and cross-entity links.

## Minimal Entity Structure
- Identity
- Ownership
- Canonical Basis
- Context
- Hypotheses
- Predictions
- Consequences
- Learning
- Links
- Current State
- Change History
- Last Updated

## Lifecycle
This repository evolves as new entities are created and enriched. The repository is operational, not canonical architecture.

## Prediction Representation Convention
Predictions may optionally use the form `- [id] statement (state: pending|confirmed|disconfirmed)` to enable machine resolution by operators such as ExpressionToConsequence. Plain text bullets remain valid and are treated as non-machine-resolvable.

## Prediction Representation Convention
Predictions may optionally use the form `- [id] statement (state: pending|confirmed|disconfirmed)` to enable machine resolution by operators such as ExpressionToConsequence. Plain text bullets remain valid and are treated as non-machine-resolvable.
