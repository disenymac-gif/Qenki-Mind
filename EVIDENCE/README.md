# EVIDENCE/

## Purpose

This directory stores Evidence Set entities produced by the
`OpportunityToDecision` cognitive operator during the execution of the
cognitive pipeline.

An Evidence Set is a structured record of all ranked evidence considered
before a decision is made. It is not a decision itself — it is the
transparent audit trail that justifies why a particular opportunity was
selected or rejected.

## Ownership

Evidence entities are owned by the **Decision Organ**, as defined in
`QENKI_MIND_ORGANS_v1.md`. They are produced automatically at runtime and
should never be edited manually.

## Naming Convention

```
evidence_set_for_<decision-id>.md
```

Example: `evidence_set_for_decision-growth-q3.md`

## Content Structure

Each Evidence Set entity contains:

- **Identity** — the evidence set identifier
- **Ownership** — Decision Organ
- **Canonical Basis** — reference to the originating opportunity
- **Evidence Items** — ranked list of weighted evidence items
- **Supporting World State** — world state snapshot at time of reasoning
- **Supporting Objectives** — objectives snapshot at time of reasoning
- **Supporting Memory** — memory items injected from `MemoryToReasoning`
- **Generated Hypotheses** — hypotheses produced by `HypothesisGenerator`
- **Confidence Estimate** — float in [0.0, 1.0] from `ConfidenceEstimator`
- **Last Updated** — ISO date of artifact creation

## Relationship to DECISIONS/

Every entry in `DECISIONS/` has a corresponding Evidence Set in this
directory. If a decision was **not** selected (confidence < 0.5), only the
Evidence Set is written — no Decision entity is created. The Evidence Set
therefore always exists; the Decision entity is conditional.

## Runtime Behaviour

The directory is created automatically by the operator if it does not
exist. No manual initialization is required.
