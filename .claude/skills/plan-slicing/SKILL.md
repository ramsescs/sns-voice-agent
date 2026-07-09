---
name: plan-slicing
description: Break a single implementation plan into independent, separately-testable vertical slices and write each as a local markdown file in issues/. Use when the user wants to turn an implementation plan into a list of concrete, independently-workable tasks.
---

# Implementation Plan to Slices

Break a single implementation plan into independently-workable **slices**, each written as a local markdown file in `issues/`.

Two properties define every slice — they come straight from what a slice is *for*, and everything below is in service of them:

1. **Independently implementable** — a slice can be built and merged on its own, without first completing other slices' work beyond its declared prerequisites.
2. **Independently testable** — a slice ships with a way to verify it in isolation (a test, a runnable demo, a check). A slice is "done" only when that verification passes.

## Process

### 1. Locate the implementation plan

This skill takes exactly one input: an implementation plan (e.g. `MVP_PLAN.md`, `PLAN.md`, or the build-out section of a design doc).

Ask the user for the plan's file path if you don't already have it. If it isn't in your context, read it.

There is no separate PRD or requirements document in this workflow — the implementation plan is the sole source of truth.

### 2. Explore the codebase (optional)

If you have not already explored the codebase, do so to understand the current state of the code and what each part of the plan will touch.

### 3. Draft the slices

Carve the plan into slices. A slice is a **usable or verifiable increment**, never a dangling half-component.

"Vertical" here means *defined by outcome*, not by touching a fixed set of layers. Depending on the project, a slice's end-to-end path might run through a schema, an API, and a UI — or it might be a single pure function plus its test suite. Both are valid, as long as the slice is independently implementable and independently testable.

<slice-rules>
- The acceptance bar for every slice is **independently implementable** AND **independently testable** — not aspirations, requirements.
- A slice leaves the system in a working, verifiable state. It is a complete increment, never a half-built layer.
- Plans are usually organized by component or by phase (often one section per file/module). Do NOT mirror that structure 1:1 — copying it tends to produce horizontal slivers (e.g. "write all the schemas") that cannot be verified on their own. Re-slice so each unit can stand and be tested alone.
- "Independent" means self-contained as a unit of work, NOT free of ordering. Slices may depend on earlier slices (see "Blocked by") — real plans have prerequisites (a contract must exist before the code that consumes it).
- Prefer many thin slices over few thick ones.
</slice-rules>

Slices may be 'HITL' or 'AFK'. HITL slices require human interaction, such as an architectural decision or a design review. AFK slices can be implemented and merged without human interaction. Prefer AFK over HITL where possible.

### 4. Quiz the user

Present the proposed breakdown as a numbered list. For each slice, show:

- **Title**: short descriptive name
- **Type**: HITL / AFK
- **Blocked by**: which other slices (if any) must complete first
- **Plan sections covered**: which parts of the implementation plan this slice delivers
- **Independent test**: the one-line description of how this slice is verified on its own

Ask the user:

- Does the granularity feel right? (too coarse / too fine)
- Is each slice genuinely independently testable as described?
- Are the dependency relationships correct?
- Should any slices be merged or split further?
- Are the correct slices marked as HITL and AFK?

Iterate until the user approves the breakdown.

### 5. Create the slice files

For each approved slice, write a markdown file in `issues/` using the naming pattern `issues/NNN-short-title.md` (e.g. `issues/001-set-engine.md`).

Number files starting from the next available number (check what files already exist in `issues/`).

Create files in dependency order (blockers first) so you can reference real filenames in the "Blocked by" field.

Do NOT use `gh issue create` or any GitHub CLI commands. Do NOT reference GitHub issue numbers. Use local filenames for all cross-references.

<slice-template>
## Source plan

`MVP_PLAN.md` (or whichever implementation plan was used)

## What to build

A concise description of this slice as an end-to-end outcome, not a layer-by-layer implementation. Reference specific sections of the source plan rather than duplicating them.

## Acceptance criteria

- [ ] Criterion 1
- [ ] Criterion 2
- [ ] Criterion 3

## How to test independently

The concrete way to verify this slice on its own — the test(s) to run, the command to execute, or the demo to perform. This must be runnable without completing any slice not listed under "Blocked by". The slice is done when this passes.

## Blocked by

- Blocked by `issues/NNN-title.md` (if any)

Or "None - can start immediately" if no blockers.

## Plan sections covered

Reference the part(s) of the source implementation plan this slice delivers:

- "Key components → 3. set_engine.py"
- ...

</slice-template>

Do NOT modify the source implementation plan file.
