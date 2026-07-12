# skill-composer

Decompose, transform, and compose skills across domains using structural analogy and the General Relevance Transform (GRT). Extract abstract skill templates, port them to new domains, chain multi-hop transformations, and share reusable scaffolds.

**Version:** 0.1.0 | **Category:** Skill Engineering | **Tags:** `skill` `composition` `transform` `analogy`

---

## Description

`skill-composer` provides a pipeline for working with skills as composable, transformable artifacts. Given a skill directory (containing a SKILL.md), it can extract an abstract template that captures the skill's structure independent of domain, then apply structural analogy to map that template to any target domain. The General Relevance Transform (GRT) enables principled cross-domain skill transfer.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `skill_decompose` | Extract abstract template + domain bindings from a skill | `skill_path` |
| `skill_transform` | Map a template to a new domain via structural analogy | `template_path`, `target_domain` |
| `skill_chain_transforms` | Multi-hop domain transfer through a chain of domains | `skill_path`, `domains` |
| `skill_apply_grt` | Apply the General Relevance Transform | `source`, `target_context` |
| `skill_share_template` | Publish a skill template as a reusable scaffold | `template_path` |

---

## Usage Examples

### Decompose a skill into its abstract template
```
skill_decompose(skill_path="skills/my-skill", output="output/templates")
```
Produces `template_manifest.yaml` and `domain_bindings.yaml` in the output directory.

### Transform a skill to a new domain
```
skill_transform(template_path="output/templates/template_manifest.yaml", target_domain="rust", output="skills/rust-skill")
```
Generates a new skill directory adapted for the Rust domain.

### Chain multiple domain transformations
```
skill_chain_transforms(skill_path="skills/python-skill", domains="javascript,typescript,react")
```
Walks through Python → JavaScript → TypeScript → React, producing intermediate skill artifacts at each hop.

### Apply the General Relevance Transform
```
skill_apply_grt(source="skills/pattern-navigator", target_context="graph-database")
```
Identifies which structural elements of `pattern-navigator` are relevant to a graph-database context.

---

## Dependencies

None

---

## Scripts

Backend Python scripts in `scripts/`:
- `decompose_skill.py` — template extraction
- `transform_skill.py` — domain mapping via structural analogy
- `chain_transforms.py` — multi-hop transformation pipeline
- `apply_grt.py` — General Relevance Transform
- `share_template.py` — template publication
