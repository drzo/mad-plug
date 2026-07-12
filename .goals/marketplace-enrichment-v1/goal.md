# Goal: Full Marketplace Enrichment — Structural + Depth + Discoverability

## User Request

Perform the next iteration of enrichment & refinement toward optimal cognitive grip as a plugin marketplace for the gh copilot app. Full structural + depth + discoverability pass across all 7 plugins.

## Refined Goal

Transform mad-plug from a working-but-minimal plugin collection into a well-structured, self-documenting marketplace with proper governance, rich plugin metadata, and discoverability infrastructure. Every plugin gets a README with examples, versioning, and dependency declarations. The repo gets an AGENTS.md defining marketplace conventions, a root SKILL.md entrypoint, consolidated marketplace.json (eliminating duplicates), plugin categorization/tagging, and a searchable index.

## Acceptance Criteria

- [ ] AC1: AGENTS.md exists at repo root defining marketplace conventions (plugin structure, naming, commit rules, quality expectations)
- [ ] AC2: Root SKILL.md exists and serves as a valid entrypoint (referenced by marketplace.json)
- [ ] AC3: marketplace.json is canonical — no conflicting duplicates (external.json and .github/plugin/marketplace.json either removed or symlinked/generated from root)
- [ ] AC4: All 7 plugins have enriched README.md with: description, usage examples, version field, dependency declarations, and category tags
- [ ] AC5: spark plugin is registered in marketplace.json alongside the existing 6
- [ ] AC6: Each plugin directory contains a plugin.json with structured metadata (name, version, description, category, tags, dependencies, tools list)
- [ ] AC7: A categories/tags taxonomy exists (e.g., in a marketplace-index.json or similar) enabling discovery by domain
- [ ] AC8: All existing extension.mjs files still function (no breaking changes to tool wiring)

## Scope Boundaries

**In scope:**
- Create AGENTS.md (marketplace conventions)
- Create root SKILL.md (entrypoint)
- Consolidate marketplace.json (single source of truth)
- Enrich all 7 plugins with README.md, plugin.json, version, dependencies, categories
- Register spark in marketplace.json
- Create marketplace-index.json (categories + tags for discoverability)
- Preserve all existing extension.mjs wiring

**Out of scope:**
- Restructuring or modifying the 53 archived skills (they stay in skills/archive/)
- Adding test/lint infrastructure (future iteration)
- Modifying extension.mjs tool handler logic
- Publishing to any external registry
- UI/web-based marketplace frontend

## Applicable Project Conventions

**Quality gate command:**
- None configured (no Makefile/justfile at root level)
- Validation: ensure marketplace.json is valid JSON, all plugin paths resolve

**Commit convention:**
- Conventional commits: `type(scope): [B/I] description`
- Title ≤72 characters, imperative mood
- Trailer: `Assisted-by: Claude:Sonnet-4.6`

**Guidelines:**
- No .agents/guidelines/ or .github/guidelines/ discovered

**Rules:**
- Plugin directories must contain: extension.mjs, plugin.md, plugin.json, README.md
- marketplace.json at root is the single source of truth
- Extensions re-export from plugins/ via .github/extensions/
