# mad-plug — Cognitive Capability Marketplace

**mad-plug** is a GitHub Copilot plugin marketplace built on the COG253 Unified Skill Lattice.
It maps cognitive capabilities to Christopher Alexander's 253-pattern topology, enabling
navigation, discovery, and composition of skills across ecosystem, component, and implementation
hierarchies.

---

## What is mad-plug?

mad-plug provides 7 plugins that extend GitHub Copilot with specialized cognitive tools:

| Plugin | Category | Description |
|---|---|---|
| `pattern-navigator` | Pattern Recognition | Query and traverse the APL253 pattern topology |
| `skill-composer` | Skill Engineering | Decompose, transform, and compose skills across domains |
| `template-generator` | Code Generation | Scaffold skills, extensions, and projects from templates |
| `language-creator` | Language Design | Design DSLs with grammar definitions and validation |
| `cognitive-kernel` | Cognitive Computing | Build Plan 9 / Inferno-OS cognitive kernels |
| `formulation-analyzer` | Scientific Computing | Analyze and optimize formulations and brain models |
| `spark` | Code Generation | Opinionated guidance for modern web application stacks |

---

## Installation

### Prerequisites
- GitHub Copilot CLI or Copilot-enabled editor
- Node.js 18+
- Python 3.10+ (for tool backend scripts)

### Install

Clone the repository and load plugins from the `.github/extensions/` directory:

```bash
git clone https://github.com/drzo/mad-plug.git
cd mad-plug
```

Each plugin is auto-discovered from `.github/extensions/<name>/extension.mjs`.

---

## Available Plugins

### pattern-navigator
Navigate the GH253 pattern topology — 253 patterns mapped to GitHub/software domains.

```
pattern_query       — Query by ID, search term, or relationship
pattern_transform   — Map APL patterns to GitHub domains
pattern_relationships — Explore connected design decisions
```

### skill-composer
Decompose, transform, and compose skills using structural analogy and GRT.

```
skill_decompose         — Extract abstract template + domain bindings
skill_transform         — Port a skill to a new domain
skill_chain_transforms  — Multi-hop domain transfer
skill_apply_grt         — Apply the General Relevance Transform
skill_share_template    — Publish a skill template as a reusable scaffold
```

### template-generator
Scaffold new skills and extensions from curated templates.

```
template_new_skill      — Create a new skill with proper structure
template_new_extension  — Scaffold a Copilot extension
```

### language-creator (dsl-factory)
Design and create domain-specific languages end-to-end.

```
dsl_init_language   — Initialize a new language project
dsl_define_grammar  — Define grammar via prime grammar specs
dsl_emit_grammar    — Emit grammar files (PEG, BNF, ANTLR)
dsl_extract_lexicon — Extract terminology from corpora
dsl_validate        — Validate a language project
```

### cognitive-kernel
Build and operate Plan 9 / Inferno-OS cognitive development kernels.

```
cogkernel_build               — Build a cognitive kernel
cogkernel_distributed_inference — Configure distributed inference
cogkernel_cluster             — Manage compute clusters
cogkernel_daemon              — Operate cognitive service daemons
```

### formulation-analyzer
Analyze formulations, generate brain models, and perform numerical analysis.

```
formulation_analyze            — Analyze skincare/chemical formulations
formulation_optimize           — Neural hypergraph optimization
formulation_lookup_ingredient  — Ingredient safety & compatibility lookup
formulation_generate_topology  — Generate neural network topologies
formulation_brain_model        — Generate brain-inspired models
formulation_continued_fractions — Continued fraction analysis
```

### spark
Opinionated guidance for building modern web applications.

```
spark_get_stack      — Get stack details for a complexity tier
spark_list_stacks    — List all available stack variations
spark_get_reference  — Retrieve a reference document (design system, etc.)
```

---

## How to Use

1. Load the plugin you need via your Copilot-enabled tool
2. Invoke tools using their snake_case names with the described parameters
3. Combine tools across plugins for complex workflows (e.g., navigate a pattern → decompose a skill → scaffold a new extension)

---

## Conventions

See [AGENTS.md](AGENTS.md) for full plugin development conventions including commit rules,
directory structure requirements, and quality expectations.

---

## Marketplace Index

See [marketplace-index.json](marketplace-index.json) for the categories/tags taxonomy used
for plugin discovery.

---

## License

MIT — see [LICENSE](LICENSE)
