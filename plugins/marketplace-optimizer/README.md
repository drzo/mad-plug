# marketplace-optimizer

Optimize marketplace plugins and skills over KSM cycles guided by Alexander wholeness metrics.

**Version:** 0.1.0 | **Category:** Skill Engineering | **Tags:** `optimization` `metric` `pattern` `ksm`

---

## Description

`marketplace-optimizer` treats the mad-plug marketplace itself as an Alexandrian *wholeness* — every plugin and skill is a *centre* with a measurable degree of life. It quantifies each centre along three metric groups:

1. **Structural conformance** — AGENTS.md quality expectations: required files, plugin.json schema, README sections, extension.mjs contracts, registry coherence.
2. **The Fifteen Properties** — Christopher Alexander's 15 structure-preserving properties mapped to marketplace analogues (see [references/alexander-metrics.md](../../references/alexander-metrics.md)).
3. **Topology** — connectivity of tags/category to the gh253 pattern graph.

These aggregate into a wholeness score **W(plugin)** and a marketplace wholeness **W(total)**. The plugin then runs the **Knowledge Sharing Mechanism (KSM)** 12-step dual-loop process from [unicorn-dynamics](../unicorn-dynamics/README.md) to iteratively strengthen the weakest (latent) centres, applying safe automated remediations and recommending manual strengthening for content-quality items. The step-to-phase mapping is documented in [references/ksm-optimization.md](../../references/ksm-optimization.md).

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `alexander_score` | Score one plugin or the whole marketplace; returns W scores with per-metric breakdown | — (`plugin`, `format` optional) |
| `ksm_cycle_run` | Run one KSM outer-loop cycle in `report`, `plan`, or `apply` mode | `mode` (`limit` optional) |
| `optimization_report` | Rank the weakest centres — the latent centres for the next cycle | — (`count` optional) |

### `ksm_cycle_run` modes

| Mode | Effect |
|---|---|
| `report` | Score the marketplace and rank the weakest centres — read-only |
| `plan` | Emit ordered remediation actions per KSM step, per centre — read-only |
| `apply` | Execute safe automated remediations (registry sync, shim creation, metadata normalization); content-quality items remain recommendations |

---

## Usage Examples

### Score the whole marketplace
```
alexander_score()
```
Returns W(total), per-plugin wholeness, and each plugin's weakest property.

### Score a single plugin with full breakdown
```
alexander_score(plugin="pattern-navigator")
```
Returns the JSON report: structural checks, all 15 property scores, topology connectivity, failing checks, and weak properties.

### Plan one KSM cycle over the 3 weakest centres
```
ksm_cycle_run(mode="plan", limit="3")
```
Emits steps 1-5 of the KSM process: wholeness snapshot, differentiated centres, chosen critical centres, constraints, and ordered sub-tasks with their structure-preserving transformations.

### Apply safe remediations and verify convergence
```
ksm_cycle_run(mode="apply")
```
Runs the full 12-step cycle: applies automated fixes (steps 6), re-scores each centre (steps 7-9), and reports the marketplace wholeness delta with feedback (steps 10-12).

---

## Version

0.1.0

## Dependencies

None (draws on knowledge from `unicorn-dynamics` and `pattern-navigator`, but has no runtime plugin dependencies).

## Category & Tags

**Category:** `skill-engineering`
**Tags:** `optimization`, `metric`, `pattern`, `ksm`
