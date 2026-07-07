# Qenki-Mind Repository Map

## Purpose
This is a living operational document describing the current structure of
the Qenki-Mind repository. It is not canonical architecture and requires
no architectural review to update. It describes categories of content, not
individual filenames or their current status — the repository itself is
the authoritative inventory of what exists. Future topology is defined by
the canonical architecture, not by this document.

## Canonical Documents
Root-level canonical architecture documents (see repository root), governed
by `QENKI_MIND_GOVERNANCE_RULES_v1.md`.

## Meta-Model Contract
`META_MODEL.md` defines the architectural laws governing how the meta-model evolves.

## Primitive Vocabulary
`PRIMITIVE_VOCABULARY.md` defines the universal language primitives.

## Domain Vocabulary
`VOCABULARY.md` defines Qenki-specific domain concepts built from primitive vocabulary.

## Model Schema
`MODEL_SCHEMA.md` defines semantic models that operate on the shared domain vocabulary.

## Model Registry
`MODEL_REGISTRY.md` maps model names to domain vocabulary terms without semantic logic.

## Artifact Profiles
`ARTIFACT_PROFILE_REGISTRY.md` defines reusable model-composition profiles for artifact types.

## Artifact Type Registry
`ARTIFACT_TYPE_REGISTRY.md` maps artifact types to artifact profiles.

## ADR History
`ADR/` contains the repository's Architectural Decision Records.
`ADR/absorption-backups/` contains historical snapshots created during
canonical absorption.

## Proposed Topology Changes
No new repository category is canonical merely because an ADR is proposed. Proposed domains remain non-materialized until the corresponding ADR is accepted and absorbed into the canonical architecture.

## Reasoning Parameters
`REASONING_PARAMETERS/` contains Qenki-Mind's own tunable reasoning
parameters, owned by their respective organs.

## World State
`WORLD_STATE/` contains Qenki-Mind's current synthesized understanding of
its external environment.

## Maintenance
This document is updated only when repository organization changes —
categories are added, removed, renamed, or reorganized. Additions,
removals, renames, version changes, or status changes of files within an
existing category do not require updating this document.

## Validation Protocol
`VALIDATION_PROTOCOL.md` is the experimental protocol for attempting to refute the meta-model, not part of the meta-model itself.

## Investigation Log
`META_MODEL_INVESTIGATION.md` records inconclusive experiments: cases that neither validate nor refute the meta-model due to experimental limitations.

## Freeze Declaration
`FREEZE_DECLARATION.md` marks the official freeze of the standard (v1.0.0) and the start of the Evidence Phase.

## Proposal Registry
`PROPOSAL_REGISTRY.md` implements a cooling-off period for improvement ideas before they can affect the frozen standard.

## Architectural Note
`ARCHITECTURAL_NOTE_DESIGN_SPACE.md` is a non-normative observation on what was actually frozen: the design space, not just the model.

## Derived Specification
`ARTIFACT_BASE_CONTRACT_DERIVED_SPEC.md` is a non-normative, mechanically derivable specification of the Artifact base contract. It introduces no new semantics.

## Archive
`_archive/` contains superseded legacy documents (ARTIFACT_CAPABILITIES.md, ARTIFACT_CATALOG.md, ARTIFACT_MODELS.md, ARTIFACT_META_MODEL.md, ARTIFACT_SCHEMA.md), retained for history but not part of the frozen standard.
