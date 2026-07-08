# Goal: Unify cog253-main structure and merge SKILL_n files via pattern-language topology

## User Request

Reorganize `cog253-main` for optimal cognitive grip & merge disparate `SKILL_{{n}}.md` into a single cohesive definition with references.

## Refined Goal

Create a unified navigational structure that uses the 253-pattern topology from Christopher Alexander's "A Pattern Language" as the organizing skeleton for both:
1. The `cog253-main/` directory itself (decluttering root, establishing clear entry points and hierarchy)
2. The 53 `SKILL_n.md` files scattered at the `1ski/` root (merging them into a single cohesive document where each skill is positioned within the pattern lattice based on conceptual affinity)

The deliverable is a **single unified SKILL.md** that IS the reorganization — it maps skills to pattern positions, provides cross-references into cog253-main, and serves as the cognitive entry point for the entire system. Complementary: a simplified directory structure for `cog253-main/` with a clear README that points into the unified map.

The structure should be optimized for **AI agent consumption** — maximizing an LLM's ability to quickly locate relevant capabilities, understand relationships, and navigate the full pattern-skill lattice.

## Acceptance Criteria

- [ ] AC1: A single `SKILL.md` exists at `1ski/` root that contains all 53 skills organized by pattern-language topology (categories: Towns/1-94, Buildings/95-204, Construction/205-253)
- [ ] AC2: Each skill entry in the unified doc includes: name, one-line description, pattern affinity (which APL pattern(s) it maps to), and a reference path to its detailed content
- [ ] AC3: `cog253-main/` root has ≤15 non-directory items (currently ~40+ files) — generated artifacts, summaries, and scripts moved into appropriate subdirectories
- [ ] AC4: `cog253-main/README.md` is rewritten as a concise entry-point document (<100 lines) that orients a reader and links to the unified SKILL.md
- [ ] AC5: The unified SKILL.md provides at least 3 navigational affordances: (a) pattern-topology ordering, (b) skill-name alphabetical index, (c) domain/theme clusters
- [ ] AC6: No content is lost — original SKILL_n.md files are preserved (moved, not deleted) and referenced from the unified document
- [ ] AC7: Cross-references work: pattern IDs mentioned in SKILL.md link to the correct markdown files in `cog253-main/markdown/apl/`

## Scope Boundaries

**In scope:**
- Reorganizing `cog253-main/` directory structure (moving files, not modifying their content)
- Creating the unified `SKILL.md` with pattern-topology organization
- Rewriting `cog253-main/README.md` as a concise entry point
- Moving original `SKILL_n.md` files into an archive/reference directory
- Creating an alphabetical index and domain-cluster views within SKILL.md

**Out of scope:**
- Modifying the content of individual pattern files (markdown/apl/*, markdown/uia/*, etc.)
- Changing Python scripts or JSON schemas
- Modifying `.github/agents/` persona files
- Creating new patterns or skills
- Changing the `apl/` raw HTML source files
- Modifying subdirectories of `1ski/` other than `cog253-main/` (e.g., `neuro/`, `AUTOGNOSIS/`, etc.)

## Applicable Project Conventions

**Quality gate command:**
- None discovered (no test runner, linter, or preflight defined at workspace level)

**Commit convention:**
- Not a git repository — no commits. Changes are direct file operations.

**Guidelines:**
- `cog253-main/CLAUDE.md` — project overview and conventions
- `cog253-main/docs/architecture_overview.md` — system architecture

**Rules:**
- Pattern IDs: APL patterns are `apl1`-`apl253`; UIA patterns are numeric IDs like `12610010`
- Placeholder syntax: `{{placeholder-name}}`
- Domain dimensions: Physical, Social, Conceptual, Psychic (+ Interpersonal, Archetypal)
- Categories: cat1=Towns(1-94), cat2=Buildings(95-204), cat3=Construction(205-253)

## Context for Builder

### Current State

**`1ski/` root** contains 53 files named `SKILL_0.md` through `SKILL_52.md` plus a `SKILL.md.original`. Each has YAML frontmatter with `name:` and `description:` fields. The skills span domains including:
- Neural architecture theory (gauge-hypergraph-network, hypergauge-orbifold, promise-lambda-attention)
- Reservoir/echo-state computing (harmonic-resonance-esn, reservoirpy-nodes, time-crystal-*)
- Pattern languages (apl253, gh253, magic-patterns, cogsim-pml)
- Agent systems (agent-toga, agent-zero, vorticog)
- Infrastructure (plan9-*, inferno-devcontainer, koboldcpp, llama-cpp-spec)
- Meta/transforms (function-creator, general-relevance-transform, skill-infinity, topology-weaver)
- Domain-specific tools (multiplatform-api-weaver, skinform, regimorg, dgen)

**`cog253-main/`** root has ~40+ files including multiple `*_SUMMARY.md`, `*_README.md`, Python scripts, JSON data files, images, and shell scripts alongside the actual directory structure.

### Pattern-Skill Mapping Heuristic

Use the APL pattern categories as the primary axis:
- **Towns (1-94)**: Skills operating at system/ecosystem scale — orchestration, platform design, multi-agent coordination
- **Buildings (95-204)**: Skills operating at component/module scale — specific architectures, frameworks, application domains
- **Construction (205-253)**: Skills operating at implementation/material scale — specific implementations, node types, optimization techniques

Within each category, identify the most relevant pattern(s) for each skill based on conceptual resonance (e.g., skill `topology-weaver` → Pattern 52 NETWORK OF PATHS; skill `agent-zero` → Pattern 12 COMMUNITY OF 7000).

### Directory Reorganization Plan for cog253-main

Move root clutter into:
- `cog253-main/generated/` — all `*_SUMMARY.md`, `*_COMPLETE.md`, analysis reports
- `cog253-main/scripts/` — all `.py` and `.sh` files
- `cog253-main/schemas/` — all `.json` files
- `cog253-main/assets/` — all `.png` images

Keep at root only: `README.md`, `CLAUDE.md`, `LICENSE`, `.gitignore`, `.github/`
