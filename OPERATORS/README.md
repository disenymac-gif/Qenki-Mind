# OPERATORS

This directory contains the six canonical cognitive operators that
implement Qenki-Mind's processing pipeline, plus the engine
infrastructure that orchestrates them.

## Pipeline

LEARNING → LearningToMemory → MEMORY
MEMORY → MemoryToReasoning → REASONING_PARAMETERS (+ session.memory_loaded)
EVIDENCE → OpportunityToDecision → DECISIONS
DECISIONS → DecisionToExpression → EXPRESSIONS
EXPRESSIONS → ExpressionToConsequence → EVENTS / WORLD_STATE
EVENTS → ConsequenceToLearning → LEARNING

## Quick start

```python
from OPERATORS import build_engine

engine  = build_engine()
session = engine.start_session(trigger="manual", root_entity="LEARNING/my-entity.md")

# Run a single operator
artifact = engine.run("LearningToMemory", "LEARNING/my-entity.md", session=session)

# Run a full pipeline
result = engine.run_pipeline(
    entity="LEARNING/my-entity.md",
    pipeline=[
        "LearningToMemory",
        "MemoryToReasoning",
    ],
    session=session,
)
```

## Operators

| Name | Input | Output | Persists to |
|---|---|---|---|
| `LearningToMemory` | `LEARNING/*.md` path | `MEMORY/*.md` path | `MEMORY/` |
| `MemoryToReasoning` | `MEMORY/*.md` path | `REASONING_PARAMETERS/*.md` path | `REASONING_PARAMETERS/` + `session.memory_loaded` |
| `OpportunityToDecision` | `EVIDENCE/*.md` path | `DECISIONS/*.md` path | `DECISIONS/` |
| `DecisionToExpression` | `DECISIONS/*.md` path | `EXPRESSIONS/*.md` path | `EXPRESSIONS/` |
| `ExpressionToConsequence` | `EXPRESSIONS/*.md` path | Event record | `EVENTS/` |
| `ConsequenceToLearning` | Event record path | `LEARNING/*.md` path | `LEARNING/` |

## Infrastructure

| File | Purpose |
|---|---|
| `engine.py` | `CognitiveEngine`, `CognitiveSession`, `CognitiveOperator`, `EventBus`, `OperatorRunResult` |
| `registry.py` | `OperatorRegistry` — key/class store |
| `__init__.py` | `default_registry` (all 6 operators pre-registered), `build_engine()` factory |

## Adding an operator

1. Create `OPERATORS/<Name>/operator.py` with `class Operator(CognitiveOperator)`.
2. Add `from .<Name>.operator import Operator as <Name>` to `__init__.py`.
3. Call `default_registry.register("<Name>", <Name>)` in `__init__.py`.