# Opportunity to Decision Operator

## Purpose
Transforms a structured Opportunity entity into a new Decision entity by evaluating the Opportunity against World State, Objectives, and relevant Memory.

## Responsible Organ
Decision Organ.

## Inputs
- Opportunity entity
- Relevant World State
- Relevant Objectives
- Relevant Memory

## Transformation Rules
1. Assess the Opportunity against current World State.
2. Check alignment with Objectives.
3. Retrieve relevant Memory that may support, constrain, or contradict the Opportunity.
4. Generate a new Decision entity when the Opportunity is selected.
5. Record rationale for selection.
6. Generate initial Hypotheses and Predictions for the Decision entity.
7. Link the Decision entity to the originating Opportunity entity.

## Outputs
- Decision entity
- Decision rationale
- Initial Hypotheses
- Initial Predictions
- Cross-links to Opportunity, World State, Objectives, and relevant Memory

## Invariants
- A Decision entity must not be created without an originating Opportunity entity.
- The operator must preserve traceability to the inputs used.
- The operator may create at most one Decision per evaluated Opportunity within a single execution.
- If the Opportunity is not selected, the operator must record a non-selection rationale.

## Traceability
Each execution should leave a machine-readable trace in the Decision entity's change history and links.
