# COSING Formulation Patterns Guide

Reference for the 2,498 formulation patterns derived from the EU COSING cosmetic ingredient database.

## Table of Contents
1. [Pattern Overview](#pattern-overview)
2. [Pattern Categories](#pattern-categories)
3. [FormulationPatternManager API](#formulationpatternmanager-api)
4. [Pattern Structure](#pattern-structure)
5. [Usage Examples](#usage-examples)

## Pattern Overview

**Statistics:**
- Total Ingredients Analyzed: 12,070
- Atomic Functions: 80
- Function Combinations: 2,498
- Formulation Patterns: 2,498
- Most Common Function: SKIN CONDITIONING
- Average Functions/Ingredient: 1.75

## Pattern Categories

| Category | Count | Percentage | Description |
|----------|-------|------------|-------------|
| `BASE_FORMING` | 588 | 23.5% | Water, glycerin, carriers, solvents |
| `EMULSIFICATION` | 489 | 19.6% | Surfactants, emulsifiers, stabilizers |
| `ACTIVE_DELIVERY` | 914 | 36.6% | Actives, penetration enhancers, boosters |
| `PRESERVATION` | 209 | 8.4% | Preservative systems, antimicrobials |
| `SENSORY_ENHANCEMENT` | 105 | 4.2% | Texture modifiers, fragrance, feel |
| `FUNCTIONAL_SPECIALTY` | 193 | 7.7% | Specialized functions, UV filters |

## FormulationPatternManager API

### Initialization

```typescript
import { FormulationPatternManager } from '~/lib/vessels/formulation-patterns';
import patternData from '~/vessels/cosing/formulation_patterns.json';

const manager = new FormulationPatternManager(patternData);
```

### Core Methods

#### findByCategory(category)
Find patterns by category.
```typescript
const basePatterns = manager.findByCategory(PatternCategory.BASE_FORMING);
```

#### findByFunctions(functions)
Find patterns containing specific functions.
```typescript
const humectants = manager.findByFunctions(['HUMECTANT', 'SKIN CONDITIONING']);
```

#### getMostCommon(limit)
Get most frequently used patterns.
```typescript
const topPatterns = manager.getMostCommon(10);
```

#### findByComplexity(min, max)
Find patterns by complexity score.
```typescript
const simplePatterns = manager.findByComplexity(1, 3);
const complexPatterns = manager.findByComplexity(7, 10);
```

#### getSimplePatterns(limit)
Get simple, high-frequency patterns.
```typescript
const easyPatterns = manager.getSimplePatterns(20);
```

#### findByApplication(application)
Find patterns for product types.
```typescript
const serumPatterns = manager.findByApplication('serum');
const moisturizerPatterns = manager.findByApplication('moisturizer');
```

#### suggestFormulationTemplate(productType)
Get complete formulation template.
```typescript
const template = manager.suggestFormulationTemplate('moisturizer');
// Returns: { base, emulsification, actives, preservation, sensory }
```

#### checkCompatibility(patternIds)
Validate pattern combinations.
```typescript
const result = manager.checkCompatibility(['FP_SC', 'FP_H', 'FP_AM']);
// Returns: { compatible: boolean, warnings: string[], suggestions: string[] }
```

#### generateFormulationReport(patternIds)
Generate comprehensive report.
```typescript
const report = manager.generateFormulationReport(['FP_SC', 'FP_H']);
// Returns: { patterns, total_functions, categories, concentration_range, 
//            compatibility_check, recommended_ingredients }
```

#### search(keyword)
Search patterns by keyword.
```typescript
const uvPatterns = manager.search('UV protection');
const antiAgingPatterns = manager.search('anti-aging');
```

#### findRelatedPatterns(patternId, limit)
Find similar patterns.
```typescript
const related = manager.findRelatedPatterns('FP_SC_H', 5);
```

## Pattern Structure

```typescript
interface FormulationPattern {
  id: string;                          // e.g., "FP_SC_H"
  name: string;                        // Human-readable name
  functions: string[];                 // COSING functions
  function_count: number;              // Number of functions
  typical_applications: string[];      // Product types
  ingredient_examples: string[];       // Example ingredients
  usage_frequency: number;             // How often used
  complexity_score: number;            // 1-10 complexity
  category: PatternCategory;           // Category enum
  recommended_concentration_range: {
    min: number;                       // Minimum %
    max: number;                       // Maximum %
  };
  synergistic_patterns: string[];      // Compatible patterns
  incompatible_patterns: string[];     // Avoid combining
}
```

## Usage Examples

### 1. Find Moisturizer Patterns

```typescript
// Search patterns by category
const basePatterns = manager.findByCategory(PatternCategory.BASE_FORMING);
console.log(`Found ${basePatterns.length} base forming patterns`);

// Find specific functional combinations
const humectantPatterns = manager.findByFunctions(['HUMECTANT']);
console.log(`Found ${humectantPatterns.length} humectant patterns`);

// Identify preservation systems
const preservationPatterns = manager.findByCategory(PatternCategory.PRESERVATION);
console.log(`Found ${preservationPatterns.length} preservation patterns`);
```

### 2. Build Formulation Template

```typescript
const template = manager.suggestFormulationTemplate('moisturizer');

console.log('Base patterns:', template.base.map(p => p.name));
console.log('Active patterns:', template.actives.map(p => p.name));
console.log('Preservation:', template.preservation.map(p => p.name));
console.log('Sensory:', template.sensory.map(p => p.name));
```

### 3. Check Pattern Compatibility

```typescript
const selectedPatterns = ['FP_SC', 'FP_H', 'FP_AM', 'FP_PRES'];
const compatibility = manager.checkCompatibility(selectedPatterns);

if (!compatibility.compatible) {
  console.log('Issues:', compatibility.warnings);
  console.log('Suggestions:', compatibility.suggestions);
}
```

### 4. Generate Formulation Report

```typescript
const report = manager.generateFormulationReport(['FP_SC', 'FP_H', 'FP_PRES']);

console.log('Total functions:', report.total_functions);
console.log('Concentration range:', report.concentration_range);
console.log('Recommended ingredients:', report.recommended_ingredients);
```

### 5. Search and Explore

```typescript
// Keyword search
const uvPatterns = manager.search('UV protection');
const antiAgingPatterns = manager.search('anti-aging');

// Find simple, high-frequency patterns
const simplePatterns = manager.getSimplePatterns(20);

// Discover related patterns
const related = manager.findRelatedPatterns('FP_SC_H', 5);
```

### 6. Category Analysis

```typescript
const categories = [
  PatternCategory.BASE_FORMING,
  PatternCategory.EMULSIFICATION,
  PatternCategory.ACTIVE_DELIVERY,
  PatternCategory.PRESERVATION,
  PatternCategory.SENSORY_ENHANCEMENT,
  PatternCategory.FUNCTIONAL_SPECIALTY
];

categories.forEach(cat => {
  const patterns = manager.findByCategory(cat);
  console.log(`${cat}: ${patterns.length} patterns`);
});
```

## Regenerating Patterns

If the COSING database is updated:

```bash
npx tsx scripts/generate-formulation-patterns.ts
```

This ensures patterns reflect the latest ingredient data.
