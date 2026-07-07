# Artifact Profile Registry

## Purpose
Declarative registry of artifact profiles. A profile defines a reusable composition of models. Artifact types reference profiles instead of repeating model composition.

## Profiles
- GovernanceDocument: Governance, Lifecycle, Dependency
- OperationalDocument: Lifecycle, Automation, Dependency
- NormativeDocument: Governance, Lifecycle

## Rule
Profiles contain only reusable model composition. They do not redefine model semantics or artifact identity.

## Model Semantic Glosses (merged from legacy ARTIFACT_CAPABILITIES.md)
- Governance: authority, ownership, decision rights
- Lifecycle: state transitions, versioning, retirement
- Automation: machine_contract, executable actions, validation hooks
- Dependency: dependency graph, required artifacts, ordering

## Anti-Pattern Warning (merged from legacy ARTIFACT_CAPABILITIES.md)
Profiles are explicit and additive. Model composition must never be silently embedded into an Artifact Type or into the base Artifact structure; it must always be declared through a named Profile.
