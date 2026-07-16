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
- Cognitive pipeline: 8 canonical operators
  (`LearningToMemory`, `MemoryToReasoning`, `OpportunityToDecision`,
  `DecisionToExpression`, `ExpressionToConsequence`, `ConsequenceToLearning`,
  `LearningToBelief`, `BeliefToFact`)
- `CognitiveEngine` with `run()` and `run_pipeline()` (artifact-centric API)
- `CognitiveSession` model + `_persist_session()` writing to `SESSIONS/`
- `EventBus` and `OperatorRegistry`
- REASONERS subsystem (`EvidenceRanker`, `HypothesisGenerator`,
  `ConfidenceEstimator`, `DecisionSelector`) — owned by `OpportunityToDecision`
- `entity_markdown.py`: canonical entity serialisation / deserialisation
- `engine.py` root shim: re-exports `CognitiveEngine` et al. from `OPERATORS/engine.py`
- Full test suite: `tests/test_operators.py`, `tests/test_opportunity_to_decision.py`,
  `tests/test_session_persistence.py`, `tests/test_learning_to_belief.py`,
  `tests/test_belief_to_fact.py`
- `BELIEFS/` runtime artifact store: persistent epistemic layer (ADR-007/ADR-008)
- `FACTS/` runtime artifact store: Fact domain materialized (ADR-001 + ADR-008)
- `LearningToBelief` operator: Learning → Belief; BeliefCreated event
- `BeliefToFact` operator: Belief → Fact; reads `promotion_threshold` from
  `REASONING_PARAMETERS/belief_fact_promotion.md`; updates source Belief
  Epistemic State; FactPromoted event; idempotent guard (AlreadyPromotedError)
- `REASONING_PARAMETERS/belief_fact_promotion.md`: calibrated
  (`promotion_threshold: 0.80`; `minimum_independent_sources: 1`;
  `regression_threshold: 0.50`)
- ADR-001: Learning → Belief → Fact arc now fully operational
- ADR-008: Closed (topology materialized + operators implemented)
- `PROJECT_STATE.md` (this document)

## Open Work
- Belief lifecycle operators not yet implemented:
  `BeliefRegression` (Fact → Belief on contradicting Evidence),
  `BeliefArchival`, `BeliefConflictResolution`.
- `Operational State` capability: canonically supported, topology not yet defined.
- `Persistent Knowledge` capability: canonically supported, topology not yet defined.
- `Supporting Infrastructure` capability: no canonical basis identified yet.
- Integration readiness: all four external dependencies (Constitution,
  Objectives, Brand Expression Constraints, Situational Facts) remain
  undefined by their owning domains.

## Current Bottleneck
The epistemic arc is now complete in the promotion direction
(Learning → Belief → Fact). The regression direction is not yet
implemented: `BeliefRegression` (Fact → Belief when contradicting
Evidence drives confidence below `regression_threshold: 0.50`) has no
operator. Without it, the system has no mechanism to correct promoted
Facts that later prove wrong, which is an architectural gap given
ADR-008 Invariant 7 (promotion and regression both occur inside the
persistent epistemic layer).

However, `BeliefRegression` requires a triggering mechanism: an incoming
Evidence entity that contradicts an existing Fact. This is a structural
blocker — the operator depends on the Evidence input schema and how
contradiction is represented, which has no machine-readable convention yet.

The next unblocked bottleneck is therefore: define the canonical structure
for `EVIDENCE/*.md` entities and implement the `EvidenceToBeliefUpdate`
operator that routes new Evidence into the epistemic layer (either
reinforcing a Belief’s confidence or flagging contradiction). This
unblocks `BeliefRegression` and completes the contradiction-handling arc.

## Blocked Decisions
- `BeliefRegression`: blocked pending Evidence-to-epistemic-layer routing
  convention (no ADR required — implementable against existing ADR-001 +
  ADR-008 canonical basis once `EvidenceToBeliefUpdate` is defined).

## Recent Decisions
- **2026-07-16** — `BeliefToFact` operator implemented and test-covered
  (22 tests). `FACTS/` topology materialized. `belief_fact_promotion.md`
  calibrated. ADR-001 Learning→Belief→Fact arc fully operational.
- **2026-07-16** — `BELIEFS/` topology materialized per ADR-007/ADR-008.
  `LearningToBelief` operator implemented and test-covered (18 tests).
  ADR-008 transitioned to Closed.
- **2026-07-16** — ADR-008 accepted and absorbed into ONTOLOGY_v1,
  ORGANS_v1, COGNITIVE_ARCHITECTURE_v1.
- **2026-07-16** — `PROJECT_STATE.md` introduced as operational context
  snapshot.
- **2026-07-16** — Session persistence implemented and test-covered.
- **2026-07-16** — Root-level `engine.py` shim added.

## Next Iteration
Define the canonical schema for `EVIDENCE/*.md` entities and implement
`EvidenceToBeliefUpdate`: reads a new Evidence entity and an existing
Belief entity, determines whether the Evidence reinforces or contradicts
the Belief, and updates the Belief’s `Confidence`, `Supporting Evidence`,
or `Conflicting Evidence` sections accordingly. This operator is the
gateway to `BeliefRegression` and completes the full contradiction-handling
arc (ADR-001 + ADR-008).

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
- Continue automatically with the next unblocked bottleneck from
  `PROJECT_STATE.md` without asking between iterations.
