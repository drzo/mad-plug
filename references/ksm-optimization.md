# KSM Optimization — Mapping the 12 Steps to the Marketplace Optimizer

This document specifies how `scripts/ksm_optimizer.py` implements the Knowledge
Sharing Mechanism (KSM) 12-step nested iteration cycles — documented in
`plugins/unicorn-dynamics/skills/SKILL.md` — as an executable optimization
process over the mad-plug marketplace, guided by the metrics defined in
[alexander-metrics.md](alexander-metrics.md).

## Dual-Loop Structure

The KSM nests an Iteration Cycle (inner loop, steps 4-9) inside a Solution
Cycle (outer loop, steps 1-3 and 10-12). In the optimizer, the outer loop
operates on the whole marketplace; each inner loop strengthens one chosen
critical centre (plugin).

## Outer Loop — Solution Cycle

| Step | KSM (Perspective A / B) | Optimizer phase |
|---|---|---|
| 1 | Analyze Problem in Space and Time / Desired End-State | `analyze_wholeness()` — full metrics scan; snapshot W(total). The solution vision is maximum marketplace wholeness. |
| 2 | Differentiate Tasks into Centres / Transform Tasks to Centers | `differentiate_centres()` — group deficiencies per plugin: failing structural checks + weak properties, with a leverage estimate. |
| 3 | Choose Critical Centre / Choose Critical Center | `choose_critical_centres()` — weakest wholeness first; leverage (strengthening potential) breaks ties. |
| 10 | Integrate with Solution Vision / Compare to Solution Vision | Re-scan the marketplace after all inner loops; compute W(total) after. |
| 11 | Evaluate Correctness and Simplicity / Simplify the Center; Assess Solution Vision | Verify W(total) did not regress and only the minimal safe remediations were applied. |
| 12 | Assess Solution Vision / Feedback | Emit feedback: continue to the next cycle, or flag that remaining deficiencies need manual strengthening. |

## Inner Loop — Iteration Cycle (per critical centre)

| Step | KSM (Perspective A / B) | Optimizer phase |
|---|---|---|
| 4 | Identify Constraints and Relationships / Desired End-State (Iteration) | Collect the plugin's category, dependencies, and registry state. The iteration vision is a fully conformant, living centre. |
| 5 | Differentiate Sub-Tasks to Centres / Transform Tasks to Centers | Enumerate concrete fixes; each is annotated with its structure-preserving transformation and whether it is automatable. |
| 6 | Strengthen Centres / Strengthen Centers | Apply safe remediations (apply mode only): shim creation, registry/index sync, dependency declaration, category sync. |
| 7 | Integrate with Iteration Vision / Compare to Iteration Vision | Re-score just that plugin. |
| 8 | Evaluate Correctness and Simplicity / Simplify the Centers; Assess Iteration Vision | Verify W(plugin) improved and no check regressed. |
| 9 | Assess Iteration Vision / Feedback | Remaining failing checks feed back as recommendations for the next cycle. |

## Remediation ↔ Transformation Mapping

Each remediation is an application of one of the fifteen structure-preserving
transformations:

| Deficiency | Transformation | Automated? |
|---|---|---|
| Missing `.github/extensions/<name>/` shim | Not-Separateness | yes — `create-shim` |
| Missing marketplace-index entry | Not-Separateness | yes — `index-sync` |
| Registry category drift | Not-Separateness | yes — `registry-category-sync` |
| Undeclared dependencies list | Boundaries | yes — `declare-dependencies` |
| Tools list drift vs extension | Local Symmetries | no — recommend |
| Missing try/catch in handlers | Good Shape | no — recommend |
| Missing README sections, skill depth | Levels of Scale / Strong Centers | no — recommend |

Content-quality items are never automated: strengthening a centre's meaning
requires judgment, per the Four Conditions for Differentiation (Awareness of
the Whole, Step-by-Step Adaptation, Unpredictability, Feedback).

## Modes

| Mode | Steps executed | Side effects |
|---|---|---|
| `report` | 1-5 | none |
| `plan` | 1-5 | none — ordered remediation actions emitted |
| `apply` | 1-12 | safe remediations only; re-scores per centre and marketplace |

## Convergence Criteria

A cycle history (via `--history <file>`) records the wholeness trajectory
across successive cycles. The process converges when:

1. W(total) is non-decreasing across cycles (step 11 guard), and
2. no automated remediations remain (all step-5 sub-tasks are recommendations), and
3. the weakest centre's W(plugin) exceeds the living-centre threshold (0.85,
   see [alexander-metrics.md](alexander-metrics.md)).

At convergence, further strengthening is manual: the optimizer's reports
identify the latent centres and their weakest properties, and a human or agent
applies content-level transformations, then re-runs the cycle — "when
complete, we go back to the beginning of the cycle, and apply the same process
over" (Alexander's step 11).
