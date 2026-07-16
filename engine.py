"""
engine.py  (root shim)

Thin re-export so that `from engine import CognitiveEngine` resolves
from the repository root, mirroring the canonical implementation at
OPERATORS/engine.py.

Do not add logic here. All implementation lives in OPERATORS/engine.py.
"""
from OPERATORS.engine import (  # noqa: F401
    CognitiveEngine,
    CognitiveOperator,
    CognitiveSession,
    EventBus,
    OperatorRunResult,
)
