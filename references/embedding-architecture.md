# Neural Hypergraph Embedding Architecture

## Overview

The embedding system provides learnable representations for all entities in the SkinForm hypergraph, enabling context-dependent ingredient behavior and interaction modeling.

## Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 4: TASK-SPECIFIC HEADS                                   │
│  • Effectiveness prediction                                     │
│  • Compatibility classification                                 │
│  • Formulation generation                                       │
└─────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 3: HYPERGRAPH ATTENTION                                  │
│  • Multi-head attention over hyperedges                         │
│  • Node-to-hyperedge message passing                            │
│  • Hyperedge-to-node aggregation                                │
└─────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 2: RELATIONAL EMBEDDINGS                                 │
│  • Relation type embeddings (synergy, antagonism)               │
│  • Concentration encodings (sinusoidal)                         │
│  • Phase embeddings (aqueous, oil, active)                      │
└─────────────────────────────────────────────────────────────────┘
                              ▲
┌─────────────────────────────────────────────────────────────────┐
│  LAYER 1: BASE EMBEDDINGS                                       │
│  • Ingredient: E_ing ∈ ℝ^(12070×256)                            │
│  • Product: E_prod ∈ ℝ^(100×256)                                │
│  • Supplier: E_supp ∈ ℝ^(10×128)                                │
│  • Function: E_func ∈ ℝ^(50×128)                                │
└─────────────────────────────────────────────────────────────────┘
```

## Module Implementations

### Base Embeddings (JAX/Flax)

```python
class IngredientEmbedding(nn.Module):
    num_ingredients: int
    embed_dim: int = 256
    
    @nn.compact
    def __call__(self, ingredient_ids: jnp.ndarray) -> jnp.ndarray:
        embedding_table = self.param(
            'embedding',
            nn.initializers.normal(stddev=0.02),
            (self.num_ingredients, self.embed_dim)
        )
        return embedding_table[ingredient_ids]
```

### Concentration Encoder

Sinusoidal encoding for continuous concentration values:

```python
class ConcentrationEncoder(nn.Module):
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
```

### Hypergraph Attention Layer

```python
class HypergraphAttentionLayer(nn.Module):
    embed_dim: int = 256
    num_heads: int = 8
    dropout_rate: float = 0.1
    
    @nn.compact
    def __call__(
        self,
        node_embeds: jnp.ndarray,
        concentrations: jnp.ndarray,
        training: bool = True
    ) -> jnp.ndarray:
        # Encode concentrations
        conc_embeds = ConcentrationEncoder(embed_dim=64)(concentrations)
        
        # Combine node embeddings with concentration info
        combined = jnp.concatenate([node_embeds, conc_embeds], axis=-1)
        combined = nn.Dense(self.embed_dim)(combined)
        
        # Multi-head self-attention
        head_dim = self.embed_dim // self.num_heads
        Q = nn.Dense(self.embed_dim)(combined)
        K = nn.Dense(self.embed_dim)(combined)
        V = nn.Dense(self.embed_dim)(combined)
        
        # Concentration-modulated attention
        attention_weights = jnp.einsum('nd,md->nm', Q, K) / jnp.sqrt(head_dim)
        conc_weights = concentrations[:, None] * concentrations[None, :]
        attention_weights = attention_weights + conc_weights * 10
        attention_weights = nn.softmax(attention_weights, axis=1)
        
        attended = jnp.einsum('nm,md->nd', attention_weights, V)
        output = nn.Dense(self.embed_dim)(attended)
        
        return nn.LayerNorm()(node_embeds + output)
```

### Formulation Encoder

Aggregates ingredient embeddings into single formulation embedding:

```python
class FormulationEncoder(nn.Module):
    embed_dim: int = 256
    num_layers: int = 3
    num_heads: int = 8
    
    @nn.compact
    def __call__(
        self,
        ingredient_embeds: jnp.ndarray,
        concentrations: jnp.ndarray,
        training: bool = True
    ) -> jnp.ndarray:
        h = ingredient_embeds
        
        for i in range(self.num_layers):
            h = HypergraphAttentionLayer(
                embed_dim=self.embed_dim,
                num_heads=self.num_heads
            )(h, concentrations, training)
        
        # Concentration-weighted aggregation
        weights = concentrations / (concentrations.sum() + 1e-8)
        formulation_embed = jnp.einsum('n,nd->d', weights, h)
        
        return nn.Dense(self.embed_dim)(formulation_embed)
```

## Embedding Variations

### Hyperedge-Dependent Node Embeddings

Different embedding for same ingredient based on formulation context:

```python
class HyperedgeDependentEmbedding(nn.Module):
    embed_dim: int = 256
    
    @nn.compact
    def __call__(
        self,
        node_embed: jnp.ndarray,
        hyperedge_embed: jnp.ndarray
    ) -> jnp.ndarray:
        gate = nn.sigmoid(
            nn.Dense(self.embed_dim)(
                jnp.concatenate([node_embed, hyperedge_embed], axis=-1)
            )
        )
        modulated = nn.Dense(self.embed_dim)(
            jnp.concatenate([node_embed, hyperedge_embed], axis=-1)
        )
        return gate * node_embed + (1 - gate) * modulated
```

### Dynamic Hyperedge Weights

Learn importance weights for each formulation:

```python
class DynamicHyperedgeWeights(nn.Module):
    @nn.compact
    def __call__(
        self,
        node_embeds: jnp.ndarray,
        incidence: jnp.ndarray
    ) -> jnp.ndarray:
        hyperedge_features = jnp.einsum('nm,nd->md', incidence, node_embeds)
        hyperedge_features = hyperedge_features / (incidence.sum(axis=0, keepdims=True).T + 1e-8)
        weights = nn.Dense(1)(hyperedge_features).squeeze(-1)
        return nn.softplus(weights)
```

## Training Objectives

Multi-task loss function:

```python
def compute_loss(model_output, batch, config):
    # 1. Effectiveness prediction loss
    effectiveness_loss = binary_cross_entropy(
        model_output['effectiveness_pred'],
        batch['effectiveness_labels']
    )
    
    # 2. Compatibility prediction loss
    compatibility_loss = cross_entropy(
        model_output['compatibility_pred'],
        batch['compatibility_labels']
    )
    
    # 3. Concentration reconstruction loss
    concentration_loss = mse_loss(
        model_output['concentration_pred'],
        batch['concentrations']
    )
    
    # 4. Contrastive loss
    contrastive_loss = info_nce_loss(
        model_output['embeddings'],
        batch['positive_pairs'],
        batch['negative_pairs']
    )
    
    return (
        config['w_effectiveness'] * effectiveness_loss +
        config['w_compatibility'] * compatibility_loss +
        config['w_concentration'] * concentration_loss +
        config['w_contrastive'] * contrastive_loss
    )
```

## Hyperparameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| embed_dim | 256 | Embedding dimension |
| num_heads | 8 | Attention heads |
| num_layers | 3 | HGAT layers |
| dropout_rate | 0.1 | Dropout probability |
| learning_rate | 0.001 | Adam learning rate |
| batch_size | 32 | Training batch size |
