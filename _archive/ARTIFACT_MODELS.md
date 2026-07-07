# Applied Models

## Purpose
Defines the reusable semantic models that can be applied to artifact types. Models add meaning, validation, and behavior to artifacts without becoming part of the base schema.

## Current Models
- Governance Model
- Lifecycle Model
- Dependency Model
- Automation Model

## Model Creation Criteria
A new transversal model should be created only if it: applies to multiple artifact types, has its own rules and validations, evolves independently, and can be consumed uniformly by tools or agents. If it does not meet those criteria, it belongs inside an existing model or remains a type-local rule.

## Model Boundary
Models define coherent semantics. They do not define the base artifact structure and they do not enumerate implementation details.
