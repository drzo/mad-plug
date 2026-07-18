# Alexander Metrics — The Fifteen Properties as Marketplace Metrics

This document defines the scoring model used by `scripts/alexander_metrics.py` to
quantify the "degree of life" of every centre (plugin) in the mad-plug marketplace.
It maps Christopher Alexander's fifteen structure-preserving properties to
measurable marketplace analogues and specifies the wholeness aggregation.

## Wholeness Aggregation

```
W(plugin) = 0.50 · structural + 0.35 · fifteen + 0.15 · topology
W(total)  = mean of W(plugin) over all plugins
```

All scores are normalized to [0, 1].

**Weighting rationale:**

- **structural (0.50)** — AGENTS.md conformance is the load-bearing frame; a
  plugin missing required files or with drifted registries is broken regardless
  of its aesthetic qualities. It dominates the score.
- **fifteen (0.35)** — the fifteen properties measure *quality of life* beyond
  bare conformance: coherence, reuse, distinctiveness, calm. They differentiate
  living centres from merely valid ones.
- **topology (0.15)** — connectivity to the gh253 pattern graph rewards
  discoverability and integration but should not overwhelm intrinsic quality;
  it is the lightest weight.

## Group 1 — Structural Conformance

One boolean check per AGENTS.md quality expectation; the group score is the
fraction of passing checks.

| Family | Check | Source |
|---|---|---|
| Files | `extension.mjs`, `plugin.md`, `plugin.json`, `README.md` present | AGENTS.md "Plugin Directory Structure" |
| Files | shim at `.github/extensions/<name>/extension.mjs` | AGENTS.md "auto-discovery" |
| plugin.json | parses; `name`, `version`, `description`, `category`, `entrypoint` present | AGENTS.md schema |
| plugin.json | `name` matches directory; semver version; description ≤ 160 chars | Naming conventions |
| plugin.json | `category` is a defined category ID; `dependencies` is a list | Defined Categories |
| plugin.json | `tools` matches the names registered in extension.mjs | Quality Expectations |
| README | six sections present: Description, Usage Examples, Tools, Version, Dependencies, Category | Quality Expectations |
| extension.mjs | calls `joinSession()`; try/catch around `runScript`/`runPython`; snake_case tool names | Quality Expectations |
| Registry | entry in `marketplace.json` and `marketplace-index.json`; category consistent | Adding a New Plugin |

## Group 2 — The Fifteen Properties

Each property scores in [0, 1]; the group score is their mean.

| # | Property | Marketplace analogue | Scoring |
|---|---|---|---|
| 1 | **Levels of Scale** | Artifacts exist at multiple granularities | Fraction of {plugin.md, README.md, skills/, tools} present |
| 2 | **Strong Centers** | Tool depth relative to category peers | min(1, tool_count / category median) |
| 3 | **Boundaries** | Explicit dependency interface | 1 if `dependencies` list declared |
| 4 | **Alternating Repetition** | Structure consistent with category siblings | 1 − |own conformance − category avg conformance| |
| 5 | **Positive Space** | No dead intra-plugin references | Fraction of README `skills/…`, `scripts/…`, `references/…` refs that resolve |
| 6 | **Good Shape** | Well-formed single-sentence description | 1 if ≤ 160 chars and ≤ 1 sentence break |
| 7 | **Local Symmetries** | Naming conventions consistent at every level | Fraction of {kebab-case dir, snake_case tools} conforming |
| 8 | **Deep Interlock** | Participates in the dependency graph | 1 if declares deps or is depended upon, else 0.5 |
| 9 | **Contrast** | Tag distinctiveness within the category | 0.5 + 0.5 · (unique tags / total tags) |
| 10 | **Gradients** | Versioning follows the maturity gradient | 1 if valid semver |
| 11 | **Roughness** | Optional enrichment tolerated, never forced | Always 1 (optional dirs are a bonus signal only) |
| 12 | **Echoes** | Shared helpers reused, never copied | 1 if `_shared/procRunner.mjs` imported or no process spawning |
| 13 | **The Void** | No global mutable state across invocations | 1 if no top-level `let`/`var` in extension.mjs |
| 14 | **Simplicity & Inner Calm** | Extension carries no excess weight | 1 if extension ≤ 400 lines |
| 15 | **Not-Separateness** | Woven into registries and the topology | Mean of {marketplace.json, marketplace-index.json, tag ∩ index tags} |

## Group 3 — Topology

| Metric | Definition |
|---|---|
| tag-pattern-connectivity | Fraction of the plugin's tags that surface in gh253 pattern slugs (patterns/cat1-3) |
| category-anchoring | 1 if the plugin's category is a defined category (categories map onto gh253's enterprise/organisation/repository scales) |

Hub patterns (107 MODULAR DESIGN, 30 ACTIVITY NODES, 100 CONTRIBUTOR PATH) and
entry points (1, 18, 24, 95) anchor the slug space that tags are matched against.

## Interpreting Scores

- **W ≥ 0.95** — strong centre; maintain.
- **0.85 ≤ W < 0.95** — living but improvable; weak properties indicate the
  latent centre to strengthen next.
- **W < 0.85** — latent centre; prioritized by the KSM cycle engine
  (`scripts/ksm_optimizer.py`, see [ksm-optimization.md](ksm-optimization.md)).

The per-plugin report lists `failing_checks` (structural) and `weak_properties`
(fifteen, score < 0.75) so the weakest dimension of each centre is directly
actionable.
