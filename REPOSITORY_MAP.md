# Qenki-Mind Repository Map

## Purpose
This is a living operational document describing the current structure of
the Qenki-Mind repository. It is not canonical architecture and requires
no architectural review to update. It describes categories of content, not
individual filenames or their current status — the repository itself is
the authoritative inventory of what exists. Future topology is defined by
the canonical architecture, not by this document.

## Canonical Documents
Root-level canonical architecture documents (see repository root), governed
by `QENKI_MIND_GOVERNANCE_RULES_v1.md`.

## Meta-Model Contract
`META_MODEL.md` defines the architectural laws governing how the meta-model evolves.

## Primitive Vocabulary
`PRIMITIVE_VOCABULARY.md` defines the universal language primitives.

## Domain Vocabulary
`VOCABULARY.md` defines Qenki-specific domain concepts built from primitive vocabulary.

## Model Schema
`MODEL_SCHEMA.md` defines semantic models that operate on the shared domain vocabulary.

## Model Registry
`MODEL_REGISTRY.md` maps model names to domain vocabulary terms without semantic logic.

## Artifact Profiles
`ARTIFACT_PROFILE_REGISTRY.md` defines reusable model-composition profiles for artifact types.

## Artifact Type Registry
`ARTIFACT_TYPE_REGISTRY.md` maps artifact types to artifact profiles.

## ADR History
`ADR/` contains the repository's Architectural Decision Records.
`ADR/absorption-backups/` contains historical snapshots created during
canonical absorption.

## Proposed Topology Changes
No new repository category is canonical merely because an ADR is proposed. Proposed domains remain non-materialized until the corresponding ADR is accepted and absorbed into the canonical architecture.

## Cognitive Pipeline
`OPERATORS/` contains the six canonical cognitive operators that implement
the cognitive pipeline: `LearningToMemory`, `MemoryToReasoning`,
`OpportunityToDecision`, `DecisionToExpression`, `ExpressionToConsequence`,
`ConsequenceToLearning`. The pipeline engine, session model, operator
registry, and event bus are defined in `OPERATORS/engine.py` and
`OPERATORS/registry.py`.

## Epistemic Operators
`OPERATORS/` also contains the six epistemic lifecycle operators defined
by ADR-007, ADR-008, and ADR-009:
`LearningToBelief`, `BeliefToFact`, `EvidenceToBeliefUpdate`,
`BeliefRegression`, `BeliefArchival`, `BeliefConflictResolution`.
These operators manage the full Belief lifecycle (Active → Promoted →
Regressed → Conflicted → Active → Archived) and the Fact domain.
They are independently invokable within the pipeline.

## Reasoners
`REASONERS/` contains the four cognitive reasoning modules used by
`OpportunityToDecision`: `EvidenceRanker`, `HypothesisGenerator`,
`ConfidenceEstimator`, `DecisionSelector`. These are owned by the
Decision Organ and are not independently invokable outside the pipeline.

## Runtime Artifact Stores — Core Pipeline
The following directories are populated at runtime by the cognitive
pipeline. They are not manually edited.

- `LEARNING/` — Learning entities, input to `LearningToMemory`
- `MEMORY/` — Memory entities, output of `LearningToMemory`
- `REASONING_PARAMETERS/` — Reasoning context snapshots, output of `MemoryToReasoning`
- `EVIDENCE/` — Evidence Set entities, output of `OpportunityToDecision`
- `DECISIONS/` — Decision entities, output of `OpportunityToDecision` (selected only)
- `EXPRESSIONS/` — Expression entities, output of `DecisionToExpression`
- `EVENTS/` — Event records emitted by operators via the event bus
- `SESSIONS/` — Session records written by the pipeline engine
- `WORLD_STATE/` — Synthesized world state snapshots

## Runtime Artifact Stores — Epistemic Layer
The following directories are materialized by the epistemic operators
(ADR-007, ADR-008, ADR-009). They are not manually edited.

- `BELIEFS/` — Belief entities at all lifecycle stages (Active, Promoted,
  Regressed, Conflicted, Archived)
- `FACTS/` — Fact entities; semantically permanent once promoted from a
  Belief (idempotent creation enforced)
- `EPISTEMIC_EVIDENCE/` — Evidence entities consumed by
  `EvidenceToBeliefUpdate` to adjust Belief confidence

## Test Suite
`tests/` contains the pytest-based test suite covering all twelve
operators, the pipeline engine, session persistence, and the full
Integration Scaffold.

- `tests/test_operators.py` — six core pipeline operators
- `tests/test_opportunity_to_decision.py` — REASONERS integration
- `tests/test_session_persistence.py` — session model and persistence
- `tests/test_learning_to_belief.py` — LearningToBelief operator
- `tests/test_belief_to_fact.py` — BeliefToFact operator
- `tests/test_evidence_to_belief_update.py` — EvidenceToBeliefUpdate operator
- `tests/test_belief_regression.py` — BeliefRegression operator
- `tests/test_belief_archival.py` — BeliefArchival operator
- `tests/test_belief_conflict_resolution.py` — BeliefConflictResolution operator
- `tests/test_integration_e2e.py` — Integration Scaffold: end-to-end
  pipeline across all 12 operators (cognitive tramo E2E, epistemic tramo
  E2E, full 12-operator pipeline)

## Reasoning Parameters (tunable)
`REASONING_PARAMETERS/` also contains manually authored parameter files
that tune reasoning behaviour:
- `belief_fact_promotion.md` — promotion threshold (0.80), minimum
  independent sources (1), regression threshold (0.50)
- `consequence_resolution.md` — consequence resolution parameters

These coexist with runtime-generated context snapshots in the same directory.

## Shared Libraries
`entity_markdown.py` — canonical entity serialisation/deserialisation
library used by all operators and tests.
`prediction_representation.py` — prediction state machine and parsing.
`qcontext.py` — context assembly utilities.
`engine.py` — root-level shim re-exporting `CognitiveEngine` and companion
types from `OPERATORS/engine.py` for bare-import compatibility.

## Project State
`PROJECT_STATE.md` — single-file operational snapshot of the project.
Read this file first when starting a new session. Updated in the same
commit as each relevant implementation.

## Validation Protocol
`VALIDATION_PROTOCOL.md` is the experimental protocol for attempting to refute the meta-model, not part of the meta-model itself.

## Investigation Log
`META_MODEL_INVESTIGATION.md` records inconclusive experiments: cases that neither validate nor refute the meta-model due to experimental limitations.

## Freeze Declaration
`FREEZE_DECLARATION.md` marks the official freeze of the standard (v1.0.0) and the start of the Evidence Phase.

## Proposal Registry
`PROPOSAL_REGISTRY.md` implements a cooling-off period for improvement ideas before they can affect the frozen standard.

## Architectural Note
`ARCHITECTURAL_NOTE_DESIGN_SPACE.md` is a non-normative observation on what was actually frozen: the design space, not just the model.

## Derived Specification
`ARTIFACT_BASE_CONTRACT_DERIVED_SPEC.md` is a non-normative, mechanically derivable specification of the Artifact base contract. It introduces no new semantics.

## Archive
`_archive/` contains superseded legacy documents, retained for history but not part of the frozen standard.

## Maintenance
This document is updated only when repository organization changes —
categories are added, removed, renamed, or reorganized. Additions,
removals, renames, version changes, or status changes of files within an
existing category do not require updating this document.
