from .engine import CognitiveEngine, CognitiveOperator, CognitiveSession, EventBus, OperatorRunResult
from .registry import OperatorRegistry

from .LearningToMemory.operator import Operator as LearningToMemory
from .MemoryToReasoning.operator import Operator as MemoryToReasoning
from .OpportunityToDecision.operator import Operator as OpportunityToDecision
from .DecisionToExpression.operator import Operator as DecisionToExpression
from .ExpressionToConsequence.operator import Operator as ExpressionToConsequence
from .ConsequenceToLearning.operator import Operator as ConsequenceToLearning
from .LearningToBelief.operator import Operator as LearningToBelief

# Pre-built registry with all seven canonical operators registered.
# Pass this to CognitiveEngine(registry=default_registry) or use
# build_engine() to get a ready-to-run engine instance.
default_registry = OperatorRegistry()
default_registry.register("LearningToMemory",        LearningToMemory)
default_registry.register("MemoryToReasoning",       MemoryToReasoning)
default_registry.register("OpportunityToDecision",   OpportunityToDecision)
default_registry.register("DecisionToExpression",    DecisionToExpression)
default_registry.register("ExpressionToConsequence", ExpressionToConsequence)
default_registry.register("ConsequenceToLearning",   ConsequenceToLearning)
default_registry.register("LearningToBelief",        LearningToBelief)


def build_engine(event_bus=None):
    """
    Returns a CognitiveEngine pre-loaded with all seven canonical operators.

    Usage:
        from OPERATORS import build_engine
        engine = build_engine()
        session = engine.start_session(trigger="manual", root_entity="LEARNING/example.md")
        result  = engine.run_pipeline(
            entity="LEARNING/example.md",
            pipeline=[
                "LearningToMemory",
                "LearningToBelief",
            ],
            session=session,
        )
    """
    return CognitiveEngine(registry=default_registry, event_bus=event_bus)
