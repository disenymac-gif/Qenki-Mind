# Model Registry

## Purpose
Declarative registry of models and the domain vocabulary terms they use.

## Model Entries
- Governance: uses [Owner, Authority, Decision, Constraint, Rule, Validation, Reference]
- Lifecycle: uses [Lifecycle State, Version, Constraint, Rule, Validation, Reference]
- Dependency: uses [Dependency, Reference, Constraint, Validation, Relationship]
- Automation: uses [Entity, Relationship, Rule, Validation, Version, Reference]

## Registry Rule
The registry only maps model names to domain vocabulary terms. It contains no semantic logic.

## Model Creation Criteria (merged from legacy ARTIFACT_MODELS.md)
A new transversal Model should be created only if it:
- applies to multiple Artifact Types,
- has its own rules and validations,
- evolves independently,
- can be consumed uniformly by tools or agents.

If it does not meet these criteria, it belongs inside an existing Model or remains a Type-local rule, not a new Model.
