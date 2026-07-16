from .engine import CognitiveEngine, CognitiveOperator, CognitiveSession, EventBus, OperatorRunResult
from .registry import OperatorRegistry

from .LearningToMemory.operator import Operator as LearningToMemory
from .MemoryToReasoning.operator import Operator as MemoryToReasoning
from .OpportunityToDecision.operator import Operator as OpportunityToDecision
from .DecisionToExpression.operator import Operator as DecisionToExpression
from .ExpressionToConsequence.operator import Operator as ExpressionToConsequence
from .ConsequenceToLearning.operator import Operator as ConsequenceToLearning
from .LearningToBelief.operator import Operator as LearningToBelief
from .BeliefToFact.operator import Operator as BeliefToFact
from .EvidenceToBeliefUpdate.operator import Operator as EvidenceToBeliefUpdate

# Pre-built registry with all nine canonical operators registered.
default_registry = OperatorRegistry()
default_registry.register("LearningToMemory",        LearningToMemory)
default_registry.register("MemoryToReasoning",       MemoryToReasoning)
default_registry.register("OpportunityToDecision",   OpportunityToDecision)
default_registry.register("DecisionToExpression",    DecisionToExpression)
default_registry.register("ExpressionToConsequence", ExpressionToConsequence)
default_registry.register("ConsequenceToLearning",   ConsequenceToLearning)
default_registry.register("LearningToBelief",        LearningToBelief)
default_registry.register("BeliefToFact",            BeliefToFact)
default_registry.register("EvidenceToBeliefUpdate",  EvidenceToBeliefUpdate)


def build_engine(event_bus=None):
    """
    Returns a CognitiveEngine pre-loaded with all nine canonical operators.

    Usage:
        from OPERATORS import build_engine
        engine = build_engine()
        session = engine.start_session(trigger="manual", root_entity="BELIEFS/belief-x.md")
        artifact = engine.run(
            "EvidenceToBeliefUpdate",
            "EPISTEMIC_EVIDENCE/evidence-x.md",
            session=session,
        )
    """
    return CognitiveEngine(registry=default_registry, event_bus=event_bus)
