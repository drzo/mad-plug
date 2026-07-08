---
name: manuscog-cognitive-devkernel
description: "Self-aware Inferno-OS cognitive development kernel synthesized from skill-creator(Autognosis(inferno-devcontainer[promise-lambda-attention(inferno-devcontainer, opencog-inferno-kernel) to function-creator(tc | time-crystal-nn)]) /skill-infinity). Use when deploying or validating ManusCog cognitive kernel environments, running autognosis self-monitoring cycles, managing cognitive 9P namespaces, checking temporal hierarchy status, or verifying kernel promise constraints. Provides devcontainer validation, self-image building, namespace management, and fixed-point convergence checking."
---

# ManusCog Cognitive DevKernel

A self-aware, self-improving cognitive development kernel for the ManusCog distributed AGI operating system. Synthesized from the composition:

```
skill-creator(
  Autognosis(
    inferno-devcontainer[
      promise-lambda-attention(inferno-devcontainer, opencog-inferno-kernel)
        => function-creator(tc | time-crystal-nn)
    ]
  ) /skill-infinity
)
```

## Composition Layers

| Layer | Skill Source | Role in Kernel |
|-------|-------------|----------------|
| Infrastructure | inferno-devcontainer | Devcontainer with Inferno-OS, Limbo IDE, cluster support |
| Constraints | promise-lambda-attention | 8 kernel promises validate configuration |
| File System | function-creator(tc) | TC file ops → cognitive 9P namespace operations |
| Temporal | function-creator(time-crystal-nn) | 9-level time crystal → kernel service scheduling |
| Self-Awareness | Autognosis | 3-level hierarchical self-image building |
| Convergence | skill-infinity | Self-referential fixed-point checking |

**For the full composition parse tree and data flow**, read `references/composition_architecture.md`.

## Quick Start

### 1. Validate a Kernel Configuration

Check that a ManusCog repository satisfies all 8 kernel promises:

```bash
python3 /home/ubuntu/skills/manuscog-cognitive-devkernel/scripts/cognitive_devkernel.py validate /path/to/manuscog
```

### 2. View Kernel Self-Image

Display the Autognosis hierarchical self-image with temporal hierarchy status:

```bash
python3 /home/ubuntu/skills/manuscog-cognitive-devkernel/scripts/cognitive_devkernel.py status
```

### 3. Run Autognosis Cycle

Execute 5 self-improvement cycles and check for fixed-point convergence:

```bash
python3 /home/ubuntu/skills/manuscog-cognitive-devkernel/scripts/cognitive_devkernel.py cycle
```

### 4. View Domain Transforms

Display the tc → Cognitive File System and time-crystal-nn → Temporal Hierarchy mappings:

```bash
python3 /home/ubuntu/skills/manuscog-cognitive-devkernel/scripts/cognitive_devkernel.py transform
```

## Promise-Lambda Attention

The kernel validates its configuration through 8 promises derived from `promise-lambda-attention(inferno-devcontainer, opencog-inferno-kernel)`:

| Promise | λ Constraint | KV Source |
|---------|-------------|----------|
| `inferno-binary` | emu binary in Dockerfile | opencog-inferno-kernel |
| `limbo-compiler` | limbo compiler in Dockerfile | opencog-inferno-kernel |
| `9p-listener` | Port 6666 in devcontainer.json | inferno-devcontainer |
| `cluster-compose` | inferno-registry in compose | inferno-devcontainer |
| `cognitive-ns` | /cognitive/ namespace defined | opencog-inferno-kernel |
| `devcontainer-json` | INFERNO_ROOT in containerEnv | inferno-devcontainer |
| `autognosis-loop` | Verification in post-start.sh | Autognosis |
| `temporal-levels` | 9+ temporal levels defined | time-crystal-nn |

## Cognitive Namespace (tc Transform)

Total Commander file operations are mapped to cognitive 9P namespace operations:

```
/cognitive/
├── atomspace/{atoms, types, indices}
├── inference/{rules, queue, results}
├── attention/{bank, agents}
├── learning/{populations, fitness}
├── temporal/{levels, phases}
└── autognosis/{images, insights, metrics}
```

Each path is accessible via 9P/Styx protocol. `read` queries values, `write` updates them, `stat` returns metadata.

**For the full namespace reference and 9P operation mapping**, read `references/cognitive_namespace.md`.

## Temporal Hierarchy (time-crystal-nn Transform)

The 9-level time crystal neuron architecture maps to kernel service scheduling:

| Level | Service | Period | Biological Analog |
|-------|---------|--------|-------------------|
| L0 | AtomSpace CRUD | 8ms | Protein dynamics (Ax, Pr-Ch) |
| L1 | Pattern matching | 26ms | Ion channel gating (Io-Ch, Li) |
| L2 | PLN inference | 52ms | Membrane dynamics (Me, Ac) |
| L3 | ECAN attention | 110ms | Axon initial segment (AIS) |
| L4 | MOSES learning | 160ms | Dendritic integration (Ch-Co) |
| L5 | Namespace sync | 250ms | Synaptic plasticity (Ca, Fi-lo) |
| L6 | Cluster heartbeat | 330ms | Soma processing (Rh, Soma) |
| L7 | Autognosis observation | 500ms | Network sync (Gl-S, El) |
| L8 | Self-image rebuild | 1000ms | Global rhythm (Me-Rh, Sy-c) |

## Autognosis Self-Image

Three hierarchical levels of self-monitoring:

| Level | Name | What It Observes |
|-------|------|------------------|
| 0 | Direct Observation | Promise satisfaction, temporal levels, namespace paths |
| 1 | Pattern Analysis | Configuration completeness, hierarchy status |
| 2 | Meta-Cognitive | Self-awareness quality, convergence factor |

Each cycle produces self-images with confidence scores and meta-reflections.

## skill-infinity Convergence

The system converges to a fixed point when:

```
|self_awareness(cycle_n) - self_awareness(cycle_{n-1})| < 0.001
```

At convergence, further self-improvement cycles produce no change — the kernel has reached equilibrium.

## Limbo Module Template

A sample Limbo module implementing Autognosis within Inferno-OS is provided at `templates/cogkernel_autognosis.b`. It demonstrates:
- Temporal level constants mapped from time-crystal-nn
- `SelfImage` ADT with confidence and reflections
- Channel-based observation collection at L7 (500ms)
- Self-image building at L8 (1000ms)

Compile with: `limbo-build compile templates/cogkernel_autognosis.b`

## Bundled Resources

- **`scripts/`**
  - `cognitive_devkernel.py` — Unified CLI: status, validate, promise, transform, cycle
- **`references/`**
  - `composition_architecture.md` — Full parse tree, layer architecture, data flow
  - `cognitive_namespace.md` — 9P namespace hierarchy, tc transform mapping, temporal binding
- **`templates/`**
  - `.promise` — Promise-lambda configuration file for kernel validation
  - `cogkernel_autognosis.b` — Limbo module template for Autognosis
  - `transform_spec.yaml` — Function-creator transform specification (tc | time-crystal-nn)

## Composition with Other Skills

| Skill | Relationship |
|-------|-------------|
| **inferno-devcontainer** | Infrastructure substrate — devcontainer templates |
| **opencog-inferno-kernel** | Cognitive services — kernel C implementation |
| **promise-lambda-attention** | Constraint mechanism — promise validation |
| **function-creator** | Transform engine — tc and time-crystal-nn mappings |
| **tc** | Source domain — file management operations |
| **time-crystal-nn** | Source domain — temporal hierarchy architecture |
| **Autognosis** | Self-awareness — hierarchical self-image building |
| **skill-infinity** | Convergence — self-referential fixed point |
| **skill-creator** | Packaging — skill structure and validation |
