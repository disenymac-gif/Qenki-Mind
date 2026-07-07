# Artifact Schema

## Purpose
Defines the minimum contract that makes an object a valid artifact in the Qenki ecosystem. This schema is intentionally neutral: it does not define governance, standards, or any Qenki-specific taxonomy. It defines structure, not policy.

## Base Artifact Contract
- id
- title
- owner
- domain
- type
- object
- authority
- stability
- lifecycle
- dependencies
- metadata
- machine_contract

## Machine Contract
Declares how machine-readable the artifact is:
- structured
- partially_structured
- human_readable_only

## Validation
An artifact is valid only if it satisfies the base contract and any additional constraints imposed by its declared type.

## Specialization
Artifact types specialize this schema by declaring required fields, allowed values, and additional constraints.
