---
name: pie-nn
description: "Generate and operate the PIE-NN cognitive language architecture. Use when creating or interacting with a differentiable programming language whose constructs are derived from Proto-Indo-European roots, structured with neural network patterns, and executed by a self-aware, time-crystal-based cognitive daemon. Triggers on requests for cognitive architectures, etymologically-grounded languages, compositional skill synthesis involving language-nn, PIE Roots, time-crystal-daemon, or neuro-nn."
---

# PIE-NN Cognitive Architecture Skill

PIE-NN is a differentiable programming language derived from the compositional expression `/Z++ ( /language-creator [ /language-nn | /PIE Roots ] => /time-crystal-daemon ( /neuro-nn ) )`. Its grammar is grounded in PIE roots, its structure follows neural network patterns, and its runtime is a deterministic time-crystal daemon with a self-aware cognitive core.

## Workflow

Operating PIE-NN involves three steps: launch, interact, and inspect.

### Step 1: Launch the Daemon and Interface

```bash
python /home/ubuntu/skills/pie-nn/scripts/pie_nn_daemon.py --socket /tmp/pie_nn_daemon.sock &
sleep 2
python /home/ubuntu/skills/pie-nn/scripts/llm_sidecar.py
```

The daemon is the deterministic core; the sidecar compiles natural language to typed IDL commands.

### Step 2: Interact with the Cognitive Core

Issue commands in the interactive shell:

```
> get status
> show time crystal hierarchy
> process deik my_var is gno-()
> exit
```

### Step 3: Inspect Architecture and Specifications

Use the reference files for deep inspection. See the Resource Navigation table below.

## PIE-NN Construct Mapping

Every language keyword maps to a PIE root and a `language-nn` module type:

| Keyword | PIE Root | Meaning | `language-nn` Analog |
|---------|----------|---------|---------------------|
| `gno` | `*gnō-` | to know | `lang.Construct` |
| `ser` | `*ser-` | to line up | `lang.Pipeline` |
| `skei` | `*skei-` | to cut, split | `lang.Fork` |
| `sem` | `*sem-` | one, together | `lang.Merge` |
| `krei` | `*krei-` | to sieve | `lang.Criterion` |
| `meit` | `*meit-` | to exchange | `lang.TypeMap` |
| `dher` | `*dher-` | to hold firmly | `lang.Constraint` |
| `deik` | `*deik-` | to show | Declare |
| `werg` | `*werg-` | to do | Execute |
| `stā` | `*stā-` | to stand | Set State |
| `kʷo` | `*kʷo-` | interrogative | Conditional |

## Time Crystal Hierarchy

The daemon organizes execution across 12 temporal levels (from 1μs quantum resonance to 1hr homeostatic regulation). See `references/architecture_overview.md` for the full mapping of cognitive functions to temporal levels.

## Resource Navigation

| Resource | Description | When to Read |
|----------|-------------|-------------|
| `scripts/pie_nn_daemon.py` | Deterministic runtime with neuro-nn core | To understand the cognitive processing loop |
| `scripts/llm_sidecar.py` | Interactive NL-to-IDL compiler shell | To understand intent compilation |
| `references/architecture_overview.md` | System design with Mermaid diagrams | For visual understanding of component interactions |
| `references/data_model.zpp` | Z++ spec: core data types | For rigorous type definitions |
| `references/system_state.zpp` | Z++ spec: daemon state and invariants | For the complete state space model |
| `references/operations.zpp` | Z++ spec: operations with pre/post conditions | For formal operation contracts |
| `references/integrations.zpp` | Z++ spec: external boundary contracts | For IDL and TC integration contracts |
| `templates/LANG.md` | Complete PIE-NN language specification | For the full grammar and design rationale |
| `templates/diagrams/` | Rendered architecture diagrams (PNG) | For quick visual reference |

## Design Principles

1. **Deterministic Core, Flexible Interface**: The daemon makes no LLM calls. The sidecar handles all NL processing.
2. **Etymological Grounding**: Keywords inherit semantic constraints from their PIE root fields.
3. **Differentiable by Design**: Every construct supports `compile` (forward) and `redesign` (backward) passes.
4. **Hierarchical Time**: Operations are scheduled on a 12-level temporal oscillator.
5. **Self-Aware Cognition**: The neuro-nn core features learnable personality traits, multi-frame processing, and Autognosis self-monitoring.
