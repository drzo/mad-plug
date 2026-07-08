---
name: skill-composer
description: >
  Decompose, transform, and compose skills across domains. Provides tooling for
  skill templating, domain binding extraction, chain transformations, and the
  General Relevance Transform (GRT) application.
tools:
  - scripts/decompose_skill.py
  - scripts/transform_skill.py
  - scripts/chain_transforms.py
  - scripts/apply_grt.py
  - scripts/share_template.py
resources:
  - syntax_templates/
---

# Skill Composer Plugin

Provides tools for decomposing skills into abstract templates, transforming them
across domains, and composing new skills from existing building blocks.

## Capabilities

- **Decompose** a skill into its invariant template structure and domain-specific bindings
- **Transform** skills from one domain to another using structural analogy
- **Chain** multiple transformations for multi-hop domain transfer
- **Apply GRT** (General Relevance Transform) to map skill patterns to new contexts
- **Share** skill templates as reusable scaffolds

## Usage

Invoke when the user asks about:
- Creating a new skill from an existing one ("make a version of X for Y domain")
- Understanding skill structure ("what are the invariant parts of this skill?")
- Skill transformation pipelines ("chain these transformations together")
- Template extraction ("extract a reusable template from this skill")

## Architecture

```
SKILL.md → decompose → template_manifest.yaml + domain_bindings.yaml
template_manifest.yaml + new_bindings → transform → NEW_SKILL.md
```
