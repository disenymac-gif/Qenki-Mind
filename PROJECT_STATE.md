# Project State

## Repository
disenymac-gif/Qenki-Mind

## Branch
main

## Baseline Commit
6add39f4480a6c81e621de5ad936b69e1a7c6d6b

## Last Updated
2026-07-16

## Current Architecture
Eight ADRs total. ADR-001 through ADR-008 all Closed. Six canonical
documents frozen. Full reference: `QENKI_MIND_GOVERNANCE_RULES_v1.md`
and `REPOSITORY_MAP.md`.

## Implemented
- Cognitive pipeline: 7 canonical operators
  (`LearningToMemory`, `MemoryToReasoning`, `OpportunityToDecision`,
  `DecisionToExpression`, `ExpressionToConsequence`, `ConsequenceToLearning`,
  `LearningToBelief`)
- `CognitiveEngine` with `run()` and `run_pipeline()` (artifact-centric API)
- `CognitiveSession` model + `_persist_session()` writing to `SESSIONS/`
- `EventBus` and `OperatorRegistry`
- REASONERS subsystem (`EvidenceRanker`, `HypothesisGenerator`,
  `ConfidenceEstimator`, `DecisionSelector`) — owned by `OpportunityToDecision`
- `entity_markdown.py`: canonical entity serialisation / deserialisation
- `engine.py` root shim: re-exports `CognitiveEngine` et al. from `OPERATORS/engine.py`
- Full test suite: `tests/test_operators.py`, `tests/test_opportunity_to_decision.py`,
  `tests/test_session_persistence.py`, `tests/test_learning_to_belief.py`
- `BELIEFS/` runtime artifact store: persistent epistemic layer materialized
  (topology declared per ADR-007, basis: ADR-008)
- `LearningToBelief` operator: Learning entity -> Belief entity, owned by
  Learning & Reflection Organ; BeliefCreated event; idempotent persist
- ADR-008: Closed (canonical documents absorbed + topology materialized +
  operator implemented)
- `PROJECT_STATE.md` (this document)

## Open Work
- Belief lifecycle operators not yet implemented:
  `BeliefToFact` (ADR-001 promotion), `BeliefRegression`,
  `BeliefArchival`, `BeliefConflictResolution`.
- `Operational State` capability: canonically supported, topology not yet defined.
- `Persistent Knowledge` capability: canonically supported, topology not yet defined.
- `Supporting Infrastructure` capability: no canonical basis identified yet.
- Integration readiness: all four external dependencies (Constitution,
  Objectives, Brand Expression Constraints, Situational Facts) remain
  undefined by their owning domains.

## Current Bottleneck
Belief lifecycle is incomplete. `LearningToBelief` creates Beliefs at
neutral confidence (0.50), but the promotion path (ADR-001: Belief → Fact
when convergent Evidence crosses the owned threshold) has no operator.
`BeliefToFact` is the highest-impact next operator: it closes the
Learning → Belief → Fact epistemic arc and makes the confidence threshold
in `REASONING_PARAMETERS/belief_fact_promotion.md` operationally active
for the first time.

## Blocked Decisions
None. All ADRs are Closed. `BeliefToFact` implementation may proceed
immediately; canonical basis is ADR-001 + ADR-008.

## Recent Decisions
- **2026-07-16** — `BELIEFS/` topology materialized per ADR-007/ADR-008.
  `LearningToBelief` operator implemented and test-covered (18 tests).
  ADR-008 transitioned to Closed.
- **2026-07-16** — ADR-008 accepted and absorbed into ONTOLOGY_v1,
  ORGANS_v1, COGNITIVE_ARCHITECTURE_v1.
- **2026-07-16** — `PROJECT_STATE.md` introduced as operational context
  snapshot. Updated in same commit as each relevant implementation.
- **2026-07-16** — Session persistence implemented and test-covered.
- **2026-07-16** — Root-level `engine.py` shim added.

## Next Iteration
Implement `BeliefToFact` operator: reads a Belief entity from `BELIEFS/`,
checks whether the confidence threshold in
`REASONING_PARAMETERS/belief_fact_promotion.md` is met with convergent,
independently-sourced Evidence, and if so promotes the Belief to Fact
status inside the persistent epistemic layer (ADR-001 + ADR-008). Also
creates the corresponding entry in a new `FACTS/` runtime artifact store
(topology to be derived from ADR-001 + ADR-008 as basis).

## Working Contract
- Branch: `main`. All work committed directly to `main`.
- No local artifacts unless a real technical blocker prevents GitHub writes.
- After each relevant implementation: commit + push + verify SHA + respond
  with `STATUS: PUSHED` block.
- `PROJECT_STATE.md` is updated in the same commit as the implementation
  it records. It is never updated in a standalone commit unless the only
  change is a state correction.
- Information here must be verifiable against actual repository content.
  Do not add items that are designed but not yet committed.
