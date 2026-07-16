"""Operator registry for Qenki-Mind cognitive pipeline.

All ten canonical operators are imported here so that
``from OPERATORS import <Name>`` resolves correctly and the
OperatorRegistry in engine.py can discover them by name.
"""
from OPERATORS.LearningToMemory.operator import Operator as LearningToMemory
from OPERATORS.MemoryToReasoning.operator import Operator as MemoryToReasoning
from OPERATORS.OpportunityToDecision.operator import Operator as OpportunityToDecision
from OPERATORS.DecisionToExpression.operator import Operator as DecisionToExpression
from OPERATORS.ExpressionToConsequence.operator import Operator as ExpressionToConsequence
from OPERATORS.ConsequenceToLearning.operator import Operator as ConsequenceToLearning
from OPERATORS.LearningToBelief.operator import Operator as LearningToBelief
from OPERATORS.BeliefToFact.operator import Operator as BeliefToFact
from OPERATORS.EvidenceToBeliefUpdate.operator import Operator as EvidenceToBeliefUpdate
from OPERATORS.BeliefRegression.operator import Operator as BeliefRegression

__all__ = [
    "LearningToMemory",
    "MemoryToReasoning",
    "OpportunityToDecision",
    "DecisionToExpression",
    "ExpressionToConsequence",
    "ConsequenceToLearning",
    "LearningToBelief",
    "BeliefToFact",
    "EvidenceToBeliefUpdate",
    "BeliefRegression",
]
