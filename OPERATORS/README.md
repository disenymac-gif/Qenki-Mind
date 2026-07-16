# Operators

Canonical cognitive operators for the Qenki-Mind pipeline.
All operators follow the `CognitiveOperator` interface defined in
`OPERATORS/engine.py`: `inputs()`, `validate()`, `execute()`,
`persist()`, `emit_events()`.

## Pipeline

```
Learning  -->  LearningToMemory       -->  MEMORY/
                                           |
               MemoryToReasoning      -->  REASONING/
                                           |
               OpportunityToDecision  -->  DECISIONS/
                                           |
               DecisionToExpression   -->  EXPRESSIONS/
                                           |
               ExpressionToConsequence -->  CONSEQUENCES/
                                           |
               ConsequenceToLearning  -->  LEARNING/
                                           |
               LearningToBelief       -->  BELIEFS/
                                           |
               BeliefToFact           -->  FACTS/           (promotion arc)
                                           |
               EvidenceToBeliefUpdate -->  BELIEFS/         (evidence arc)
                   |                            |
                   +-- sets Regression Pending  |
                                                v
               BeliefRegression       -->  FACTS/ (Regressed) + BELIEFS/ (Active)
                                           |
               BeliefArchival         -->  BELIEFS/ (Archived) [+ FACTS/ (Archived)]
```

## Operators

| # | Operator | Input domain | Output domain | Authority |
|---|---|---|---|---|
| 1 | `LearningToMemory` | `LEARNING/` | `MEMORY/` | Learning & Reflection Organ |
| 2 | `MemoryToReasoning` | `MEMORY/` | `REASONING/` | Learning & Reflection Organ |
| 3 | `OpportunityToDecision` | `REASONING/` | `DECISIONS/` | Decision Organ |
| 4 | `DecisionToExpression` | `DECISIONS/` | `EXPRESSIONS/` | Expression Organ |
| 5 | `ExpressionToConsequence` | `EXPRESSIONS/` | `CONSEQUENCES/` | Expression Organ |
| 6 | `ConsequenceToLearning` | `CONSEQUENCES/` | `LEARNING/` | Learning & Reflection Organ |
| 7 | `LearningToBelief` | `LEARNING/` | `BELIEFS/` | Learning & Reflection Organ |
| 8 | `BeliefToFact` | `BELIEFS/` | `FACTS/` | Learning & Reflection Organ |
| 9 | `EvidenceToBeliefUpdate` | `EPISTEMIC_EVIDENCE/` | `BELIEFS/` | Learning & Reflection Organ |
| 10 | `BeliefRegression` | `BELIEFS/` (Regression Pending) | `FACTS/` (Regressed) + `BELIEFS/` (Active) | Learning & Reflection Organ |
| 11 | `BeliefArchival` | `BELIEFS/` (any non-Archived) | `BELIEFS/` (Archived) [+ `FACTS/` (Archived)] | Learning & Reflection Organ |

## Epistemic Lifecycle (ADR-001 + ADR-008)

```
Learning  -[LearningToBelief]->   Belief (Active)
                                       |
                               [BeliefToFact]
                                       |
                                  Fact (Promoted)
                                       |
                      [EvidenceToBeliefUpdate: Contradicting]
                                       |
                           Belief (Regression Pending)
                                       |
                            [BeliefRegression]
                                       |
                    Fact (Regressed) + Belief (Active)
                                       |
                             [BeliefArchival]  (terminal)
                                       |
             Belief (Archived) [+ Fact (Archived)]  ✓

Accepted archival input states:
  Active | Promoted | Regressed | Regression Pending | Conflicted
```

The full Belief lifecycle is now implemented.
