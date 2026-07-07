# ADR 005: Mental Model Deprecation Authority

## Status
Closed

## Context
Mental Models are reusable explanatory templates originated by Sense-Making
and continuously applied by it during reasoning. The Ontology and Organs
specification assigned Learning & Reflection a role in revising or
deprecating Mental Models based on accumulated performance, but did not
explicitly foreclose Sense-Making, as the originating organ, from also
holding concurrent authority over deprecation. This left open the
possibility of two organs independently acting on the same model's status,
creating a race condition capable of producing inconsistent reasoning
outcomes depending on timing alone.

## Decision
Learning & Reflection holds sole authority to deprecate or reinstate a
Mental Model, based on accumulated performance across its applications.
Sense-Making may propose deprecation based on its own observed application
difficulties, but such proposals only take effect once Learning &
Reflection acts on them.

## Architectural Invariants
1. Every Mental Model has exactly one authoritative lifecycle owner.
2. Learning & Reflection is the sole authority permitted to deprecate or
   reinstate a Mental Model.
3. Sense-Making may propose deprecation but may never enact it.
4. Proposal and authority are permanently distinct concepts.
5. A Mental Model remains active until Learning & Reflection explicitly
   changes its status.
6. Deprecation must be justified by accumulated performance rather than
   arbitrary preference.
7. Deprecation never deletes a Mental Model.
8. Every deprecated Mental Model remains permanently retrievable as part
   of the organism's cognitive history.

## Consequences
- QENKI_MIND_ORGANS_v1.md is clarified: Learning & Reflection's ownership
  scope explicitly includes sole authority over Mental Model lifecycle
  status, while Sense-Making's role is explicitly limited to proposal
  rather than enactment.
- QENKI_MIND_ONTOLOGY_v1.md is clarified: the Mental Model object's
  deprecation transition is now bound by a single-owner invariant rather
  than left organizationally ambiguous.
- ORGANS/SENSE_MAKING/ retains the record of any deprecation proposals it
  raises, while ORGANS/LEARNING_REFLECTION/ retains the authoritative
  record of every lifecycle status change it enacts.
- Deprecated Mental Models remain permanently retrievable within the
  organism's memory, ensuring no explanatory framework is ever silently
  erased from its cognitive history.

## Affected Canonical Documents
- QENKI_MIND_ORGANS_v1.md (Learning & Reflection and Sense-Making
  authority boundaries)
- QENKI_MIND_ONTOLOGY_v1.md (Mental Model lifecycle transition rules)
