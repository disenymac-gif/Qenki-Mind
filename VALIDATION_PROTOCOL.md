# Validation Protocol

## Purpose
This is not part of the meta-model. It is the experimental protocol used to generate empirical evidence about the meta-model's stability. The objective is not to demonstrate that the meta-model works, but to attempt to refute it as aggressively as possible.

## Level 1: Normal Cases
Examples: simple ADR, simple Specification, simple Runbook.
Objective: verify baseline functioning.

## Level 2: Complex Cases
Examples: multiple dependencies, reused profiles, cross-references, versioning, full lifecycle transitions.
Objective: search for friction.

## Level 3: Hostile Cases
Deliberately designed to break the system. Examples:
- an artifact that appears to require two profiles
- a concept that appears to belong to two models
- a Specification that reuses most of the ontology
- a Canon with multiple layers of dependency
- an ADR that references another ADR which redefines a Policy
Objective: find a refutation.

## Level 4: Heterogeneous Engines
The same artifact is interpreted, without additional instructions, by multiple independent engines (e.g. Claude, ChatGPT, a local engine, future engines).
Objective: test Semantic Equivalence. If independent engines converge on the same semantic representation, the validation carries substantially more weight.

## Metric Naming
Validation attempts are recorded as Attempted Refutations, not as passive validations, to keep the team oriented toward actively searching for failure rather than confirmation.

## Reporting Format
Attempted Refutations: N
Confirmed Refutations: n
Successful Resistance: N - n

These figures feed directly into META_MODEL_VALIDATION.md and META_MODEL_CHANGELOG.md.

## Change Discipline
No new axiom, derived property, or verification rule may be proposed unless it is justified by a specific failed refutation attempt with a corresponding entry in META_MODEL_CHANGELOG.md. Ideas without a documented empirical case are not sufficient grounds for modifying META_MODEL.md.

## Level 5: Reduction Test
Distinct from the earlier levels, this level does not test whether the meta-model is sufficient. It tests whether it is unnecessarily strong.

Procedure: temporarily remove one element of the meta-model (a Model, a merged pair of Artifact Profiles, a Domain Vocabulary concept, a simplified axiom, or even a derived property) and check whether the remaining system can still represent all known artifacts without loss of expressiveness, verifiability, or closure.

### Irreducibility Criterion
An element is considered irreducible only when no restructuring of upper layers permits its elimination without violating a meta-model axiom. Breaking artifacts on removal is not sufficient evidence of necessity: it may only reflect an accidental dependency of the current implementation, not an architectural requirement.

### Three Possible Outcomes
Instead of a binary resist/fail result, each Reduction Test attempt must be classified into one of three outcomes:

| Outcome | Meaning |
|---|---|
| Reducible | The element can be removed outright. |
| Refactorizable | The element can be removed after reorganizing upper layers, without modifying the meta-model itself. |
| Irreducible | No reorganization removes it without violating an axiom. |

A Refactorizable outcome is not a refutation of the meta-model. It is an implementation improvement: the element was not necessary, but was misplaced.

This test is the inverse of the Minimal Meta-Model Principle (Section 2 of META_MODEL.md): that axiom prevents adding what already can be expressed; the Reduction Test prevents keeping what removal does not truly require. Together they create constant pressure toward simplicity.

### Two Kinds of Minimality
- Theoretical Minimality: the smallest set of concepts necessary to represent the domain.
- Operational Minimality: the smallest set that remains maintainable, readable, and governable by both humans and engines.

These do not always coincide. A design can be theoretically minimal yet operationally difficult to use. Because Qenki OS is consumed by both humans and multiple engines, Operational Minimality carries equal weight to Theoretical Minimality.

### Architectural Minimality
Not a claim that the design is small, but that it has survived deliberate, repeated attempts to simplify it, while remaining evaluated against both Theoretical and Operational Minimality. This property emerges only from accumulated Reduction Test results, and is never asserted a priori.

### Reporting
Each Reduction Test attempt should record:
- element removed
- artifacts re-evaluated
- restructuring attempted, if any
- outcome (Reducible / Refactorizable / Irreducible)
- impact on Theoretical Minimality and Operational Minimality
- conclusion

Reducible and Refactorizable outcomes feed into META_MODEL_VALIDATION.md as implementation improvements. Irreducible outcomes with a documented Refutation feed into META_MODEL_CHANGELOG.md as confirmed necessity.


## Transversal Dimension: Dataset Diversity
This is not an additional hostility level but a cross-cutting classification applied to every attempted refutation at every level. Its purpose is to counter validation bias: a protocol built only on artifacts created for Qenki OS can only demonstrate stability for Qenki OS, not for the broader class of documentary knowledge systems it claims to generalize over.

Each artifact used in a Reduction, Validation, or Refutation attempt must be tagged with its origin:
- Native: created for Qenki OS.
- Imported: adapted from another system.
- Blind: produced by a third party with no knowledge of the meta-model.
- Synthetic: deliberately generated to stress the system.

A meaningful Stability Index should be reported per origin category, not only in aggregate, since aggregate numbers dominated by Native artifacts overstate generality.

## Negative Controls
Attempting only cases that should succeed measures sensitivity, not specificity. Negative controls are artifacts deliberately constructed to be invalid; the meta-model is expected to reject them.

Examples of required negative controls:
- an artifact deliberately misclassified into the wrong layer
- a document assigned two semantic owners
- a circular Artifact Profile
- an Artifact Type with no Profile
- an artifact with impossible dependencies

The expected result is rejection. If the system accepts a negative control, the problem is excess permissiveness, not insufficient expressiveness, and this itself constitutes a Refutation Condition (an ambiguity that Verification failed to catch).

## Discriminative Power Metrics
Alongside the Stability Index, the protocol must track:
- Accepted valid artifacts
- Rejected invalid artifacts
- False acceptances (invalid artifacts wrongly accepted)
- False rejections (valid artifacts wrongly rejected)

A system that is stable only because it never rejects anything is not evidence of a good meta-model; it is evidence of excessive permissiveness. False acceptances should be treated as Confirmed Refutations and logged in META_MODEL_CHANGELOG.md.


## Epistemic Outcomes
Every attempted refutation, at any level or dimension, must resolve into exactly one of three epistemic states:

| Outcome | Meaning | Registry |
|---|---|---|
| PASS | The meta-model resisted the attempt. | META_MODEL_VALIDATION.md |
| FAIL | The meta-model was refuted. | META_MODEL_CHANGELOG.md |
| INCONCLUSIVE | The experiment cannot support a conclusion (incomplete artifact, non-compliant engine, undocumented external ontology, lossy translation, defective implementation). | META_MODEL_INVESTIGATION.md |

An inconclusive result is neither positive nor negative evidence. It must never be forced into PASS or FAIL to avoid diluting the meaning of the other two registries.

## Evidence Coverage
Stability, Refutation Rate, and Discriminative Power describe outcomes, not the breadth of exploration behind them. Evidence Coverage measures how much of the problem space has actually been exercised:

Coverage is a function of:
- Artifact Types exercised
- Artifact Profiles exercised
- Models exercised
- Dataset Diversity categories exercised
- Engines exercised

No single formula is prescribed; the purpose is qualitative context, not a precise score. A report should always accompany raw counts (e.g. "1000 validations") with the coverage behind them (e.g. "8 Artifact Types, 6 Profiles, all Models, 4 engines, 4 Dataset Diversity categories"), since low-coverage aggregates overstate the strength of the evidence.


## Protocol Stability Rule
This addresses a specific risk: the experimental protocol itself could drift over time, undermining the evidentiary chain it is meant to produce.

Any modification to VALIDATION_PROTOCOL.md must be justified exclusively by evidence obtained through a registered case in META_MODEL_INVESTIGATION.md or a confirmed refutation in META_MODEL_CHANGELOG.md. The protocol may never be modified to accommodate a single unexpected result, nor to make a specific experiment pass. This subjects the protocol itself to the same evidentiary discipline it imposes on the meta-model, preventing infinite regress: the protocol audits the meta-model, and documented evidence audits the protocol.

## Depth and Breadth
Evidence Coverage (breadth) describes how much of the problem space has been explored, but it must always be reported alongside Depth: the number of repeated attempts on the same combination of Artifact Type, Profile, Model, engine, and Dataset Diversity category.

- Depth measures repeatability: statistical confidence within a single combination.
- Breadth measures generalization: diversity across the explored space.

500 attempts concentrated on a single ADR type is strong depth but weak breadth. 80 attempts distributed across all Types, Profiles, Models, engines, and origin categories is weaker depth but strong breadth. Any conclusion about stability must report both axes together; neither alone is sufficient evidence.
