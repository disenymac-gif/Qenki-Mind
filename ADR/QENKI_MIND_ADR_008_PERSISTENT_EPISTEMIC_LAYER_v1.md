# ADR 008: Persistent Epistemic Layer

## Status
Proposed

## Context
The canonical Ontology defines Belief, Fact, Hypothesis, Evidence, and
Learning as distinct cognitive objects, and ADR-001 already binds the
Belief-to-Fact transition through independently-sourced Evidence and a
Learning & Reflection-owned confidence threshold. However, the current
canonical architecture stops at semantic existence and transition rules: it
does not yet decide whether Qenki-Mind maintains a persistent,
authoritative epistemic layer in repository topology, who owns that layer,
which organs may modify it, or how Learning changes future decisions by
revising operational belief state rather than only emitting historical
records. This leaves an architectural ambiguity with externally observable
consequences. One implementation could treat Beliefs as first-class,
persistent, revisable entities that shape future decisions; another could
leave beliefs implicit inside Memory, Evidence, or Decision records. Both
would satisfy the current semantic Ontology while producing materially
different learning behavior, decision explainability, and long-term
adaptation.

The ambiguity is not about storage convenience. It concerns whether
Qenki-Mind possesses a persistent epistemic layer as part of its cognitive
model, distinct from World State, Memory, and Evidence, and whether
Learning is architecturally empowered to revise that layer.

## Decision
Qenki-Mind shall include a persistent epistemic layer, materialized in
repository topology as a first-class domain owned authoritatively by the
Learning & Reflection Organ. This layer stores Beliefs as revisable,
persistent entities distinct from Memory, Evidence, Decision, and World
State.

Learning & Reflection is the sole authority permitted to enact changes to
a Belief's authoritative state, including creation, confidence revision,
promotion to Fact, regression from Fact to Belief, archival, and conflict
resolution. Other organs may consume Beliefs and may propose updates or
revisions through their own artifacts, but such proposals only take effect
once Learning & Reflection acts on them.

Evidence remains immutable support or contradiction linked to claims.
Memory remains retained cognitive history. World State remains the current
synthesized picture of the external environment. The epistemic layer is
architecturally distinct: it stores the organism's current internal claims
about what is believed to be true beyond direct observation, with explicit
confidence and revision history.

## Architectural Invariants
1. Belief is a first-class persistent epistemic entity, not merely an
   implicit view materialized from other domains.
2. Qenki-Mind maintains exactly one authoritative persistent epistemic
   layer for Beliefs and related lifecycle state.
3. Learning & Reflection is the sole organ authorized to enact changes to
   a Belief's authoritative state.
4. Other organs may propose Belief creation or revision, but proposal and
   authority are permanently distinct concepts.
5. Every authoritative Belief state change must be traceable to supporting
   and/or contradicting Evidence, Learning, or Reflection inputs.
6. A Belief may exist with incomplete Evidence, but its confidence and
   revision history must make that epistemic incompleteness explicit.
7. Fact remains a strictly higher epistemic commitment than Belief and is
   governed by ADR-001; promotion and regression occur inside the
   persistent epistemic layer rather than outside it.
8. Conflicting Beliefs may coexist transiently only if the conflict is
   explicitly represented and unresolved; no implementation may silently
   collapse conflict by deletion or overwrite.
9. Belief archival never erases epistemic history; inactive or superseded
   Beliefs remain retrievable.
10. Future Decisions may consume the persistent epistemic layer, but may
    not authoritatively mutate it.

## Consequences
- QENKI_MIND_ONTOLOGY_v1.md requires clarification so that Belief, Fact,
  Hypothesis, Evidence, and Learning are not only semantically distinct,
  but also structurally related to a persistent epistemic layer owned by
  Learning & Reflection.
- QENKI_MIND_ORGANS_v1.md requires clarification so that Learning &
  Reflection's ownership scope explicitly includes authoritative Belief
  lifecycle management, while other organs are limited to proposal and
  consumption.
- QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md requires clarification so that
  learning is architecturally capable of changing future reasoning through
  Belief revision rather than only producing historical records.
- Repository topology may materialize a new canonical domain for the
  persistent epistemic layer only after this ADR is accepted. The accepted
  ADR decides the existence of the layer, not the eventual physical
  substrate (for example BELIEFS/, a datastore, or a distributed store).
- Because Fact regression to Belief is permitted, Fact is no longer
  strictly monotonic across the full lifecycle; monotonicity only holds
  until contradicting Evidence triggers an authorized regression.
- REASONING_PARAMETERS/ remains the canonical home for tunable thresholds
  and criteria used within Belief promotion, regression, and conflict
  handling, provided they do not violate the invariants above.

## Affected Canonical Documents
- QENKI_MIND_ONTOLOGY_v1.md (Belief, Fact, Evidence, Learning, Hypothesis)
- QENKI_MIND_ORGANS_v1.md (Learning & Reflection authority boundaries;
  other organs' proposal vs. enactment boundaries)
- QENKI_MIND_COGNITIVE_ARCHITECTURE_v1.md (learning feedback into future
  reasoning and decision formation; persistent epistemic layer as an
  architectural property)
- QENKI_MIND_GOVERNANCE_RULES_v1.md (only if the accepted ADR is later
  absorbed into topology derivation language)

## Relationships
Depends on ADR-001 for Belief-to-Fact promotion invariants and extends the
architecture by deciding whether Beliefs remain purely semantic objects or
become part of a persistent epistemic layer. Supersedes no prior ADR.
