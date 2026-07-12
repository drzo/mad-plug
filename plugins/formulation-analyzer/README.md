# formulation-analyzer

Analyze and optimize complex formulations spanning skincare chemistry, neural network topologies, brain-inspired computational models, and mathematical structures.

**Version:** 0.1.0 | **Category:** Scientific & Mathematical Computing | **Tags:** `formulation` `neural-network` `brain-model` `optimization` `mathematics`

---

## Description

`formulation-analyzer` applies neural hypergraph embeddings and computational neuroscience methods to a diverse set of formulation problems. It can evaluate skincare compound compatibility and safety, optimize formulations toward specific targets (stability, absorption, efficacy), generate neural network topology specifications, construct brain-inspired models, and perform continued fraction numerical analysis. The plugin bridges domains that share structural similarities in their formulation problems.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `formulation_analyze` | Analyze a formulation for compatibility and safety | `file` |
| `formulation_optimize` | Optimize a formulation using neural hypergraph embeddings | `file` |
| `formulation_lookup_ingredient` | Look up ingredient properties, safety, compatibility | `ingredient` |
| `formulation_generate_topology` | Generate a neural network topology specification | `type` |
| `formulation_brain_model` | Generate and optionally visualize brain-inspired models | `model` |
| `formulation_continued_fractions` | Compute continued fraction representations | `value` |

---

## Usage Examples

### Analyze a skincare formulation
```
formulation_analyze(file="formulations/moisturizer-v2.form")
```
Returns compatibility matrix, safety flags, and optimization opportunities.

### Optimize for absorption
```
formulation_optimize(file="formulations/moisturizer-v2.form", target="absorption")
```
Returns an optimized ingredient ratio set targeting maximum dermal absorption.

### Look up an ingredient
```
formulation_lookup_ingredient(ingredient="niacinamide")
```
Returns INCI name, safety data, pH range, compatibility notes, and concentration guidelines.

### Generate a transformer topology
```
formulation_generate_topology(type="transformer", layers="12", output="topologies/transformer-base.yaml")
```
Emits a YAML topology specification for a 12-layer transformer architecture.

### Build a hippocampal-inspired model
```
formulation_brain_model(model="hippocampal-sequence", visualize=true, output="models/hippo.json")
```
Generates the model JSON and a visualization artifact.

### Analyze a continued fraction
```
formulation_continued_fractions(value="3.14159265358979", depth="20")
```
Returns the continued fraction expansion `[3; 7, 15, 1, 292, ...]` and convergents.

---

## Dependencies

None

---

## Scripts

Python scripts in `scripts/`:
- `analyze_formulation.py` — formulation compatibility and safety analysis
- `skinform_optim.py` — neural hypergraph optimization
- `lookup_ingredient.py` — ingredient database lookup
- `generate_topology.py` — neural network topology generation
- `generate_brain_model.py` — brain-inspired model generation
- `visualize_brain.py` — model visualization
- `continued_fractions.py` — continued fraction analysis
