# ADR 002: Insight Handoff Authority Between Sense-Making and Opportunity

## Status
Closed

## Context
The canonical transformation graph shows Insight flowing from Sense-Making
to Opportunity, but the Organs specification did not define whether
Sense-Making forwards every Insight it forms or filters them before
forwarding. This left relevance authority ambiguously distributed between
the two organs, permitting materially different implementations: one in
which Sense-Making co-determines relevance, and one in which Opportunity
alone determines it. These produce observably different sets of
Opportunities the organism ever considers.

## Decision
Sense-Making forwards every Insight it forms to Opportunity by default.
Sense-Making may withhold an Insight only under narrow, explicitly bounded
exceptions. All relevance and timeliness judgment beyond those bounded
exceptions belongs exclusively to the Opportunity Organ.

## Architectural Invariants
1. Opportunity is the sole organ with authority to determine opportunity
   relevance.
2. Sense-Making's default behavior is to forward every Insight.
3. Sense-Making may withhold an Insight only under explicitly bounded
   architectural exceptions.
4. Those exceptions are limited to:
   - insufficient confidence for meaningful evaluation;
   - explicit redundancy with an Insight already pending evaluation.
5. A withheld Insight is never discarded.
6. Every Insight remains permanently retrievable through the organism's
   memory.
7. Opportunity evaluates every Insight that reaches it; it is never
   required to reconstruct or rediscover Insights withheld upstream.

## Consequences
- QENKI_MIND_ORGANS_v1.md is clarified: Sense-Making's mission remains
  explanatory, not evaluative; its withholding authority is strictly
  bounded and must never expand into relevance judgment proper, which
  remains exclusive to Opportunity.
- QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md is clarified: the Insight to
  Opportunity handoff in the daily cognitive loop is now a default,
  near-total forwarding step rather than an ambiguous filtering step.
- QENKI_MIND_ONTOLOGY_v1.md is clarified: the Insight object's transition
  to Opportunity is now bound by the invariants above rather than left
  organizationally undefined.
- Every withheld Insight remains permanently retrievable through Memory,
  ensuring no explanatory work performed by Sense-Making is ever silently
  lost, regardless of whether it becomes an Opportunity.

## Affected Canonical Documents
- QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md (Insight to Opportunity handoff step)
- QENKI_MIND_ORGANS_v1.md (Sense-Making and Opportunity authority boundaries)
- QENKI_MIND_ONTOLOGY_v1.md (Insight object transformation rules)
- MEMORY_REPOSITORY/ (permanent retrievability of withheld Insights)
