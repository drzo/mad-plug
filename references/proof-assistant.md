# Proof Assistant API Reference

Formal verification system for skincare formulation hypotheses using multi-scale modeling.

## Table of Contents
1. [Overview](#overview)
2. [Multi-Scale Types](#multi-scale-types)
3. [CEO Subsystem](#ceo-subsystem)
4. [Verification Engine](#verification-engine)
5. [Cognitive Agents](#cognitive-agents)

## Overview

The SKIN-TWIN Proof Assistant provides formal verification for:
- Ingredient compatibility claims
- Multi-scale skin model predictions
- Formulation optimization hypotheses
- Penetration and efficacy modeling

## Multi-Scale Types

### Scale Hierarchy

```typescript
type ScaleType = 'molecular' | 'cellular' | 'tissue' | 'organ' | 'system';
```

| Scale | Focus | Examples |
|-------|-------|----------|
| `molecular` | Chemical interactions | Bond formation, pH effects |
| `cellular` | Cell-level effects | Receptor binding, signaling |
| `tissue` | Tissue responses | Barrier function, hydration |
| `organ` | Organ-level outcomes | Skin appearance, elasticity |
| `system` | Systemic effects | Absorption, metabolism |

### MultiscaleField Interface

```typescript
interface MultiscaleField {
  scale: ScaleType;
  data: number[];
  dimensions: {
    spatial: number[];    // [x, y, z] dimensions
    temporal: number;     // Time resolution
  };
  metadata: {
    units: string;
    description: string;
  };
  properties?: Record<string, unknown>;
  
  // Computed properties
  min?: number;
  max?: number;
  mean?: number;
  variance?: number;
}
```

### Scale Transitions

```typescript
interface ScaleTransition {
  from: ScaleType;
  to: ScaleType;
  operator: string;       // Transformation operator
  preserves?: string[];   // Properties preserved across scales
}
```

## CEO Subsystem

The Cognitive Execution Orchestrator (CEO) handles high-level cognitive operations.

### Initialization

```typescript
import { getCEO } from '~/lib/ceo';

const ceo = getCEO();
```

### Formulation Analysis

```typescript
const result = await ceo.orchestrateFormulationAnalysis(
  ingredients,      // Array of ingredient objects
  targetEffects,    // Array of target effect objects
  context           // Optional cognitive context
);

// Result structure:
interface CognitiveExecutionResult {
  task_id: string;
  status: 'success' | 'failure';
  result?: {
    interactions: any[];
    scale_effects: any;
    quality: {
      overall_score: number;
      efficacy_score: number;
      safety_score: number;
      stability_score: number;
    };
  };
  metrics: {
    execution_time_ms: number;
    memory_used_mb: number;
    cpu_utilization: number;
  };
  insights?: string[];
  recommendations?: string[];
  error?: string;
}
```

### Formulation Optimization

```typescript
interface FormulationOptimizationRequest {
  current_formulation: any;
  target_properties: any[];
  constraints: any[];
  optimization_method: string;
  max_iterations: number;
}

const result = await ceo.optimizeFormulation(request);

// Result structure:
interface FormulationOptimizationResult {
  optimized_formulation: any;
  objective_value: number;
  iterations: number;
  convergence_status: 'converged' | 'max_iterations';
  optimization_history: Array<{
    iteration: number;
    objective_value: number;
    gradient_norm: number;
  }>;
}
```

### Multi-Scale Analysis

```typescript
interface MultiScaleAnalysisRequest {
  fields: MultiscaleField[];
  analysis_type: string;
  scales_to_analyze: string[];
  cross_scale_interactions: boolean;
}

const result = await ceo.performMultiScaleAnalysis(request);

// Result structure:
interface MultiScaleAnalysisResult {
  correlations: any[];
  causal_relationships: any[];
  emergent_properties: any[];
  insights: string[];
}
```

### Skin Condition Prediction

```typescript
interface SkinConditionPredictionRequest {
  features: any;
  conditions_to_predict: string[];
  time_horizon_days: number;
}

const result = await ceo.predictSkinConditions(request);

// Result structure:
interface SkinConditionPredictionResult {
  predictions: Array<{
    condition: string;
    probability: number;
    confidence_interval: [number, number];
    risk_factors: string[];
    protective_factors: string[];
  }>;
  recommendations: Array<{
    action: string;
    priority: 'high' | 'medium' | 'low';
    expected_benefit: string;
  }>;
}
```

## Verification Engine

### Proof Verification Request

Include in formulation responses to invoke verification:

```
**PROOF VERIFICATION REQUEST:**
Hypothesis: [Your formulation hypothesis]
Ingredients: [List of ingredients to verify]
Target Effects: [Expected outcomes]
```

### Example Verification

```
**PROOF VERIFICATION REQUEST:**
Hypothesis: "Combining 2% niacinamide with 1% hyaluronic acid will enhance skin barrier function through synergistic hydration mechanisms"
Ingredients: Niacinamide, Sodium Hyaluronate, Glycerin
Target Effects: Improved hydration, enhanced barrier function, reduced transepidermal water loss
```

### Verification Components

The proof assistant integrates:

1. **Formal Logic** - Propositional and predicate logic for ingredient compatibility
2. **Tensor Operations** - Multi-scale field transformations
3. **Hypergraph Analysis** - Network-based interaction verification
4. **Cognitive Accounting** - Relevance realization for ingredient selection

## Cognitive Agents

### Deep Tree Echo

**Role**: Novelty, primes, exploration (Right hemisphere)

**Use for**:
- Creative formulation ideation
- Novel ingredient combinations
- Exploring unconventional approaches

**Prompt file**: `deep-tree-echo.prompt.yml`

**Key characteristics**:
- Navigates recursive patterns
- Explores uncharted domains
- Emphasizes curiosity and growth

### Marduk

**Role**: Metric tensor, synthesis, production (Left hemisphere)

**Use for**:
- Systematic formulation architecture
- Process optimization
- Production-ready formulations

**Prompt file**: `marduk.prompt.yml`

**Key characteristics**:
- Distills chaos into coherent frameworks
- Builds persistent memory systems
- Focuses on actionable processes

### Agent Integration

The two agents form a complementary system:

| Aspect | Deep Tree Echo | Marduk |
|--------|----------------|--------|
| Orientation | Exploration | Synthesis |
| Focus | Novelty | Production |
| Output | Ideas | Blueprints |
| Metaphor | Right hemisphere | Left hemisphere |

Use Deep Tree Echo for ideation, then Marduk for systematization.
