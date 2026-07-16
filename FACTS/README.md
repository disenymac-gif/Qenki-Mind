# FACTS

## Purpose
Runtime artifact store for Fact entities. Materializes the Fact domain
defined by the Ontology and operationally activated by the `BeliefToFact`
operator (ADR-001 + ADR-008).

## Topological Basis
This directory exists because:
- `QENKI_MIND_ONTOLOGY_v1.md` defines Fact as a distinct epistemic
  commitment with strictly higher confidence than Belief;
- ADR-001 (Closed) establishes the Belief-to-Fact promotion invariant,
  including the convergent independently-sourced Evidence requirement and
  the owned confidence threshold;
- ADR-008 (Closed) establishes that promotion and regression occur inside
  the persistent epistemic layer rather than outside it; and
- `BeliefToFact` is the first operator to enact promotion, making the
  Fact domain operationally necessary for the first time.

This satisfies Repository Topology Derivation Rule 2
(`QENKI_MIND_GOVERNANCE_RULES_v1.md`): the domain is materialized only
once the canonical basis is closed and the first consuming operator is
implemented.

## Ownership
Learning & Reflection Organ, sole authority to enact Fact state changes.
No other organ may write authoritative Fact entities to this directory.
Other organs may read from this directory to consume Facts.

## Naming Convention
`fact-<stem>.md` where `<stem>` is derived from the source Belief
entity name (e.g., `BELIEFS/belief-learning-001.md` →
`FACTS/fact-belief-learning-001.md`).

## Fact Lifecycle States
- `Promoted` — actively held Fact; confidence met the promotion threshold
  at time of promotion and has not since been contradicted.
- `Regressed` — confidence dropped below the regression threshold
  subsequent to promotion; Fact returns to Belief status. The Fact record
  remains here permanently for epistemic history (ADR-008 Invariant 9).
- `Archived` — superseded or withdrawn; retained permanently.

## Relationship to BELIEFS/
Every Fact entity was promoted from a Belief entity. The corresponding
Belief entity in `BELIEFS/` transitions to `Epistemic State: Promoted`
when promotion occurs. If regression happens later, the Belief is
restored to `Active` and the Fact transitions to `Regressed`. The Fact
record is never deleted.

## Maintenance
Files in this directory are never manually edited. All authoritative
state changes are enacted by epistemic lifecycle operators
(`BeliefToFact`, `BeliefRegression`) owned by Learning & Reflection.
