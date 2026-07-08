# Goal: Add Plugin Definitions to Marketplace

## Context
The `mad-plug` repository is a Copilot marketplace package with 53 skills but zero plugins.
The `marketplace.json` has `"plugins": []`. The repo contains rich tooling in `scripts/`,
`generators/`, and `templates/` that should be exposed as plugin capabilities.

## Acceptance Criteria

1. A `plugins/` directory exists at repo root with subdirectories for each plugin
2. Each plugin has a `plugin.md` definition file with frontmatter (name, description)
3. The `marketplace.json` `plugins` array is populated with entries referencing each plugin
4. Plugin entries follow the same format as skills: `{ "name", "path", "description" }`
5. Plugins logically group the repo's executable capabilities:
   - Pattern navigation (gh253 topology)
   - Skill composition/transformation
   - Template/project scaffolding
   - Language creation tools
   - Cognitive kernel operations
   - Formulation/analysis tools

## Scope Boundaries
- Do NOT modify existing skills or their content
- Do NOT restructure scripts/generators/templates directories
- Do NOT add external dependencies
- Plugin definitions are descriptive manifests, not runtime code

## Quality Gates
- `marketplace.json` must be valid JSON
- All `path` entries must point to existing files
- No duplicate plugin names

## Conventions
- No AGENTS.md or CONSTITUTION.md in this repo
- No Makefile/justfile/package.json quality gates
- Commit convention: conventional commits with Assisted-by trailer
