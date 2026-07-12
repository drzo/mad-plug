# AGENTS.md — mad-plug Marketplace Conventions

This document defines the conventions, structure requirements, naming rules, and quality
expectations for all plugins in the mad-plug marketplace.

---

## Plugin Directory Structure

Every plugin lives under `plugins/<plugin-name>/` and **must** contain:

```
plugins/<plugin-name>/
├── extension.mjs   # Copilot extension entry — registers tools via joinSession()
├── plugin.md       # Human-readable plugin description (short-form prose)
├── plugin.json     # Structured metadata (see schema below)
├── README.md       # Full documentation with examples
└── skills/         # (optional) Skill sub-directories for knowledge-based plugins
└── .github/        # (optional) Plugin-local GitHub config
```

The shared runtime helper lives at `plugins/_shared/procRunner.mjs` — import from there,
never copy it.

Extensions registered for auto-discovery are re-exported from `.github/extensions/` with
a single-line shim:

```js
// .github/extensions/<name>/extension.mjs
import "../../../plugins/<name>/extension.mjs";
```

---

## plugin.json Schema

```json
{
  "name": "kebab-case-name",
  "version": "MAJOR.MINOR.PATCH",
  "description": "One sentence, ≤120 chars, imperative mood.",
  "category": "one-of-the-defined-categories",
  "tags": ["tag1", "tag2"],
  "dependencies": [],
  "tools": ["tool_name_1", "tool_name_2"],
  "entrypoint": "extension.mjs"
}
```

**Required fields:** `name`, `version`, `description`, `category`, `entrypoint`.

---

## Naming Conventions

| Artifact | Convention | Example |
|---|---|---|
| Plugin directory | `kebab-case` | `pattern-navigator` |
| Tool names (in extension.mjs) | `snake_case` | `pattern_query` |
| marketplace.json `name` | `kebab-case` | `pattern-navigator` |
| plugin.json `name` | matches directory name | `pattern-navigator` |
| Tags | `kebab-case`, singular nouns preferred | `pattern`, `dsl` |
| Category IDs | `kebab-case` | `cognitive-computing` |

---

## Defined Categories

| ID | Name |
|---|---|
| `pattern-recognition` | Pattern Recognition & Navigation |
| `skill-engineering` | Skill Engineering |
| `code-generation` | Code Generation & Scaffolding |
| `language-design` | Language Design & DSLs |
| `cognitive-computing` | Cognitive Computing |
| `scientific-computing` | Scientific & Mathematical Computing |

---

## Commit Rules (Conventional Commits)

All commits to this repository follow the format:

```
type(scope): [B/I] description
```

- **type** — `feat`, `fix`, `docs`, `refactor`, `chore`, `test`
- **scope** — plugin name or `marketplace` for cross-cutting changes
- **[B]** — Breaking change; **[I]** — Iterative / non-breaking
- **description** — Imperative mood, ≤72 characters total for the title line

**Examples:**

```
feat(pattern-navigator): [I] add path traversal tool
docs(marketplace): [I] enrich all plugin READMEs
refactor(cognitive-kernel): [B] rename cogkernel_build parameters
```

**Required trailer** for AI-assisted commits:
```
Assisted-by: Claude:Sonnet-4.6
```

---

## Quality Expectations

### plugin.json
- `version` follows semantic versioning (`MAJOR.MINOR.PATCH`)
- `description` is a single sentence in imperative mood
- `tools` lists **all** tool names exposed by the extension
- `dependencies` lists other plugins this plugin requires (empty array if none)

### README.md
Must contain all of the following sections:
1. **Description** — what the plugin does
2. **Usage Examples** — at least 2 concrete invocation examples
3. **Tools** — table of all exposed tools with parameter descriptions
4. **Version** — current version number
5. **Dependencies** — other plugins required (or "None")
6. **Category & Tags** — discovery metadata

### extension.mjs
- Must call `joinSession({ tools: [...] })` from `@github/copilot-sdk/extension`
- All tool handlers must return a string
- Error handling must wrap every `runScript`/`runPython` call in `try/catch`
- Do **not** use global mutable state across tool invocations

### Versioning Policy
- Start at `0.1.0` for new/beta plugins
- `1.0.0` when a plugin is considered production-stable
- Patch bumps for bug fixes, minor for new tools, major for breaking changes

---

## Adding a New Plugin

1. Create `plugins/<name>/` with all required files
2. Add re-export shim at `.github/extensions/<name>/extension.mjs`
3. Add entry to root `marketplace.json` plugins array
4. Add entry to root `marketplace-index.json` under appropriate category
5. Open a PR using `feat(<name>): [I] add <name> plugin`
