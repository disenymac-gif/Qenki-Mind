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
Eight ADRs total. ADR-001 through ADR-007 absorbed. ADR-008 accepted and
absorbed into ONTOLOGY_v1, ORGANS_v1, and COGNITIVE_ARCHITECTURE_v1.
Six canonical documents frozen. Full reference: `QENKI_MIND_GOVERNANCE_RULES_v1.md`
and `REPOSITORY_MAP.md`.

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
- ADR-008 accepted and absorbed: persistent epistemic layer is now an
  architectural invariant across ONTOLOGY_v1, ORGANS_v1, COGNITIVE_ARCHITECTURE_v1
- `PROJECT_STATE.md` (this document)

## Open Work
- Persistent epistemic layer topology: `BELIEFS/` domain (or equivalent
  substrate) not yet materialized. ADR-008 is accepted; materialization
  requires an explicit topology decision per the Repository Topology
  Derivation principle (ADR-007 / Governance Rules).
- `Operational State` capability: canonically supported, topology not yet defined.
- `Persistent Knowledge` capability: canonically supported, topology not yet defined.
- `Supporting Infrastructure` capability: no canonical basis identified yet.
- Integration readiness: all four external dependencies (Constitution,
  Objectives, Brand Expression Constraints, Situational Facts) remain
  undefined by their owning domains.

## Current Bottleneck
Persistent epistemic layer topology is not yet materialized. ADR-008 has
been accepted and absorbed into the canonical documents, but the `BELIEFS/`
domain (or chosen substrate) must now be explicitly declared under ADR-007
before any Belief persistence operators can be implemented.

## Blocked Decisions
- **Epistemic topology materialization** — No blocker at ADR level. The
  topology decision (`BELIEFS/` directory, separate datastore, or other
  form) must be taken explicitly under the Repository Topology Derivation
  principle (ADR-007). Once declared, Belief operators and persistence can
  be implemented.

## Recent Decisions
- **2026-07-16** — ADR-008 accepted and absorbed. ONTOLOGY_v1 updated
  with Belief epistemic invariants and Learning epistemic feedback.
  ORGANS_v1 updated with authority boundaries for all organs re: epistemic
  layer. COGNITIVE_ARCHITECTURE_v1 updated with epistemic feedback path
  and rhythm-level epistemic actions.
- **2026-07-16** — `PROJECT_STATE.md` introduced as single-file
  operational context snapshot. Updated in same commit as each
  relevant implementation.
- **2026-07-16** — Session persistence implemented and test-covered.
- **2026-07-16** — Root-level `engine.py` shim added.

## Next Iteration
Declare the persistent epistemic layer topology under ADR-007
(e.g., `BELIEFS/` directory as a runtime artifact store), then implement
the Belief entity schema and the first Belief-lifecycle operator
(`LearningToBelief` or equivalent).

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
