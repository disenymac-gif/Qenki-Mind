# Reasoners

## Purpose
Reasoners provide reusable cognitive subcomponents used by operators to transform entities autonomously. Operators orchestrate; reasoners produce ranked evidence, hypotheses, confidence estimates, and selections.

## Components
- base_reasoner.py
- evidence_ranker.py
- hypothesis_generator.py
- confidence_estimator.py
- decision_selector.py

## Invariants
- Operators should not embed decision intelligence directly when a reusable reasoner exists.
- Reasoner outputs must be traceable and persistable through operator-owned entities.
