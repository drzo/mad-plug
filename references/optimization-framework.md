# Optimization Framework for Maximum Clinical Effectiveness

## Objective Function

The primary objective is to maximize total clinical effectiveness:

```
E_total = Σⱼ wⱼ · εⱼ(F) · Pⱼ(F) · Iⱼ(F)

where:
  F = Formulation (ingredient concentrations)
  wⱼ = Target importance weight (Σwⱼ = 1)
  εⱼ = Embedding-predicted effectiveness for target j
  Pⱼ = Multi-scale penetration probability to target layer
  Iⱼ = Interaction factor (synergy/antagonism)
```

## Constraint System

### Hard Constraints (Must Satisfy)

```python
def constraint_penalty(concentrations: jnp.ndarray) -> float:
    penalty = 0.0
    
    # C1: Total concentration = 100%
    total = concentrations.sum()
    penalty += 100.0 * (total - 100.0) ** 2
    
    # C2: Minimum therapeutic concentrations
    active_mask = concentrations > 0.01
    below_min = jnp.maximum(0, min_conc - concentrations) * active_mask
    penalty += 10.0 * jnp.sum(below_min ** 2)
    
    # C3: Maximum safe concentrations
    above_max = jnp.maximum(0, concentrations - max_conc)
    penalty += 100.0 * jnp.sum(above_max ** 2)
    
    # C4: Non-negativity
    negative = jnp.maximum(0, -concentrations)
    penalty += 1000.0 * jnp.sum(negative ** 2)
    
    return penalty
```

### Soft Constraints (Optimize)

- Sensory elegance (texture, absorption)
- Stability (12+ month shelf life)
- Penetration enhancement

## Optimization Algorithm

### Gradient-Based Optimization

```python
def optimization_step(
    concentrations: jnp.ndarray,
    params: Dict,
    opt_state: optax.OptState,
    optimizer: optax.GradientTransformation
) -> Tuple[jnp.ndarray, optax.OptState, float]:
    
    def objective(conc):
        effectiveness, _ = compute_effectiveness(conc, params)
        penalty = constraint_penalty(conc)
        return -effectiveness + penalty
    
    loss, grads = jax.value_and_grad(objective)(concentrations)
    updates, opt_state = optimizer.update(grads, opt_state, concentrations)
    concentrations = optax.apply_updates(concentrations, updates)
    
    # Project to feasible region
    concentrations = jnp.clip(concentrations, 0.0, max_conc)
    
    return concentrations, opt_state, loss
```

### Learning Rate Schedule

Warmup cosine decay for stable convergence:

```python
schedule = optax.warmup_cosine_decay_schedule(
    init_value=learning_rate,
    peak_value=learning_rate * 2,
    warmup_steps=100,
    decay_steps=num_iterations - 100,
    end_value=learning_rate * 0.01
)
optimizer = optax.adam(learning_rate=schedule)
```

## Multi-Scale Skin Penetration Model

### Potts-Guy Permeability

```python
def compute_permeability(mw: float, log_p: float) -> float:
    """
    Potts-Guy equation for skin permeability.
    
    log Kp = -2.7 + 0.71·logP - 0.0061·MW
    
    Args:
        mw: Molecular weight (Da)
        log_p: Octanol-water partition coefficient
    
    Returns:
        Permeability coefficient Kp (cm/h)
    """
    log_kp = -2.7 + 0.71 * log_p - 0.0061 * mw
    return 10 ** log_kp
```

### Layer-Specific Penetration

```python
LAYER_DEPTHS = {
    'stratum_corneum': 15.0,    # μm
    'epidermis': 100.0,
    'dermis': 2000.0,
    'hypodermis': 10000.0
}

def compute_penetration(
    kp: float,
    diffusion: float,
    concentration: float,
    log_p: float,
    target_depth: float
) -> float:
    """
    Compute penetration probability to target layer.
    
    P = Kp · D · C · exp(-depth/λ)
    
    where λ = characteristic penetration length
    """
    lambda_pen = 100.0 * (1 + log_p)
    lambda_pen = jnp.clip(lambda_pen, 10.0, 1000.0)
    
    penetration = kp * diffusion * concentration * jnp.exp(-target_depth / lambda_pen)
    return jnp.clip(penetration, 0.0, 1.0)
```

## Interaction Modeling

### Bilinear Interaction Scores

```python
class InteractionModel(nn.Module):
    embed_dim: int = 256
    
    @nn.compact
    def __call__(
        self,
        ingredient_embeds: jnp.ndarray,
        concentrations: jnp.ndarray
    ) -> jnp.ndarray:
        N = ingredient_embeds.shape[0]
        
        # Bilinear form: score_ij = e_i^T W e_j
        W = self.param(
            'interaction_matrix',
            nn.initializers.normal(stddev=0.02),
            (self.embed_dim, self.embed_dim)
        )
        
        interaction_scores = jnp.einsum('id,de,je->ij', ingredient_embeds, W, ingredient_embeds)
        
        # Weight by concentration product
        conc_weights = concentrations[:, None] * concentrations[None, :]
        mask = 1.0 - jnp.eye(N)  # No self-interaction
        
        interaction_scores = interaction_scores * mask
        conc_weights = conc_weights * mask
        
        # Weighted average
        total_interaction = jnp.sum(interaction_scores * conc_weights)
        total_weight = jnp.sum(conc_weights) + 1e-8
        avg_interaction = total_interaction / total_weight
        
        # Transform to multiplier (centered at 1.0)
        return 1.0 + 0.5 * jnp.tanh(avg_interaction)
```

### Known Synergies

| Combination | Multiplier | Mechanism |
|-------------|------------|-----------|
| C + E + Ferulic | 1.8x | Antioxidant network |
| Niacinamide + Retinoid | 1.3x | Barrier + anti-aging |
| HA + Peptides | 1.2x | Hydration + collagen |
| AHA + BHA | 1.15x | Dual exfoliation |

### Known Antagonisms

| Combination | Multiplier | Issue |
|-------------|------------|-------|
| Vitamin C + Niacinamide (high pH) | 0.7x | pH incompatibility |
| Retinoids + AHA/BHA | 0.6x | Irritation risk |
| Benzoyl Peroxide + Retinoids | 0.5x | Oxidative degradation |

## Optimization Workflow

```
1. Initialize concentrations at optimal therapeutic values
2. Scale to sum to 100%
3. Setup Adam optimizer with warmup schedule
4. For each iteration:
   a. Compute effectiveness score
   b. Compute constraint penalty
   c. Compute gradients
   d. Update concentrations
   e. Project to feasible region
   f. Track best solution
5. Return best formulation with effectiveness breakdown
```

## Hyperparameters

| Parameter | Default | Range | Description |
|-----------|---------|-------|-------------|
| num_iterations | 500 | 100-2000 | Optimization steps |
| learning_rate | 0.5 | 0.01-1.0 | Base learning rate |
| warmup_steps | 100 | 50-200 | LR warmup period |
| penalty_weight_total | 100 | 10-1000 | Total=100% penalty |
| penalty_weight_min | 10 | 1-100 | Min concentration penalty |
| penalty_weight_max | 100 | 10-1000 | Max concentration penalty |
| penalty_weight_neg | 1000 | 100-10000 | Non-negativity penalty |
