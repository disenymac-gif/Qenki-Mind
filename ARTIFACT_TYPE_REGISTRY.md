# Artifact Type Registry

## Purpose
Maps concrete artifact types to artifact profiles. Artifact types define identity; profiles define reusable model composition.

## Layering Rule
Each layer may only use elements from the layer immediately below it. Artifact types use profiles. Profiles use models. Models use domain vocabulary. Domain vocabulary uses primitive vocabulary.

## Entries
- ADR: GovernanceDocument
- Registry: OperationalDocument
- Standard: NormativeDocument
- Policy: GovernanceDocument
- Specification: GovernanceDocument
- Runbook: OperationalDocument
- Architecture: GovernanceDocument
- Canon: GovernanceDocument

## Machine Contract Declaration (merged from legacy ARTIFACT_CATALOG.md)
Each Artifact Type should declare its machine readability level:
- structured
- partially_structured
- human_readable_only

This declaration is an Attribute of the artifact, constrained to one of the three enumerated values; it does not introduce a new Domain Vocabulary term.
