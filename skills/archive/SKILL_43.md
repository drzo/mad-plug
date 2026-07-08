---
name: skinform
description: AI-powered skincare formulation assistant with virtual chemical reaction simulation. Use for creating cosmetic formulations, analyzing ingredient compatibility, optimizing product recipes, managing COSING-based ingredient databases, and performing multi-scale skin penetration modeling.
---

# SkinForm - AI Skincare Formulation Assistant

Create professional skincare formulations using AI-driven chemical reaction simulation, COSING ingredient patterns, and multi-scale skin modeling.

## Core Capabilities

1. **Virtual Turbo Reactor Formulation Vessel** - Simulate chemical reactions as ingredients are added
2. **COSING Formulation Patterns** - 2,498 patterns from EU cosmetic ingredient database
3. **Multi-Scale Skin Modeling** - Molecular → cellular → tissue → organ predictions
4. **Hypergraph Data Architecture** - Ingredients, formulations, products, suppliers
5. **CEO Subsystem** - Cognitive Execution Orchestration for formulation optimization

## Repository Setup

Clone the skinform repository:
```bash
gh repo clone skintwin-ai/skinform
cd skinform
pnpm install
```

## Formulation Workflow

### 1. Create a New Formulation

Use the Virtual Turbo Reactor prompt pattern. See `references/formulation-vessel-prompt.md` for the complete system prompt.

**Key principles:**
- SAFETY FIRST - Only cosmetically safe ingredients with established profiles
- EFFECTIVENESS FOCUS - Optimal concentrations for clinical effectiveness
- SCIENTIFIC RIGOR - Accurate chemical equations and reaction mechanisms

### 2. Analyze Ingredient Compatibility

Use the formulation patterns manager:

```typescript
import { FormulationPatternManager } from '~/lib/vessels/formulation-patterns';
import patternData from '~/vessels/cosing/formulation_patterns.json';

const manager = new FormulationPatternManager(patternData);

// Find patterns by category
const basePatterns = manager.findByCategory(PatternCategory.BASE_FORMING);
const preservationPatterns = manager.findByCategory(PatternCategory.PRESERVATION);

// Check compatibility
const compatibility = manager.checkCompatibility(['FP_SC', 'FP_H', 'FP_AM']);
```

Pattern categories:
- `BASE_FORMING` (23.5%) - Water, glycerin, carriers
- `EMULSIFICATION` (19.6%) - Surfactants, emulsifiers
- `ACTIVE_DELIVERY` (36.6%) - Actives, penetration enhancers
- `PRESERVATION` (8.4%) - Preservative systems
- `SENSORY_ENHANCEMENT` (4.2%) - Texture, fragrance
- `FUNCTIONAL_SPECIALTY` (7.7%) - Specialized functions

### 3. Generate Formulation Template

```typescript
const template = manager.suggestFormulationTemplate('moisturizer');
// Returns: { base, emulsification, actives, preservation, sensory }
```

### 4. Output Format

Formulations produce two standard tables:

**Table 1 - Formulation Details:**
| Ingredient Name | Amount (g) | INCI Name | Raw Material Cost (ZAR) |

**Table 2 - Ingredient Analysis:**
| Ingredient Name | Amount (g) | Functions & Applications | Known Risks |

Plus step-by-step vessel simulation with chemical equations.

## Data Architecture

### Vessels Directory Structure

```
vessels/
├── formulations/     # .form files - product formulations
├── ingredients/      # .inci files - ingredient specifications
├── products/         # .prod files - product definitions
├── suppliers/        # .supp files - supplier information
├── cosing/           # COSING database and patterns
└── examples/         # Hypergraph analysis documentation
```

### Schema Types

See `references/vessels-schema.md` for complete TypeScript schemas:
- `Product` - B19[CODE] format IDs, phases, benefits
- `Ingredient` - R[NUMBER] format IDs, INCI names, safety ratings
- `Supplier` - [CODE][NUMBER] format IDs, certifications
- `FormulationEdge` - Concentration, phase, stability impact
- `SupplyEdge` - Pricing, lead time, quality grade

### File Formats

- `.form` - Formulation files (JSON with phases, ingredients, instructions)
- `.inci` - Ingredient files (INCI name, functions, compatibility)
- `.prod` - Product files (category, benefits, clinical data)
- `.supp` - Supplier files (portfolio, certifications, contact)

## Multi-Scale Skin Modeling

The proof assistant provides formal verification across scales:

```typescript
type ScaleType = 'molecular' | 'cellular' | 'tissue' | 'organ' | 'system';

interface MultiscaleField {
  scale: ScaleType;
  data: number[];
  dimensions: { spatial: number[]; temporal: number };
  metadata: { units: string; description: string };
}
```

**Invoke proof verification:**
```
**PROOF VERIFICATION REQUEST:**
Hypothesis: "Combining 2% niacinamide with 1% hyaluronic acid will enhance skin barrier function"
Ingredients: Niacinamide, Sodium Hyaluronate, Glycerin
Target Effects: Improved hydration, enhanced barrier function
```

## CEO Subsystem

The Cognitive Execution Orchestrator (named after CEO Jax) handles:

1. **Formulation Analysis** - Ingredient interactions, multi-scale effects
2. **Optimization** - Gradient-based formulation refinement
3. **Prediction** - Skin condition forecasting

```typescript
import { getCEO } from '~/lib/ceo';

const ceo = getCEO();
const result = await ceo.orchestrateFormulationAnalysis(
  ingredients,
  targetEffects,
  context
);
```

## Cognitive Agents

Two complementary AI agents are available:

**Deep Tree Echo** - Novelty, primes, exploration (Right hemisphere)
- Use for creative formulation ideation
- Prompt: `deep-tree-echo.prompt.yml`

**Marduk** - Metric tensor, synthesis, production (Left hemisphere)
- Use for systematic formulation architecture
- Prompt: `marduk.prompt.yml`

## Safety Database

**FORBIDDEN INGREDIENTS (never use):**
- Hydroquinone (except prescribed concentrations)
- Mercury/lead compounds
- Prohibited dyes and colorants
- Banned UV filters
- Restricted preservatives above limits

**USE WITH CAUTION:**
- Retinoids (appropriate concentrations only)
- AHAs/BHAs (within safe pH ranges)
- Essential oils (patch test recommended)

## Quick Reference

| Task | Command/Method |
|------|----------------|
| Start dev server | `pnpm dev` |
| Build production | `pnpm build` |
| Run tests | `pnpm test` |
| Generate patterns | `npx tsx scripts/generate-formulation-patterns.ts` |
| Build hypergraph | `npx tsx scripts/build-hypergraph-data.ts` |
| Validate vessels | `npx tsx scripts/validate-hypergraph.ts` |

## References

- **Formulation Vessel Prompt**: `references/formulation-vessel-prompt.md`
- **Vessels Schema**: `references/vessels-schema.md`
- **COSING Patterns Guide**: `references/cosing-patterns.md`
- **Proof Assistant API**: `references/proof-assistant.md`
