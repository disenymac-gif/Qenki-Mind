# World State

## Purpose
This domain holds Qenki-Mind's current synthesized understanding of its
external environment — the organism's maintained interpretation of the
world after reasoning, as distinct from its own architectural or
operational maturity (`MATURITY_STATUS.md`) and its own tunable
reasoning parameters (`REASONING_PARAMETERS/`).

This is not a store of raw external observations. Raw observations enter
and are interpreted through the cognitive flow governed by Perception and
Sense-Making, per canonical architecture. `WORLD_STATE/` holds only the
resulting synthesized state that the organism maintains and reasons from
afterward.

## Ownership
Owned by Qenki-Mind. Each world-state category has exactly one owning
organ, assigned by canonical architecture or an absorbed ADR, which is
solely responsible for maintaining that category's authoritative state.
Other organs may contribute information toward a category through the
cognitive process, per canonical architecture, but only the owning organ
may write the authoritative state itself.

## What Belongs Here
Only categories of synthesized external-environment state explicitly
identified by the canonical documents as owned by one of Qenki-Mind's
organs — for example, situational context relevant to active reasoning,
and ecosystem-observable conditions that inform Expressions or
Consequence matching.

## What Does Not Belong Here
This domain does not hold canonical architecture, tunable reasoning
parameters, self-referential maturity status, or raw unprocessed
observations. It does not contain algorithms or implementation logic —
only the current synthesized state itself and its canonical basis for
existing here.

## Document Structure
Every world-state category document follows this structure:
- Identity (name, owning organ)
- Owning Organ
- Canonical Basis
- Current State
- Change History
- Last Updated

## Lifecycle
Contents here change continuously as the organism synthesizes updated
understanding of its environment, without requiring architectural
review, as established in `QENKI_MIND_GOVERNANCE_RULES_v1.md`. Only the
existence and ownership of a world-state category is architectural; its
specific content is not.
