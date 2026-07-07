# Reasoning Parameters

## Purpose
This domain holds Qenki-Mind's own tunable reasoning parameters — values
that govern how the organism reasons, owned entirely by Qenki-Mind itself,
as distinct from external dependencies declared in
`QENKI_MIND_INTERFACE_BOUNDARY_SPECIFICATION_v1.md`.

## Ownership
Owned by Qenki-Mind. Where a specific parameter's tuning authority is
assigned to a single organ by canonical architecture or an absorbed ADR,
that organ is the sole party permitted to change its value.

## What Belongs Here
Only parameters explicitly identified by the canonical documents as
tunable and organ-owned. Each parameter is recorded in its own document,
identified by a stable parameter name rather than by its current tuning
wording, and structured to separate its fixed definition from its
current operational value.

- Belief-to-fact promotion parameter — owned by the Learning & Reflection
  Organ, per `QENKI_MIND_ONTOLOGY_v1.md` and `QENKI_MIND_ORGANS_v1.md`.
- Consequence resolution parameter — owned by the Learning & Reflection
  Organ, per `QENKI_MIND_COGNITIVE_CONTRACT_LAYER_v1.md` and
  `QENKI_MIND_ORGANS_v1.md`.

## What Does Not Belong Here
This domain does not hold external dependencies, canonical architecture,
or any value whose ownership has not been explicitly established by a
canonical document or an absorbed ADR. It does not contain algorithms or
implementation logic — only each parameter's definition, current value,
and change history.

## Document Structure
Every parameter document follows this structure:
- Identity (name, owning organ)
- Canonical Basis
- Parameter Definition (what the parameter governs)
- Current Value
- Change History
- Last Updated

## Lifecycle
Values here may change continuously without requiring architectural
review, as established in `QENKI_MIND_GOVERNANCE_RULES_v1.md`. Only the
existence and ownership of a parameter category is architectural; its
specific value is not. An unset value means the parameter has not yet
been calibrated — it does not mean the underlying architectural
invariant is inactive, since that invariant is already binding through
the canonical documents.
