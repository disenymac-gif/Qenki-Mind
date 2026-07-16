# OPERATORS

This directory contains the nine canonical cognitive operators that
implement Qenki-Mind's processing pipeline, plus the engine
infrastructure that orchestrates them.

## Pipeline

```
LEARNING  -> LearningToMemory       -> MEMORY
MEMORY    -> MemoryToReasoning      -> REASONING_PARAMETERS (+ session.memory_loaded)
LEARNING  -> LearningToBelief       -> BELIEFS
EPISTEMIC_EVIDENCE -> EvidenceToBeliefUpdate -> BELIEFS (confidence updated)
BELIEFS   -> BeliefToFact           -> FACTS (+ BELIEFS updated to Promoted)
EVIDENCE  -> OpportunityToDecision  -> DECISIONS
DECISIONS -> DecisionToExpression   -> EXPRESSIONS
EXPRESSIONS -> ExpressionToConsequence -> EVENTS / WORLD_STATE
EVENTS    -> ConsequenceToLearning  -> LEARNING
```

## Quick start

```python
from OPERATORS import build_engine

engine  = build_engine()
session = engine.start_session(trigger="manual", root_entity="BELIEFS/my-belief.md")

# Route new Evidence into a Belief (updates confidence)
artifact = engine.run("EvidenceToBeliefUpdate",
                      "EPISTEMIC_EVIDENCE/evidence-x.md", session=session)

# Promote a Belief to Fact (requires confidence >= 0.80)
fact = engine.run("BeliefToFact", "BELIEFS/my-belief.md", session=session)
```

## Operators

| Name | Input | Output | Persists to | Authority |
|---|---|---|---|---|
| `LearningToMemory` | `LEARNING/*.md` | `MEMORY/*.md` | `MEMORY/` | Memory Organ |
| `MemoryToReasoning` | `MEMORY/*.md` | `REASONING_PARAMETERS/*.md` | `REASONING_PARAMETERS/` + session | Memory Organ |
| `LearningToBelief` | `LEARNING/*.md` | `BELIEFS/*.md` | `BELIEFS/` | Learning & Reflection Organ |
| `EvidenceToBeliefUpdate` | `EPISTEMIC_EVIDENCE/*.md` | updated `BELIEFS/*.md` | `BELIEFS/` + `EPISTEMIC_EVIDENCE/` | Learning & Reflection Organ |
| `BeliefToFact` | `BELIEFS/*.md` | `FACTS/*.md` | `FACTS/` + `BELIEFS/` (state update) | Learning & Reflection Organ |
| `OpportunityToDecision` | `EVIDENCE/*.md` | `DECISIONS/*.md` | `DECISIONS/` | Decision Organ |
| `DecisionToExpression` | `DECISIONS/*.md` | `EXPRESSIONS/*.md` | `EXPRESSIONS/` | Expression Organ |
| `ExpressionToConsequence` | `EXPRESSIONS/*.md` | Event record | `EVENTS/` | Learning & Reflection Organ |
| `ConsequenceToLearning` | Event record path | `LEARNING/*.md` | `LEARNING/` | Learning & Reflection Organ |

## Infrastructure

| File | Purpose |
|---|---|
| `engine.py` | `CognitiveEngine`, `CognitiveSession`, `CognitiveOperator`, `EventBus`, `OperatorRunResult` |
| `registry.py` | `OperatorRegistry` — key/class store |
| `__init__.py` | `default_registry` (all 9 operators pre-registered), `build_engine()` factory |

## Adding an operator

1. Create `OPERATORS/<Name>/operator.py` with `class Operator(CognitiveOperator)`.
2. Add `from .<Name>.operator import Operator as <Name>` to `__init__.py`.
3. Call `default_registry.register("<Name>", <Name>)` in `__init__.py`.
