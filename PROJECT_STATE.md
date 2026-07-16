# Project State

## Repository
disenymac-gif/Qenki-Mind

## Branch
main

## Baseline Commit
6add39f4480a6c81e621de5ad936b69e1a7c6d6b

## Last Updated
2026-07-17

## Current Architecture
Nine ADRs total. ADR-001 through ADR-009 all Closed. Six canonical
documents frozen. Full reference: `QENKI_MIND_GOVERNANCE_RULES_v1.md`
and `REPOSITORY_MAP.md`.

## Implemented
- Cognitive pipeline: 12 canonical operators
  (`LearningToMemory`, `MemoryToReasoning`, `OpportunityToDecision`,
  `DecisionToExpression`, `ExpressionToConsequence`, `ConsequenceToLearning`,
  `LearningToBelief`, `BeliefToFact`, `EvidenceToBeliefUpdate`,
  `BeliefRegression`, `BeliefArchival`, `BeliefConflictResolution`)
- `CognitiveEngine` with `run()` and `run_pipeline()` (artifact-centric API)
- `CognitiveSession` model + `_persist_session()` writing to `SESSIONS/`
- `EventBus` and `OperatorRegistry`
- REASONERS subsystem (`EvidenceRanker`, `HypothesisGenerator`,
  `ConfidenceEstimator`, `DecisionSelector`) — owned by `OpportunityToDecision`
- `entity_markdown.py`: canonical entity serialisation / deserialisation
- `engine.py` root shim: re-exports `CognitiveEngine` et al. from `OPERATORS/engine.py`
- Full test suite: `tests/test_operators.py`, `tests/test_opportunity_to_decision.py`,
  `tests/test_session_persistence.py`, `tests/test_learning_to_belief.py`,
  `tests/test_belief_to_fact.py`, `tests/test_evidence_to_belief_update.py`,
  `tests/test_belief_regression.py`, `tests/test_belief_archival.py`,
  `tests/test_belief_conflict_resolution.py`
- **`tests/test_integration_e2e.py`**: Integration Scaffold — end-to-end
  pipeline across all 12 operators (Frontera 3 complete)
- `BELIEFS/` runtime artifact store: persistent epistemic layer (ADR-007/ADR-008)
- `FACTS/` runtime artifact store: Fact domain materialized (ADR-001 + ADR-008)
- `EPISTEMIC_EVIDENCE/` runtime artifact store: epistemic Evidence schema
- `LearningToBelief` operator: Learning → Belief; BeliefCreated event
- `BeliefToFact` operator: Belief → Fact; FactPromoted event;
  idempotent guard (AlreadyPromotedError); ConflictedBeliefError guard
- `EvidenceToBeliefUpdate` operator: Evidence → Belief confidence delta;
  BeliefConfidenceUpdated + BeliefRegressionPending events;
  idempotent guard (AlreadyAppliedError)
- `BeliefRegression` operator: Belief (Regression Pending) → Fact (Regressed)
  + Belief (Active); FactRegressed event;
  guard: BeliefNotRegressionPendingError + FactNotFoundError
- `BeliefArchival` operator: Belief (any non-Archived) → Belief (Archived);
  co-archives Fact if present; BeliefArchived + FactArchived events;
  terminal operator; guard: BeliefAlreadyArchivedError
- `BeliefConflictResolution` operator: Belief (Conflicted) → Belief (Active);
  re-evaluates net confidence from Applied Evidence corpus;
  net = sum(Supporting strengths) − sum(Contradicting strengths), clamped [0,1];
  compares against promotion_threshold; sets Active in both outcomes;
  never promotes directly; BeliefConflictResolved event;
  guard: BeliefNotConflictedError
- ADR-009: Belief Conflict Resolution Rule — Closed
  QENKI_MIND_ONTOLOGY_v1.md and QENKI_MIND_ORGANS_v1.md absorbed ADR-009
- ADR-008: Persistent Epistemic Layer — Closed
- ADR-001: Learning → Belief → Fact arc fully operational
  (all directions: promotion, regression, archival, conflict resolution)
- Full Belief lifecycle now complete:
  Active → Promoted → Regressed → Conflicted → Active (resolved) → Archived
- Integration tests: full Evidence → Belief → Fact pipeline (E2E);
  full regression arc (E2E); full archival arc (E2E);
  conflict resolution above threshold → promotable (E2E);
  conflict resolution below threshold → Active, not promoted (E2E)
- `REASONING_PARAMETERS/belief_fact_promotion.md`: calibrated
  (`promotion_threshold: 0.80`; `minimum_independent_sources: 1`;
  `regression_threshold: 0.50`)
- `PROJECT_STATE.md` (this document)
- **`MATURITY_STATUS.md`** — consistency pass complete (2026-07-17):
  updated to 9 ADRs all Closed, Epistemic Layer section added
  (Implemented and test-covered), Cognitive Pipeline section updated
  to reflect all 12 operators and Integration Scaffold
- **`REPOSITORY_MAP.md`** — consistency pass complete (2026-07-17):
  Epistemic Operators section added, Epistemic Runtime Artifact Stores
  section added (BELIEFS/, FACTS/, EPISTEMIC_EVIDENCE/), Test Suite
  section updated to enumerate all 10 test files

## Open Work
- `Operational State` capability: canonically supported, topology not yet defined.
- `Persistent Knowledge` capability: canonically supported, topology not yet defined.
- `Supporting Infrastructure` capability: no canonical basis identified yet.
- Integration readiness: all four external dependencies (Constitution,
  Objectives, Brand Expression Constraints, Situational Facts) remain
  undefined by their owning domains.

## Current Bottleneck
Consistency pass (Frontera 3, option 3) is complete. `MATURITY_STATUS.md`
and `REPOSITORY_MAP.md` are now aligned with the 12-operator / 9-ADR state.

The two remaining meaningful development frontiers both require an
**owner ADR decision** before any implementation can proceed:

1. **Operational State topology** (ADR-010 candidate): Define the
   `OPERATIONAL_STATE/` domain and its canonical entity schema. Requires
   an ADR to establish topology under the Repository Topology Derivation
   principle.

2. **Persistent Knowledge topology** (ADR-010 or ADR-011 candidate):
   Define the `PERSISTENT_KNOWLEDGE/` domain, distinct from `BELIEFS/`
   and `FACTS/`. Requires an ADR to distinguish this domain from the
   epistemic layer already in place.

Both frontiers are equally unblocked from a technical standpoint.
Neither can proceed without explicit owner selection — this is an
architectural governance decision, not a technical decision.

## Blocked Decisions
- Owner must select which frontier to pursue next: Operational State
  topology (option 1) or Persistent Knowledge topology (option 2).
  Both require a new ADR. No implementation will proceed until the
  direction is confirmed.

## Recent Decisions
- **2026-07-17** — Consistency pass complete. `MATURITY_STATUS.md`
  updated: 9 ADRs all Closed; Epistemic Layer section added (Implemented
  and test-covered); Cognitive Pipeline section updated to 12 operators
  and Integration Scaffold. `REPOSITORY_MAP.md` updated: Epistemic
  Operators section added, Epistemic Runtime Artifact Stores added,
  Test Suite section updated. No defects detected.
- **2026-07-17** — Frontera 3 complete. Integration Scaffold implemented:
  `tests/test_integration_e2e.py` covers all 12 operators in three
  test classes (cognitive tramo E2E, epistemic tramo E2E, full 12-operator
  pipeline). Fixture strategy: real entity_markdown files, monkeypatch.chdir,
  mod.BASE = tmp_path pattern (canonical). No defects detected.
- **2026-07-16** — ADR-009 opened and closed. `BeliefConflictResolution`
  implemented and test-covered (30 tests). Full Belief lifecycle complete.
  12 operators total. All epistemic lifecycle operators operational.
- **2026-07-16** — `BeliefArchival` operator implemented and test-covered
  (31 tests). Terminal epistemic transition.
- **2026-07-16** — `BeliefRegression` operator implemented and
  test-covered (28 tests).
- **2026-07-16** — `EvidenceToBeliefUpdate` operator implemented and
  test-covered (25 tests).
- **2026-07-16** — `BeliefToFact` operator implemented and test-covered
  (22 tests).
- **2026-07-16** — `LearningToBelief` operator implemented and test-covered
  (18 tests). ADR-008 transitioned to Closed.
- **2026-07-16** — ADR-008 accepted and absorbed.
- **2026-07-16** — `PROJECT_STATE.md` introduced.
- **2026-07-16** — Session persistence implemented.
- **2026-07-16** — Root-level `engine.py` shim added.

## Next Iteration
Awaiting owner ADR direction. Two frontiers open:
1. Operational State topology → requires ADR-010
2. Persistent Knowledge topology → requires ADR-010 or ADR-011

Once the owner selects a direction and the ADR is drafted, implementation
can proceed without further pauses.

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
- Pause and await owner direction when multiple equally-unblocked
  frontiers exist and a selection cannot be inferred from prior context.
