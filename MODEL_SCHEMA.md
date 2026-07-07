# Model Schema

## Purpose
Defines a semantic model that operates on the shared Domain Vocabulary.

## Contract
- id
- name
- uses
- rules
- validators
- queries
- engine_hooks

## Model Semantics
A model declares which domain vocabulary terms it uses and how it applies them.

## Validation Principle
A model is valid when it can operate on domain vocabulary without redefining primitives.
