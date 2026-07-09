# Summary: Fix Plugin Install Button

## What was achieved

The mad-plug repository was restructured to follow the plugin directory pattern
used by working Copilot app plugins (awesome-copilot, copilot-plugins).

### Root cause
SKILL.md files were placed directly in top-level directories. The Copilot app's
install mechanism expects: `<plugin>/skills/<skill-name>/SKILL.md` with an
optional `plugin.json` manifest.

### Changes made
- Moved each SKILL.md into `skills/<name>/SKILL.md` within its plugin directory
- Added `plugin.json` with name, description, version, and skills path to each plugin
- Moved root SKILL.md into its own `cog253-unified-skill-lattice/` plugin directory
- Removed duplicate `egreglyphic-telomorph/SKILL_1.md`

### Plugins now available (8 total)
1. autognosis
2. cragbase
3. deep-tree-echo-core-self
4. egreglyphic-telomorph
5. metamathematical-consciousness
6. neuro
7. zpp-form-spec
8. cog253-unified-skill-lattice

## Iteration history
- Iteration 1: PASS (single iteration, structural fix)

## Recommendations
- User should refresh the Copilot app plugin list to verify Install buttons now work
- Consider if the `skills/archive/` directory (53 old skill files) should be cleaned up
- The Dependabot PR dependency bumps are unrelated to the install issue
