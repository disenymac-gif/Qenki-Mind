# EPISTEMIC_EVIDENCE

## Purpose
Runtime artifact store for epistemic Evidence entities: Observations
formally linked to a claim they support or challenge, as defined by
`QENKI_MIND_ONTOLOGY_v1.md`. These entities are distinct from the
`EVIDENCE/` directory, which stores Decision-Organ-owned Evidence Sets
produced by `OpportunityToDecision`.

## Distinction from EVIDENCE/

| Directory | Owner | Producer | Consumer |
|---|---|---|---|
| `EVIDENCE/` | Decision Organ | `OpportunityToDecision` | Decision pipeline |
| `EPISTEMIC_EVIDENCE/` | Learning & Reflection Organ | Sense-Making / external input | `EvidenceToBeliefUpdate`, `BeliefToFact` |

## Canonical Basis
- `QENKI_MIND_ONTOLOGY_v1.md` — Evidence definition (immutable, permanent)
- ADR-001 — promotion requires independently-sourced Evidence
- ADR-008 — every authoritative Belief state change traceable to Evidence

## Ownership
Learning & Reflection Organ. No other organ may write authoritative
epistemic Evidence entities to this directory.

## Naming Convention
`evidence-<stem>.md` where `<stem>` describes the subject claim
(e.g., `evidence-engagement-quality-001.md`).

## Entity Schema

Every `evidence-*.md` file must contain exactly these sections:

### Identity
Unique identifier for this Evidence entity.

### Ownership
Learning & Reflection Organ, per QENKI_MIND_ONTOLOGY_v1 and ADR-008.

### Canonical Basis
Source observation, experiment, or learning entity that grounded this
Evidence (file path or external reference).

### Claim
The proposition this Evidence speaks to (must match or reference the
`Claim` field of a Belief entity in `BELIEFS/`).

### Valence
One of: `Supporting` | `Contradicting` | `Neutral`.
`Supporting`: increases confidence in the linked Belief.
`Contradicting`: decreases confidence; may trigger BeliefRegression.
`Neutral`: recorded for audit; no confidence change applied.

### Strength
Float in [0.0, 1.0]. Magnitude of the confidence delta to apply.
`0.0` = negligible signal; `1.0` = decisive signal. Governed by
`REASONING_PARAMETERS/evidence_strength_calibration.md` (not yet
created; uses default 0.10 until calibrated).

### Source
Distinct origin identifier. Used to assess Evidence independence when
evaluating Fact promotion criteria (ADR-001).

### Linked Belief
File path to the Belief entity this Evidence is linked to
(e.g., `BELIEFS/belief-engagement-quality.md`).

### Current State
One of: `Pending` | `Applied` | `Superseded` | `Archived`.
`Pending`: not yet applied to any Belief.
`Applied`: confidence delta has been applied to the linked Belief.
`Superseded`: a later Evidence entity supersedes this one for the same claim.
`Archived`: withdrawn or expired.

### Change History
Append-only log of state changes.

### Last Updated
ISO date of last state change.

## Immutability Rule
Per the Ontology, Evidence entities are permanent and immutable once
created. The `EvidenceToBeliefUpdate` operator writes the `Current State`
field to `Applied` as the sole allowed mutation — this records that the
evidence was consumed, while leaving the epistemic content (Claim,
Valence, Strength, Source) unchanged. No other field may be overwritten
after creation.

## Lifecycle
```
Created (Pending)
    |
    v
Applied  <-- EvidenceToBeliefUpdate
    |
    +---> if Valence=Contradicting and Belief.Confidence drops
    |     below regression_threshold -> future BeliefRegression
    |
    v
Archived / Superseded  (manual or operator-driven)
```
