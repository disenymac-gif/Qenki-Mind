# Artifact Capabilities

## Purpose
Defines optional capability modules that can be composed onto an artifact type. Capabilities are separate from the base schema and should only be attached when required.

## Current Capabilities
- Governance
- Lifecycle
- Automation
- Dependency

## Capability Semantics
- Governance: authority, ownership, decision rights
- Lifecycle: state transitions, versioning, retirement
- Automation: machine_contract, executable actions, validation hooks
- Dependency: dependency graph, required artifacts, ordering

## Composition Rule
Artifact types are composed from the base schema plus zero or more capabilities. Capabilities are explicit and additive; they must not be silently embedded into the base schema.
