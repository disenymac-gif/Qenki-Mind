# Project State

## Repository
disenymac-gif/Qenki-Mind

## Branch
main

## Baseline Commit
2653706620987b258915467f690877745a8dc758

## Last Updated
2026-07-16

## Current Architecture
Six canonical documents (frozen, Governance Rules v1, Cognitive
Architecture v1, Ontology v1, Organs v1, Cognitive Contract Layer v1,
Interface Boundary Specification v1). Seven ADRs absorbed (ADR-001
through ADR-007). ADR-008 pending (see Blocked Decisions).
Full reference: `QENKI_MIND_GOVERNANCE_RULES_v1.md` and `REPOSITORY_MAP.md`.

## Implemented
- Cognitive pipeline: 6 canonical operators
  (`LearningToMemory`, `MemoryToReasoning`, `OpportunityToDecision`,
  `DecisionToExpression`, `ExpressionToConsequence`, `ConsequenceToLearning`)
- `CognitiveEngine` with `run()` and `run_pipeline()` (artifact-centric API)
- `CognitiveSession` model + `_persist_session()` writing to `SESSIONS/`
- `EventBus` and `OperatorRegistry`
- REASONERS subsystem (`EvidenceRanker`, `HypothesisGenerator`,
  `ConfidenceEstimator`, `DecisionSelector`) — owned by `OpportunityToDecision`
- `entity_markdown.py`: canonical entity serialisation / deserialisation
- `engine.py` root shim: re-exports `CognitiveEngine` et al. from `OPERATORS/engine.py`
- Full test suite: `tests/test_operators.py`, `tests/test_opportunity_to_decision.py`,
  `tests/test_session_persistence.py`
- `PROJECT_STATE.md` (this document)

## Open Work
- ADR-008 requires acceptance and absorption into three canonical documents
  (`ONTOLOGY`, `ORGANS`, `COGNITIVE_ARCHITECTURE`) before the persistent
  epistemic layer (`BELIEFS/` or equivalent) can be materialized.
- `Operational State` capability: canonically supported, topology not yet defined.
- `Persistent Knowledge` capability: canonically supported, topology not yet defined.
- `Supporting Infrastructure` capability: no canonical basis identified yet.
- Integration readiness: all four external dependencies (Constitution,
  Objectives, Brand Expression Constraints, Situational Facts) remain
  undefined by their owning domains.

## Current Bottleneck
ADR-008 (`Persistent Epistemic Layer`) is Proposed but not yet Accepted.
No Belief persistence, epistemic layer materialization, or canonical
document updates for `ONTOLOGY`, `ORGANS`, or `COGNITIVE_ARCHITECTURE`
can proceed until this ADR is resolved.

## Blocked Decisions
- **ADR-008** — Proposed. Blocks: epistemic layer topology, `BELIEFS/`
  domain, Belief lifecycle operators, and canonical document absorption
  into `ONTOLOGY_v1`, `ORGANS_v1`, `COGNITIVE_ARCHITECTURE_v1`.
  File: `ADR/QENKI_MIND_ADR_008_PERSISTENT_EPISTEMIC_LAYER_v1.md`

## Recent Decisions
- **2026-07-16** — Session persistence implemented and test-covered.
  `CognitiveEngine._persist_session()` writes session files to `SESSIONS/`.
  Test: `tests/test_session_persistence.py`. Commit: `265370662`.
- **2026-07-16** — Root-level `engine.py` shim added to resolve bare
  `from engine import CognitiveEngine` import in test suite. Commit: `265370662`.
- **2026-07-16** — `MATURITY_STATUS.md` updated: Session Persistence
  marked Implemented and test-covered.

## Next Iteration
Accept and absorb ADR-008 into the three affected canonical documents
(`ONTOLOGY_v1`, `ORGANS_v1`, `COGNITIVE_ARCHITECTURE_v1`), then
materialize the persistent epistemic layer topology.

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
