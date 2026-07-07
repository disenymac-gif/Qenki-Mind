# Meta-Model Contract

## 1. Purpose
Defines the architectural laws that govern how the Qenki meta-model evolves. This is not another semantic layer; it is the governing contract for change across the existing layers.

## 2. Axioms

### Layer Independence
Each layer may depend only on the immediately lower layer. No upward or lateral semantic dependency is allowed.

### Single Semantic Authority
Every concept has exactly one authoritative owner in exactly one layer. No concept may be defined twice.

### Extension over Modification
The meta-model should grow primarily by adding new instances to existing layers rather than modifying lower layers. Changes to lower layers require stronger justification than changes to higher layers.

### Downward Expressibility
Every concept in a layer must be fully expressible using the immediately lower layer. If it cannot be expressed downward, it belongs elsewhere.

### Stability Gradient
Lower layers are expected to change far less often than higher layers. Primitive Vocabulary should be nearly immutable; Artifacts are expected to change continuously.

### Minimal Meta-Model Principle
No element may be added to the meta-model if it can be fully expressed using existing elements. This is an ontological economy rule, not an organizational one:
- do not create a Primitive if existing primitives can express it
- do not create a Domain Vocabulary term if it is a composition of existing terms
- do not create a Model if a Profile suffices
- do not create a Profile if a Type suffices
- do not create a Type if an instance suffices

This axiom acts as a permanent brake against conceptual inflation.

## 3. Derived Properties
These properties are logical consequences of the axioms above, not independent design decisions.

### Semantic Closure
Derived from Downward Expressibility + Layer Independence.
All meaning must be traceable to Primitive Vocabulary. No meaning may originate outside this chain.

### Structural Closure
Derived from Downward Expressibility + Layer Independence.
All structure must be traceable to Artifact. No structure may exist outside this chain.

## 4. Verification

### Stability Test
Derived from Extension over Modification + Single Semantic Authority.
A future change should fall unambiguously into one of these cases:
- Add a Primitive Vocabulary instance
- Add a Domain Vocabulary instance
- Add a Model
- Add an Artifact Profile
- Add an Artifact Type
- Add an Artifact

If a change cannot be classified into one of these categories, the meta-model requires review.

### Closure Test
Derived from Semantic Closure + Structural Closure.
An artifact is valid only if it can be traced completely downward and upward without leaving the meta-model.

Downward traversal:
Artifact -> Artifact Type -> Artifact Profile -> Model -> Domain Vocabulary -> Primitive Vocabulary

Upward traversal:
Primitive Vocabulary -> Domain Vocabulary -> Model -> Artifact Profile -> Artifact Type -> Artifact

If any step introduces an external concept, an implicit rule, or an undeclared dependency, the artifact is not closed.

## 5. Evolution Rules
- Modifications to this document require empirical evidence from real artifact modeling, not new abstractions.
- A new concept is placed at the first layer, from the bottom up, where it can no longer be expressed by the layer below.
- Any proposed new layer, registry, or abstraction must be justified by a concrete case that violates Stability Test or Closure Test.
- This document is considered mature when future changes originate only from empirical contradictions found while modeling real artifacts.

## 6. Refutation
Refutation is the logical counterpart to Verification. Verification defines acceptance criteria; Refutation defines falsification criteria.

### Refutation Conditions
The meta-model must be revised only if one of the following occurs:
- A concept cannot be classified into any existing layer without violating an axiom.
- A concept requires two semantic owners, violating Single Semantic Authority.
- An artifact fails the Closure Test without introducing implicit semantics or structure.
- A legitimate change repeatedly requires modifying lower layers instead of extending upper layers, indicating the stratification itself is wrong.
- Two independent engines produce incompatible interpretations of the same artifact using exactly the same meta-model, revealing formal ambiguity rather than an implementation defect.

### Status
The meta-model is considered valid as long as no Refutation Condition has occurred. It is not "true," it is "unrefuted."

## 7. Meta-Model Status
This meta-model is considered feature complete. Future modifications are not expected to introduce new conceptual capabilities, but only to resolve empirically demonstrated refutations documented in META_MODEL_CHANGELOG.md.

"Feature complete" is a deliberately conservative status: it does not claim the design is frozen or perfect, only that no further conceptual capabilities are expected. Legitimate refutations may still occur; when they do, they are resolved through disciplined, documented change, not treated as evidence of a flawed design.

## 8. Scope and Semantic Neutrality
The meta-model does not evaluate whether a decision, policy, or process is correct. It evaluates only whether the artifact representing that decision is classifiable, traceable, consistent, verifiable, and expressible within the system.

An ADR may defend a poor architectural decision, a Policy may be misguided, a Runbook may describe an inefficient process, a Specification may define an inelegant API — and each can still be a perfectly valid artifact under this meta-model.

This preserves a strict separation of responsibilities:
- Representational correctness: the responsibility of this meta-model.
- Domain correctness: the responsibility of domain experts and governance processes, never of this meta-model.

### Semantic Neutrality
The meta-model is agnostic to the content it represents. It never requires content to be true, correct, or optimal. Mixing domain judgment into the meta-model would compromise its generality.

### Summary Statement
Qenki OS Meta-Model is a domain-neutral, self-governing knowledge representation framework whose evolution is driven exclusively by documented empirical refutation rather than theoretical refinement.

## 9. Standard Status
From this point, META_MODEL.md is treated as a published standard, not a document under active improvement. It is opened for modification only when a real, documented, reproducible case demonstrates a violation of its own Refutation Conditions (Section 6), with a corresponding entry in META_MODEL_CHANGELOG.md.
