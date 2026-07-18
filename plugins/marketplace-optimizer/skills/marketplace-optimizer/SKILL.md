---
name: marketplace-optimizer
description: Optimize marketplace plugins and skills over KSM cycles guided by Alexander wholeness metrics. Use for scoring plugin conformance, ranking latent centres, running KSM 12-step nested iteration cycles, and tracking marketplace wholeness convergence.
---

# Marketplace Optimizer

Optimization of plugins & skills over KSM cycles & Alexander metrics: the marketplace is a *wholeness*, every plugin is a *centre*, and each optimization cycle strengthens the weakest latent centre through structure-preserving transformations.

## The Metrics Model

Each plugin's degree of life is scored along three groups, aggregated into a wholeness score:

```
W(plugin) = 0.50·structural + 0.35·fifteen + 0.15·topology
W(total)  = mean over all plugins
```

### Group 1 — Structural Conformance (AGENTS.md)

Boolean checks derived from the marketplace quality expectations:

| Family | Checks |
|---|---|
| Files | extension.mjs, plugin.md, plugin.json, README.md, `.github/extensions/<name>/` shim |
| plugin.json | required fields, semver, name matches directory, description length, valid category, dependencies declared, tools list matches extension registrations |
| README | six mandated sections: Description, Usage Examples, Tools, Version, Dependencies, Category & Tags |
| extension.mjs | `joinSession()` usage, try/catch around script runners, snake_case tool names |
| Registry | present in marketplace.json and marketplace-index.json, category consistent |

### Group 2 — The Fifteen Properties

Alexander's 15 structure-preserving properties, each mapped to a measurable marketplace analogue in `references/alexander-metrics.md`. Examples:

| Property | Marketplace analogue |
|---|---|
| Levels of Scale | Artifacts at multiple granularities (plugin.md → README → skills → tools) |
| Strong Centers | Tool count relative to category median |
| Boundaries | Explicit dependency declarations |
| Echoes | Reuse of `plugins/_shared/procRunner.mjs` instead of copies |
| The Void | No global mutable state in extension.mjs |
| Not-Separateness | Woven into both registries and the pattern topology |

### Group 3 — Topology

Connectivity of the plugin's tags and category to the gh253 pattern graph (hub patterns such as 107 MODULAR DESIGN and 30 ACTIVITY NODES).

## The KSM Optimization Workflow

The optimizer executes the KSM 12-step dual-loop process (see `plugins/unicorn-dynamics/skills/SKILL.md`):

**Outer Loop (Solution Cycle):**

| KSM Step | Optimizer Phase |
|---|---|
| 1. Analyze Problem in Space & Time | Full metrics scan; snapshot W(total) |
| 2. Differentiate Tasks into Centres | Group deficiencies per plugin |
| 3. Choose Critical Centre | Weakest wholeness, highest leverage first |
| 10. Integrate with Solution Vision | Re-scan the marketplace |
| 11. Evaluate Correctness & Simplicity | Verify W(total) did not regress |
| 12. Assess Solution Vision | Feedback into the next cycle |

**Inner Loop (Iteration Cycle), per chosen centre:**

| KSM Step | Optimizer Phase |
|---|---|
| 4. Identify Constraints and Relationships | Category, dependencies, registry state |
| 5. Differentiate Sub-Tasks to Centres | Enumerate concrete fixes with their transformations |
| 6. Strengthen Centres | Apply safe remediations (shim creation, registry sync, metadata normalization) |
| 7. Compare to Iteration Vision | Re-score the plugin |
| 8. Evaluate Correctness and Simplicity | Verify improvement and minimality |
| 9. Assess Iteration Vision | Feedback into the outer loop |

## Workflow: Running an Optimization Pass

1. `optimization_report()` — identify the latent centres
2. `ksm_cycle_run(mode="plan")` — review the ordered remediation actions
3. `ksm_cycle_run(mode="apply")` — execute safe remediations, verify convergence
4. Manually strengthen remaining recommended items (content quality, tool depth)
5. Repeat until W(total) converges

## Reference Files

- `references/alexander-metrics.md` — full 15-property mapping, scoring formulas, weighting rationale
- `references/ksm-optimization.md` — KSM step-to-phase mapping and convergence criteria
- `scripts/alexander_metrics.py` — the metrics scanner
- `scripts/ksm_optimizer.py` — the cycle engine
