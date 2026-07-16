# Decision: Reference Entity

## Identity
decision-reference-001

## Ownership
Owned by the Decision Organ, per QENKI_MIND_ORGANS_v1.md. This document is a canonical reference entity, not an operational decision produced by the cognitive runtime.

## Canonical Basis
DECISIONS/README.md — Minimal Entity Structure.

## Context
This entity was created solely as a canonical reference for validating entity parsing, persistence, and operator behavior. It does not represent a real operational decision made by Qenki-Mind and must not be treated as domain knowledge.

## Hypotheses
- A parser built against DECISIONS/README.md's Minimal Entity Structure should read every section of this file without error.
- An operator transforming this Decision into an Expression should preserve traceability back to this entity via Canonical Basis and Links.

## Predictions
- entity_markdown.parse_entity_markdown() will return exactly 12 sections (plus optional title) when applied to this file.
- entity_markdown.validate_entity_structure() will pass when given the Minimal Entity Structure section list as the required contract.

## Consequences
- This file serves as the golden reference for DecisionToExpression until a real operational Decision exists in this repository.
- Any future change to the Minimal Entity Structure contract should be validated first against this reference entity.

## Learning
None yet. This section will remain empty of operational content, since this entity does not undergo real belief revision.

## Links
- DECISIONS/README.md
- EXPRESSIONS/README.md (target domain for DecisionToExpression)

## Current State
Reference

## Change History
- 2026-07-16: Created as the first canonical reference entity for the Decision domain.

## Last Updated
2026-07-16
