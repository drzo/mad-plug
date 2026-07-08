---
name: skinform-optim
description: Generate maximally effective skincare formulations using neural hypergraph embeddings and constraint optimization. Use for optimizing ingredient concentrations, maximizing clinical effectiveness, generating Pareto-optimal formulations, and running differentiable optimization on the CEO (JAX) subsystem.
---

# SkinForm Optimization - Maximum Clinical Effectiveness Engine

Generate optimal skincare formulations by combining neural hypergraph embeddings with constraint optimization on the JAX-based CEO subsystem.

## Core Capabilities

1. **Neural Hypergraph Embeddings** - Learnable representations for ingredients, effects, and interactions
2. **Effectiveness Maximization** - Gradient-based optimization for clinical targets
3. **Multi-Scale Skin Modeling** - Penetration prediction across skin layers
4. **Interaction Modeling** - Synergy/antagonism detection via attention
5. **Constraint Satisfaction** - Safety and stability verification

## Quick Start

### Install Dependencies

```bash
sudo pip3 install jax jaxlib flax optax
```

### Run Optimization

```python
from skinform_optim import MaxEffectivenessOptimizer, GOLD_STANDARD_INGREDIENTS, ANTI_AGING_TARGETS

optimizer = MaxEffectivenessOptimizer(
    ingredients=GOLD_STANDARD_INGREDIENTS,
    targets=ANTI_AGING_TARGETS,
    embed_dim=256
)

result = optimizer.generate_optimal_formulation(
    num_iterations=500,
    learning_rate=0.5
)
```

## Optimization Pipeline

### Stage 1: Define Clinical Targets

Specify target effects with importance weights:

```python
targets = [
    ClinicalTarget("collagen_stimulation", weight=0.25, layer="dermis"),
    ClinicalTarget("wrinkle_reduction", weight=0.20, layer="dermis"),
    ClinicalTarget("hyperpigmentation", weight=0.15, layer="epidermis"),
    ClinicalTarget("barrier_repair", weight=0.15, layer="stratum_corneum"),
    ClinicalTarget("antioxidant", weight=0.10, layer="all"),
    ClinicalTarget("hydration", weight=0.10, layer="epidermis"),
    ClinicalTarget("cell_turnover", weight=0.05, layer="epidermis"),
]
```

### Stage 2: Embedding-Based Candidate Selection

The system computes embeddings for all ingredients and target effects, then selects candidates via similarity search in embedding space.

### Stage 3: Differentiable Concentration Optimization

Gradient descent on the effectiveness objective:

```
E_total = Σⱼ wⱼ · εⱼ(F) · Pⱼ(F) · Iⱼ(F)

where:
  wⱼ = Target importance weight
  εⱼ = Embedding-predicted effectiveness
  Pⱼ = Multi-scale penetration probability
  Iⱼ = Interaction factor (synergy/antagonism)
```

### Stage 4: Constraint Verification

Hard constraints enforced via penalty functions:
- Total concentration = 100%
- Minimum therapeutic concentrations
- Maximum safe concentrations
- Non-negativity

## Architecture Components

### Hypergraph Attention Layer

```python
class HypergraphAttentionLayer(nn.Module):
    embed_dim: int = 256
    num_heads: int = 8
    
    def __call__(self, node_embeds, concentrations):
        # Concentration-modulated multi-head attention
        # Returns context-aware ingredient embeddings
```

See `references/embedding-architecture.md` for complete module specifications.

### Multi-Scale Skin Model

Predicts penetration using Potts-Guy equation:

```
log Kp = -2.7 + 0.71·logP - 0.0061·MW
```

Target layers with depths:
- Stratum corneum: 15 μm
- Epidermis: 100 μm
- Dermis: 2000 μm

### Interaction Model

Bilinear form for pairwise interactions:

```
score_ij = e_i^T W e_j
```

Positive scores indicate synergy (>1 multiplier), negative indicate antagonism (<1).

## Gold-Standard Ingredients

### Tier 1: Highest Clinical Evidence

| Ingredient | Optimal % | Mechanism |
|------------|-----------|-----------|
| Tretinoin | 0.025-0.1 | RAR/RXR activation |
| L-Ascorbic Acid | 10-20 | Collagen cofactor |
| Niacinamide | 4-5 | Ceramide synthesis |
| Retinol | 0.5-1.0 | Converts to tretinoin |

### Tier 2: Strong Evidence

| Ingredient | Optimal % | Mechanism |
|------------|-----------|-----------|
| Glycolic Acid | 8-10 | Desmosome dissolution |
| Hyaluronic Acid | 0.1-2 | GAG synthesis |
| Matrixyl 3000 | 2-5 | GF mimetic |
| Ferulic Acid | 0.5-1 | Stabilizes C+E |

### Key Synergies

- **C+E+Ferulic**: 8x antioxidant boost
- **Niacinamide + Retinoid**: Enhanced barrier + anti-aging
- **HA + Peptides**: Deep hydration + collagen support

## Output Format

Optimized formulations include:

**Formulation Table:**
| Ingredient | INCI Name | Concentration (%) |

**Effectiveness Scores:**
| Target | Base | Penetration | Final Score |

**Phase Assignment:**
- Phase A (Aqueous): Water-soluble actives
- Phase B (Oil): Lipophilic actives
- Phase C (Preservation): Preservative system

## Integration with SkinForm

This skill extends the base `skinform` skill. Use together:

1. `skinform` - Formulation creation, COSING patterns, vessel architecture
2. `skinform-optim` - Optimization, embeddings, maximum effectiveness

## References

- **Embedding Architecture**: `references/embedding-architecture.md`
- **Optimization Framework**: `references/optimization-framework.md`
- **Clinical Targets**: `references/clinical-targets.md`
- **Gold-Standard Ingredients**: `references/gold-standard-ingredients.md`
