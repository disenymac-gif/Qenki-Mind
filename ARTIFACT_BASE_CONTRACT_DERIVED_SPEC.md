# Artifact Base Contract — Derived Specification

## Status
Derived Specification (Non-Normative)

This document is mechanically derivable from the frozen v1.0 standard (PRIMITIVE_VOCABULARY.md, VOCABULARY.md, MODEL_REGISTRY.md, ARTIFACT_PROFILE_REGISTRY.md, ARTIFACT_TYPE_REGISTRY.md). It introduces no additional semantics, concepts, rules, or governance authority. It exists purely to make an already-implicit composition explicit and convenient for engines and tooling to consume.

## Purpose
Shows how the base structural fields of a concrete Artifact instance materialize from composing existing normative concepts. This is analogous to an API generated automatically from a schema: it does not change the schema, but it makes consumption easier.

## Base Artifact Fields and Their Derivation

| Field | Derived From |
|---|---|
| id | Identifier (Primitive Vocabulary) |
| title | Attribute (Primitive Vocabulary) |
| owner | Owner (Domain Vocabulary) = Entity + Relationship |
| domain | Attribute (Primitive Vocabulary) |
| type | Type (Primitive Vocabulary); references the Artifact Type layer |
| object | Attribute (Primitive Vocabulary) |
| authority | Authority (Domain Vocabulary) = Relationship |
| stability | Attribute / State (Primitive Vocabulary) |
| lifecycle | Lifecycle State (Domain Vocabulary) = State |
| dependencies | Dependency (Domain Vocabulary) = Relationship |
| metadata | Attribute (Primitive Vocabulary) |
| machine_contract | Attribute + Constraint (Primitive Vocabulary): an Attribute whose value is constrained to {structured, partially_structured, human_readable_only} |

## Validation Note
All fields above are derivable without exception from the normative standard. No field required introducing a new concept, layer, or semantic authority. See META_MODEL_VALIDATION.md for the corresponding PASS entry.

## Non-Normative Notice
This document must never be treated as a source of new rules, axioms, or vocabulary. Any apparent gap or ambiguity encountered while using this document must be resolved by tracing back to the normative documents listed in FREEZE_DECLARATION.md, never by editing this specification directly with new semantics.
