# Goal: Fix Plugin Install Button in GitHub Copilot App

## User Request

The "Install" button for mad-plug plugins in the GitHub Copilot desktop app does nothing when clicked. The plugins appear in the list (pattern-navigator, skill-composer, template-generator, dsl-factory, cognitive-kernel, formulation-analyzer) but cannot be installed.

## Refined Goal

Restructure the mad-plug repository so that its skills follow the directory pattern expected by the GitHub Copilot desktop app's plugin installation mechanism. Working plugins (awesome-copilot, copilot-plugins) use either a `plugin.json` manifest pointing to a `skills/` directory, or organize skills as `skills/<name>/SKILL.md`. The mad-plug repo currently has SKILL.md files scattered in top-level directories without the required nesting. Fix the structure so the Install button functions correctly.

## Acceptance Criteria

- [ ] Each plugin/skill directory follows the pattern: `<plugin>/skills/<skill-name>/SKILL.md`
- [ ] OR each plugin has a `plugin.json` with a `"skills"` field pointing to the skills directory
- [ ] The root SKILL.md (cog253-unified-skill-lattice) is properly accessible as an installable skill
- [ ] All existing SKILL.md content is preserved (no skill definitions lost)
- [ ] The Install button in the Copilot app works after the restructure (user verifies)

## Scope Boundaries

**In scope:**
- Restructuring skill files into proper plugin directory pattern
- Adding plugin.json manifests where needed
- Preserving all skill content

**Out of scope:**
- Rewriting skill content or instructions
- Fixing the cragbase/cragbase app dependencies (separate Dependabot PR)
- Modifying the Copilot app itself

## Applicable Project Conventions

**Quality gate command:**
- No formal quality gate discovered (no preflight/check/lint/test for the plugin structure)

**Commit convention:**
- Conventional commits (default)
- Assisted-by trailer required: `Assisted-by: Claude:Sonnet-4.6`

**Guidelines:**
- copilot-setup-steps.yml exists at `.github/workflows/`

**Rules:**
- None discovered (no AGENTS.md or CONSTITUTION.md)
