# Composition Architecture

This document describes how the skill composition expression is parsed, evaluated, and instantiated.

## Expression Grammar

```
skill-creator(
  Autognosis(
    inferno-devcontainer[
      promise-lambda-attention(
        inferno-devcontainer,
        opencog-inferno-kernel
      ) => function-creator(
        tc | time-crystal-nn
      )
    ]
  ) /skill-infinity
)
```

## Parse Tree

| Operator | Meaning | Example |
|----------|---------|---------|
| `f(x)` | Apply: f wraps/transforms x | `Autognosis(...)` wraps inner in self-awareness |
| `[...]` | Bracket: inner configures outer | `inferno-devcontainer[...]` — inner configures devcontainer |
| `(a, b)` | Tuple: paired inputs | `(inferno-devcontainer, opencog-inferno-kernel)` as (λ, KV) |
| `=>` | Pipe: output feeds into next | Promise results feed into function-creator |
| `a \| b` | Compose: parallel merge | `tc \| time-crystal-nn` — file ops + temporal hierarchy |
| `f g` | Juxtapose: converge | `Autognosis(...) /skill-infinity` — converge to fixed point |

## Layer Architecture

### Layer 0: Infrastructure Substrate (inferno-devcontainer)

The outermost bracket `inferno-devcontainer[...]` establishes the Inferno-OS devcontainer as the execution environment. Everything inside runs within:
- Multi-stage Docker build from `inferno-os/inferno-os`
- Limbo IDE (VS Code + Acme)
- Docker-in-Docker for cluster deployment
- 9P/Styx networking on ports 6666-6668

### Layer 1: Constraint Satisfaction (promise-lambda-attention)

`promise-lambda-attention(inferno-devcontainer, opencog-inferno-kernel)`:
- **λ (Query/Promise)**: inferno-devcontainer's requirements — what must be true for the devcontainer to function (emu binary, limbo compiler, 9P ports, cluster compose, etc.)
- **KV (Key-Value/Protocol-Execution)**: opencog-inferno-kernel's capabilities — the cognitive services available (AtomSpace, PLN, ECAN, MOSES, pattern matching)
- **Mechanism**: `λ(KV)^-1` — find all kernel configurations that satisfy the devcontainer's promises

The 8 kernel promises validate that the cognitive kernel is properly configured within the devcontainer infrastructure.

### Layer 2: Domain Transforms (function-creator(tc | time-crystal-nn))

The constraint-satisfied configurations are transformed through two parallel domain mappings:

**tc → Cognitive File System**: Total Commander's file management operations are mapped to cognitive namespace operations:

| TC Operation | Cognitive Equivalent |
|-------------|---------------------|
| `tree` | Display `/cognitive/` namespace hierarchy |
| `search` | Pattern search across cognitive namespaces |
| `copy/move` | Atom migration between namespace partitions |
| `props` | Atom metadata inspection |
| `archive` | Namespace snapshot/restore |

**time-crystal-nn → Temporal Hierarchy**: The 9-level time crystal neuron architecture maps to cognitive kernel service timing:

| nn4c Level | Kernel Service | Period |
|-----------|---------------|--------|
| L0 (Ax, Pr-Ch) | AtomSpace CRUD | 8ms |
| L1 (Io-Ch, Li) | Pattern matching | 26ms |
| L2 (Me, Ac) | Inference step | 52ms |
| L3 (AIS, An-n) | Attention tick | 110ms |
| L4 (Ch-Co, PNN) | Learning batch | 160ms |
| L5 (Ca, Fi-lo) | Namespace sync | 250ms |
| L6 (Rh, Soma) | Cluster pulse | 330ms |
| L7 (Gl-S, El) | Autognosis observation | 500ms |
| L8 (Me-Rh, Sy-c) | Self-image rebuild | 1000ms |

The pipe `|` composes these: each cognitive namespace path has an associated temporal level that determines its update frequency.

### Layer 3: Self-Awareness (Autognosis)

`Autognosis(...)` wraps the entire system in hierarchical self-monitoring:

- **Level 0 (Direct Observation)**: Raw metrics — promises satisfied, temporal levels active, namespace paths
- **Level 1 (Pattern Analysis)**: Behavioral patterns — configuration completeness, hierarchy status
- **Level 2 (Meta-Cognitive)**: Self-awareness quality — confidence scores, convergence factor

Each autognosis cycle builds self-images at all three levels, generates meta-cognitive insights, and discovers optimization opportunities.

### Layer 4: Fixed Point (skill-infinity)

`... /skill-infinity` converges the Autognosis-wrapped system to a self-referential fixed point:

```
T(system) = system
```

The backward pass (self-improvement) terminates when the self-awareness score stabilizes:

```
|score(cycle_n) - score(cycle_{n-1})| < ε = 0.001
```

At convergence, the system has reached equilibrium — it understands itself completely and further self-improvement produces no change. This is the cognitive kernel's fixed point.

## Data Flow

```
                    ┌─────────────────────────┐
                    │   skill-infinity         │
                    │   (fixed point check)    │
                    └────────┬────────────────┘
                             │
                    ┌────────▼────────────────┐
                    │   Autognosis             │
                    │   (self-image building)  │
                    └────────┬────────────────┘
                             │
              ┌──────────────▼──────────────────┐
              │   inferno-devcontainer           │
              │   (infrastructure substrate)     │
              └──────────────┬──────────────────┘
                             │
              ┌──────────────▼──────────────────┐
              │   promise-lambda-attention       │
              │   λ = devcontainer requirements  │
              │   KV = kernel capabilities       │
              └──────────────┬──────────────────┘
                             │
                    ┌────────▼────────┐
                    │    => (pipe)    │
                    └───┬────────┬───┘
                        │        │
              ┌─────────▼──┐  ┌──▼──────────┐
              │  tc →       │  │ tc-nn →     │
              │  CogFS      │  │ Temporal    │
              └─────────────┘  └─────────────┘
```
