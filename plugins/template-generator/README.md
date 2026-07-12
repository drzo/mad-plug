# template-generator

Scaffold new Copilot skills and extensions from curated templates. Generates proper directory structure, frontmatter, placeholder content, and extension boilerplate in seconds.

**Version:** 0.1.0 | **Category:** Code Generation & Scaffolding | **Tags:** `scaffold` `template` `generator` `extension`

---

## Description

`template-generator` accelerates the creation of new skills and Copilot extensions by generating standardized scaffolds. Rather than copying files manually and editing placeholders, invoke a single tool and get a correctly structured project ready to fill in. Templates follow the conventions defined in [AGENTS.md](../../AGENTS.md).

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `template_new_skill` | Create a new skill with proper structure and frontmatter | `name` |
| `template_new_extension` | Scaffold a Copilot extension with standard layout | `name` |

### `template_new_skill` parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✓ | Skill name (kebab-case) |
| `description` | string | — | Short description for frontmatter |
| `output` | string | — | Output directory (default: `skills/`) |

### `template_new_extension` parameters

| Parameter | Type | Required | Description |
|---|---|---|---|
| `name` | string | ✓ | Extension name (kebab-case) |
| `description` | string | — | Short description for plugin.md |

---

## Usage Examples

### Create a new skill
```
template_new_skill(name="code-reviewer", description="Review pull requests for common issues")
```
Generates `skills/code-reviewer/` with `SKILL.md`, proper frontmatter, and placeholder sections.

### Scaffold with a custom output directory
```
template_new_skill(name="api-designer", description="Design REST APIs", output="plugins/my-plugin/skills")
```
Creates the skill inside a plugin's skills subdirectory.

### Scaffold a new Copilot extension
```
template_new_extension(name="my-plugin", description="Custom tooling for my workflow")
```
Generates `plugins/my-plugin/extension.mjs`, `plugin.md`, `plugin.json`, and `README.md` stubs.

---

## Dependencies

None

---

## Version

0.1.0

---

## Category & Tags

Category: `code-generation`

Tags: `scaffold` `template` `generator` `extension`

---

## Scripts

Shell scripts in `scripts/`:
- `new-skill.sh` — skill scaffold generator
- `new-extension.sh` — extension scaffold generator
