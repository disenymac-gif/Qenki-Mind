# BELIEFS

## Purpose
Runtime artifact store for Belief entities. Materializes the persistent
epistemic layer defined by ADR-008 and owned by the Learning & Reflection
Organ.

## Topological Basis
This directory exists because ADR-008 (Persistent Epistemic Layer, Status:
Closed) explicitly establishes:
- the existence of a persistent epistemic layer for Beliefs;
- its architectural purpose (first-class epistemic entity store, distinct
  from Memory, Evidence, World State, and Decision);
- its ownership (Learning & Reflection Organ, sole authority to enact
  Belief state changes); and
- its role within the organism (enables Learning to change future reasoning
  through Belief revision, not only through historical records).

This satisfies the four conditions of Repository Topology Derivation Rule 2
(QENKI_MIND_GOVERNANCE_RULES_v1.md). The directory was not materialized
before ADR-008 was accepted and absorbed.

## Ownership
Learning & Reflection Organ. No other organ may write authoritative Belief
entities to this directory. Other organs may read from this directory to
consume Beliefs.

## Contents
Belief entity files in canonical entity Markdown format, written by the
`LearningToBelief` operator. Each file encodes a single Belief with:
- identity, claim text, confidence score, epistemic state, and source
  Learning entity;
- full revision history traceable to Evidence or Learning inputs;
- explicit incompleteness marker when Evidence is partial.

## Naming Convention
`belief-<stem>.md` where `<stem>` is derived from the source Learning
entity name (e.g., `LEARNING/learning-001.md` → `BELIEFS/belief-learning-001.md`).

## Epistemic States
A Belief entity may be in one of the following states:
- `Active` — currently held with meaningful confidence.
- `Promoted` — confidence crossed the Fact promotion threshold (ADR-001);
  the Belief record remains as the regression target.
- `Regressed` — previously Promoted, now returned to Belief upon
  contradicting Evidence (ADR-001, ADR-008 Invariant 7).
- `Archived` — no longer held; retained permanently for epistemic history
  (ADR-008 Invariant 9). Never deleted.
- `Conflicted` — in explicit, unresolved conflict with another Belief;
  coexists until Learning & Reflection resolves (ADR-008 Invariant 8).

## Maintenance
Files in this directory are never manually edited. All authoritative
state changes are enacted by the `LearningToBelief` operator or future
epistemic lifecycle operators (e.g., `BeliefToFact`, `BeliefRegression`,
`BeliefArchival`) owned by Learning & Reflection.
