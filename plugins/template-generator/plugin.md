---
name: template-generator
description: >
  Scaffold new projects, skills, extensions, and devcontainers from curated templates.
  Supports Lua/nn modules, Plan 9 environments, WASM web workers, cognitive kernels,
  and general-purpose project structures.
tools:
  - scripts/new-skill.sh
  - scripts/new-extension.sh
resources:
  - templates/
  - template/
---

# Template Generator Plugin

Scaffolds new projects and components from the repository's curated template library.

## Capabilities

- **Scaffold skills** with proper frontmatter, directory structure, and placeholder content
- **Create extensions** with the standard extension layout
- **Generate projects** from specialized templates:
  - `.devcontainer` — Development container configurations
  - `.plan9-devenv` — Plan 9 development environments
  - `daemon` — Background service templates
  - `kernel` — Cognitive kernel scaffolds
  - `llama-arm64-minimal` — Minimal LLM inference for ARM64
  - `wasm-web-worker` — WebAssembly web worker projects
  - `ecommerce-hub` — E-commerce application templates
  - `topology_weaver` — Neural network topology generators

## Usage

Invoke when the user asks about:
- Creating a new skill ("scaffold a skill called X")
- Starting a new project ("generate a WASM web worker project")
- Setting up development environments ("create a Plan 9 devcontainer")
- Extension authoring ("create a new extension")

## Template Inventory

The `templates/` directory contains full project scaffolds.
The `template/` directory contains Lua/Torch7 nn module templates.
