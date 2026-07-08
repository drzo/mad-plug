#!/usr/bin/env python3
"""
SkinForm Optimization - Maximum Clinical Effectiveness Engine

Generate optimal skincare formulations using neural hypergraph embeddings
and constraint optimization on the JAX-based CEO subsystem.

Usage:
    python skinform_optim.py [--iterations N] [--learning-rate LR]
"""

import json
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
import argparse

import jax
import jax.numpy as jnp
from jax import random
import flax.linen as nn
import optax

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class Ingredient:
    """Ingredient specification with optimization bounds."""
    name: str
    inci_name: str
    min_conc: float
    max_conc: float
    optimal_conc: float
    mw: float  # Molecular weight (Da)
    log_p: float  # Octanol-water partition coefficient
    solubility: str  # 'water', 'oil', or 'both'
    functions: List[str] = field(default_factory=list)

@dataclass
class ClinicalTarget:
    """Clinical target with importance weight."""
    name: str
    weight: float
    target_layer: str  # 'stratum_corneum', 'epidermis', 'dermis', 'all'
    mechanism: str = ""

# ============================================================================
# GOLD-STANDARD INGREDIENTS
# ============================================================================

GOLD_STANDARD_INGREDIENTS = [
    Ingredient("Purified Water", "Aqua", 50.0, 80.0, 62.0, 18.0, -1.4, "water", ["solvent"]),
    Ingredient("L-Ascorbic Acid", "Ascorbic Acid", 10.0, 20.0, 15.0, 176.1, -1.8, "water", ["antioxidant", "collagen"]),
    Ingredient("Niacinamide", "Niacinamide", 4.0, 10.0, 5.0, 122.1, -0.4, "water", ["barrier", "brightening"]),
    Ingredient("Glycerin", "Glycerin", 2.0, 10.0, 5.0, 92.1, -1.8, "water", ["humectant"]),
    Ingredient("Hyaluronic Acid", "Sodium Hyaluronate", 0.1, 2.0, 1.5, 403.3, -5.0, "water", ["hydration"]),
    Ingredient("Matrixyl 3000", "Palmitoyl Tripeptide-1", 2.0, 8.0, 4.0, 578.8, 2.1, "water", ["collagen", "peptide"]),
    Ingredient("Butylene Glycol", "Butylene Glycol", 1.0, 5.0, 3.0, 90.1, -0.8, "water", ["penetration"]),
    Ingredient("Tretinoin", "Tretinoin", 0.025, 0.1, 0.05, 300.4, 6.3, "oil", ["retinoid", "collagen"]),
    Ingredient("Ferulic Acid", "Ferulic Acid", 0.5, 1.0, 1.0, 194.2, 1.5, "both", ["antioxidant", "stabilizer"]),
    Ingredient("Tocopherol", "Tocopherol", 0.5, 2.0, 1.0, 430.7, 10.7, "oil", ["antioxidant"]),
    Ingredient("Squalane", "Squalane", 1.0, 5.0, 2.0, 422.8, 14.0, "oil", ["emollient"]),
    Ingredient("Phenoxyethanol", "Phenoxyethanol", 0.5, 1.0, 0.8, 138.2, 1.2, "both", ["preservative"]),
    Ingredient("Ethylhexylglycerin", "Ethylhexylglycerin", 0.1, 0.5, 0.3, 204.3, 2.7, "both", ["preservative_booster"]),
]

ANTI_AGING_TARGETS = [
    ClinicalTarget("collagen_stimulation", 0.25, "dermis", "fibroblast_activation"),
    ClinicalTarget("wrinkle_reduction", 0.20, "dermis", "ecm_remodeling"),
    ClinicalTarget("hyperpigmentation", 0.15, "epidermis", "tyrosinase_inhibition"),
    ClinicalTarget("barrier_repair", 0.15, "stratum_corneum", "ceramide_synthesis"),
    ClinicalTarget("antioxidant", 0.10, "all", "ros_neutralization"),
    ClinicalTarget("hydration", 0.10, "epidermis", "ha_synthesis"),
    ClinicalTarget("cell_turnover", 0.05, "epidermis", "keratinocyte_proliferation"),
]

LAYER_DEPTHS = {
    'stratum_corneum': 15.0,
    'epidermis': 100.0,
    'dermis': 2000.0,
    'all': 100.0,
}

# ============================================================================
# NEURAL NETWORK MODULES
# ============================================================================

class ConcentrationEncoder(nn.Module):
    """Sinusoidal encoding for concentration values."""
    embed_dim: int = 64
    max_concentration: float = 100.0
    
    @nn.compact
    def __call__(self, concentrations: jnp.ndarray) -> jnp.ndarray:
        conc_norm = concentrations / self.max_concentration
        d = self.embed_dim // 2
        positions = jnp.arange(d)
        div_term = jnp.exp(positions * -(jnp.log(10000.0) / d))
        
        pe_sin = jnp.sin(conc_norm[..., None] * div_term * jnp.pi)
        pe_cos = jnp.cos(conc_norm[..., None] * div_term * jnp.pi)
        sinusoidal = jnp.concatenate([pe_sin, pe_cos], axis=-1)
        
        return nn.Dense(self.embed_dim)(sinusoidal)

class HypergraphAttentionLayer(nn.Module):
    """Hypergraph attention for ingredient interactions."""
    embed_dim: int = 256
    num_heads: int = 8
    
    @nn.compact
    def __call__(
        self,
        node_embeds: jnp.ndarray,
        concentrations: jnp.ndarray
    ) -> jnp.ndarray:
        conc_embeds = ConcentrationEncoder(embed_dim=64)(concentrations)
        combined = jnp.concatenate([node_embeds, conc_embeds], axis=-1)
        combined = nn.Dense(self.embed_dim)(combined)
        
        head_dim = self.embed_dim // self.num_heads
        Q = nn.Dense(self.embed_dim)(combined)
        K = nn.Dense(self.embed_dim)(combined)
        V = nn.Dense(self.embed_dim)(combined)
        
        attention_weights = jnp.einsum('nd,md->nm', Q, K) / jnp.sqrt(head_dim)
        conc_weights = concentrations[:, None] * concentrations[None, :]
        attention_weights = attention_weights + conc_weights * 0.1
        attention_weights = nn.softmax(attention_weights, axis=1)
        
        attended = jnp.einsum('nm,md->nd', attention_weights, V)
        output = nn.Dense(self.embed_dim)(attended)
        
        return nn.LayerNorm()(node_embeds + output)

# ============================================================================
# OPTIMIZER
# ============================================================================

class MaxEffectivenessOptimizer:
    """
    Maximum Clinical Effectiveness Optimizer.
    
    Combines neural hypergraph embeddings with gradient-based optimization
    to find optimal ingredient concentrations.
    """
    
    def __init__(
        self,
        ingredients: List[Ingredient],
        targets: List[ClinicalTarget],
        embed_dim: int = 256,
        seed: int = 42
    ):
        self.ingredients = ingredients
        self.targets = targets
        self.embed_dim = embed_dim
        self.rng = random.PRNGKey(seed)
        
        self.n_ingredients = len(ingredients)
        self.n_targets = len(targets)
        
        # Initialize embeddings
        self.rng, key1, key2 = random.split(self.rng, 3)
        self.ingredient_embeds = random.normal(key1, (self.n_ingredients, embed_dim)) * 0.1
        self.target_embeds = random.normal(key2, (self.n_targets, embed_dim)) * 0.1
        
        # Concentration bounds
        self.min_conc = jnp.array([ing.min_conc for ing in ingredients])
        self.max_conc = jnp.array([ing.max_conc for ing in ingredients])
        self.optimal_conc = jnp.array([ing.optimal_conc for ing in ingredients])
        
        # Target weights
        self.target_weights = jnp.array([t.weight for t in targets])
        
        # Molecular properties
        self.mw = jnp.array([ing.mw for ing in ingredients])
        self.log_p = jnp.array([ing.log_p for ing in ingredients])
        
        # Interaction matrix (learned bilinear form)
        self.rng, key3 = random.split(self.rng)
        self.interaction_matrix = random.normal(key3, (embed_dim, embed_dim)) * 0.01
        
        # Known synergies
        self._setup_known_interactions()
    
    def _setup_known_interactions(self):
        """Setup known synergy/antagonism pairs."""
        self.synergies = {
            ('L-Ascorbic Acid', 'Tocopherol', 'Ferulic Acid'): 1.8,
            ('Niacinamide', 'Tretinoin'): 1.3,
            ('Hyaluronic Acid', 'Matrixyl 3000'): 1.2,
        }
        self.antagonisms = {
            ('Tretinoin', 'Glycolic Acid'): 0.7,
        }
    
    def compute_permeability(self, mw: jnp.ndarray, log_p: jnp.ndarray) -> jnp.ndarray:
        """Potts-Guy equation for skin permeability."""
        log_kp = -2.7 + 0.71 * log_p - 0.0061 * mw
        return jnp.power(10.0, log_kp)
    
    def compute_penetration(
        self,
        concentrations: jnp.ndarray,
        target_depth: float
    ) -> jnp.ndarray:
        """Compute penetration probability to target layer."""
        kp = self.compute_permeability(self.mw, self.log_p)
        lambda_pen = 100.0 * (1 + jnp.clip(self.log_p, -2, 10))
        penetration = kp * concentrations * jnp.exp(-target_depth / lambda_pen)
        return jnp.clip(penetration, 0.0, 1.0)
    
    def compute_interaction_factor(
        self,
        concentrations: jnp.ndarray
    ) -> float:
        """Compute synergy/antagonism factor."""
        # Bilinear interaction scores
        scores = jnp.einsum(
            'id,de,je->ij',
            self.ingredient_embeds,
            self.interaction_matrix,
            self.ingredient_embeds
        )
        
        # Weight by concentration product
        conc_weights = concentrations[:, None] * concentrations[None, :]
        mask = 1.0 - jnp.eye(self.n_ingredients)
        
        weighted_scores = scores * conc_weights * mask
        total_weight = jnp.sum(conc_weights * mask) + 1e-8
        avg_score = jnp.sum(weighted_scores) / total_weight
        
        # Apply known synergies (C+E+Ferulic)
        c_idx = next(i for i, ing in enumerate(self.ingredients) if 'Ascorbic' in ing.name)
        e_idx = next(i for i, ing in enumerate(self.ingredients) if 'Tocopherol' in ing.name)
        f_idx = next(i for i, ing in enumerate(self.ingredients) if 'Ferulic' in ing.name)
        
        cef_active = (concentrations[c_idx] > 5) & (concentrations[e_idx] > 0.3) & (concentrations[f_idx] > 0.3)
        synergy_boost = jnp.where(cef_active, 0.15, 0.0)
        
        return 1.0 + 0.3 * jnp.tanh(avg_score) + synergy_boost
    
    def compute_effectiveness(
        self,
        concentrations: jnp.ndarray
    ) -> Tuple[float, jnp.ndarray]:
        """Compute total effectiveness score."""
        # Formulation embedding (concentration-weighted)
        weights = concentrations / (concentrations.sum() + 1e-8)
        formulation_embed = jnp.einsum('n,nd->d', weights, self.ingredient_embeds)
        
        # Similarity to targets
        similarities = jnp.einsum('d,td->t', formulation_embed, self.target_embeds)
        norm_form = jnp.linalg.norm(formulation_embed) + 1e-8
        norm_targets = jnp.linalg.norm(self.target_embeds, axis=-1) + 1e-8
        similarities = similarities / (norm_form * norm_targets)
        
        # Base effectiveness (sigmoid)
        base_effectiveness = 1 / (1 + jnp.exp(-similarities * 5))
        
        # Penetration factors per target
        penetration_factors = []
        for target in self.targets:
            depth = LAYER_DEPTHS.get(target.target_layer, 100.0)
            pen = self.compute_penetration(concentrations, depth)
            penetration_factors.append(pen.mean())
        penetration_factors = jnp.array(penetration_factors)
        
        # Interaction factor
        interaction = self.compute_interaction_factor(concentrations)
        
        # Per-target scores
        target_scores = base_effectiveness * penetration_factors * interaction
        
        # Weighted total
        total = jnp.sum(self.target_weights * target_scores)
        
        return total, target_scores
    
    def constraint_penalty(self, concentrations: jnp.ndarray) -> float:
        """Compute constraint violation penalty."""
        penalty = 0.0
        
        # Total = 100%
        total = concentrations.sum()
        penalty += 100.0 * (total - 100.0) ** 2
        
        # Min concentrations (for active ingredients)
        below_min = jnp.maximum(0, self.min_conc - concentrations)
        penalty += 10.0 * jnp.sum(below_min ** 2)
        
        # Max concentrations
        above_max = jnp.maximum(0, concentrations - self.max_conc)
        penalty += 100.0 * jnp.sum(above_max ** 2)
        
        # Non-negativity
        negative = jnp.maximum(0, -concentrations)
        penalty += 1000.0 * jnp.sum(negative ** 2)
        
        return penalty
    
    def objective(self, concentrations: jnp.ndarray) -> float:
        """Objective function (minimize negative effectiveness + penalty)."""
        effectiveness, _ = self.compute_effectiveness(concentrations)
        penalty = self.constraint_penalty(concentrations)
        return -effectiveness + penalty
    
    def generate_optimal_formulation(
        self,
        num_iterations: int = 500,
        learning_rate: float = 0.5
    ) -> Dict:
        """Run optimization to find optimal formulation."""
        print("=" * 70)
        print("MAXIMUM EFFECTIVENESS FORMULATION OPTIMIZATION")
        print("=" * 70)
        print(f"Optimizing {self.n_ingredients} ingredients for {self.n_targets} targets")
        
        # Initialize at optimal concentrations, scaled to 100%
        concentrations = self.optimal_conc.copy()
        concentrations = concentrations * (100.0 / concentrations.sum())
        
        # Setup optimizer
        warmup_steps = min(50, num_iterations // 4)
        decay_steps = max(1, num_iterations - warmup_steps)
        schedule = optax.warmup_cosine_decay_schedule(
            init_value=learning_rate,
            peak_value=learning_rate * 2,
            warmup_steps=warmup_steps,
            decay_steps=decay_steps,
            end_value=learning_rate * 0.01
        )
        optimizer = optax.adam(learning_rate=schedule)
        opt_state = optimizer.init(concentrations)
        
        best_concentrations = concentrations
        best_effectiveness = -float('inf')
        
        for i in range(num_iterations):
            # Compute gradients
            loss, grads = jax.value_and_grad(self.objective)(concentrations)
            
            # Update
            updates, opt_state = optimizer.update(grads, opt_state, concentrations)
            concentrations = optax.apply_updates(concentrations, updates)
            
            # Project to feasible region
            concentrations = jnp.clip(concentrations, 0.0, self.max_conc)
            
            # Track best
            effectiveness, _ = self.compute_effectiveness(concentrations)
            if effectiveness > best_effectiveness:
                best_effectiveness = effectiveness
                best_concentrations = concentrations.copy()
            
            if i % 100 == 0:
                interaction = self.compute_interaction_factor(concentrations)
                print(f"Iteration {i:4d} | Effectiveness: {effectiveness:.4f} | "
                      f"Interaction: {interaction:.3f} | Loss: {loss:.4f}")
        
        # Final results
        final_effectiveness, target_scores = self.compute_effectiveness(best_concentrations)
        interaction = self.compute_interaction_factor(best_concentrations)
        
        return {
            'concentrations': best_concentrations,
            'effectiveness': float(final_effectiveness),
            'target_scores': target_scores,
            'interaction_factor': float(interaction),
            'formulation': self._format_formulation(best_concentrations, target_scores)
        }
    
    def _format_formulation(
        self,
        concentrations: jnp.ndarray,
        target_scores: jnp.ndarray
    ) -> str:
        """Format formulation as readable output."""
        lines = []
        lines.append("\n" + "=" * 70)
        lines.append("OPTIMAL FORMULATION")
        lines.append("=" * 70)
        
        # Formulation table
        lines.append(f"\n{'Ingredient':<25} {'INCI Name':<30} {'Concentration':>12}")
        lines.append("-" * 70)
        
        sorted_indices = sorted(range(len(concentrations)), 
                               key=lambda i: float(concentrations[i]), reverse=True)
        
        total = 0.0
        for idx in sorted_indices:
            conc = float(concentrations[idx])
            if conc > 0.001:
                ing = self.ingredients[idx]
                lines.append(f"{ing.name:<25} {ing.inci_name:<30} {conc:>11.3f}%")
                total += conc
        
        lines.append("-" * 70)
        lines.append(f"{'TOTAL':<56} {total:>11.3f}%")
        
        # Target scores
        lines.append("\n" + "=" * 70)
        lines.append("EFFECTIVENESS BY TARGET")
        lines.append("=" * 70)
        
        for i, target in enumerate(self.targets):
            score = float(target_scores[i])
            lines.append(f"{target.name:<25} | Score: {score:.4f} (weight={target.weight:.2f})")
        
        return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description='SkinForm Maximum Effectiveness Optimizer')
    parser.add_argument('--iterations', type=int, default=500, help='Number of optimization iterations')
    parser.add_argument('--learning-rate', type=float, default=0.5, help='Learning rate')
    args = parser.parse_args()
    
    print("=" * 70)
    print("   SKINFORM MAXIMUM CLINICAL EFFECTIVENESS FORMULATION SYSTEM")
    print("   CEO Subsystem (Cognitive Execution Orchestration)")
    print("=" * 70)
    print("\nUse Case: Ultimate Anti-Aging Treatment Serum")
    print("Constraint: MAXIMUM CLINICAL EFFECTIVENESS (no budget limit)\n")
    
    optimizer = MaxEffectivenessOptimizer(
        ingredients=GOLD_STANDARD_INGREDIENTS,
        targets=ANTI_AGING_TARGETS,
        embed_dim=256
    )
    
    result = optimizer.generate_optimal_formulation(
        num_iterations=args.iterations,
        learning_rate=args.learning_rate
    )
    
    print(result['formulation'])
    print(f"\n{'=' * 70}")
    print(f"FINAL EFFECTIVENESS SCORE: {result['effectiveness']:.4f}")
    print(f"INTERACTION FACTOR: {result['interaction_factor']:.3f}")
    print("=" * 70)


if __name__ == '__main__':
    main()
