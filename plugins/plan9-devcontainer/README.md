# plan9-devcontainer

Optimal devcontainer configuration for Plan 9 from Bell Labs / 9front development. Use when setting up Plan 9 development environments, configuring acme/sam IDE toolchains, deploying distributed CPU server grids via QEMU, building Plan 9 C programs with mk, or creating devcontainer.json for Plan 9 projects. Provides Dockerfile with plan9port and QEMU, docker-compose for CPU server grids, CLI tools, and grid management. Transformed from inferno-devcontainer via function-creator.

**Version:** 0.1.0 | **Category:** skill-engineering | **Tags:** `transform` `distributed` `plan9` `inferno`

---

## Description

Provision a complete Plan 9 from Bell Labs development environment inside a devcontainer with plan9port tools (acme, sam, mk, rc), QEMU for running native Plan 9/9front, distributed CPU server grid support, and CLI tools.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `plan9_devcontainer_guide` | Provide guidance on plan9-devcontainer topics | `topic` |

---

## Usage Examples

### Get guidance on a topic
```
plan9_devcontainer_guide(topic="core concepts")
```
Returns structured guidance about the core concepts from the plan9-devcontainer knowledge base.

### Get guidance with context
```
plan9_devcontainer_guide(topic="implementation", context="production deployment")
```
Returns guidance narrowed to the specific context provided.

---

## Dependencies

None

---

## Version

0.1.0

---

## Category & Tags

Category: `skill-engineering`

Tags: `transform` `distributed` `plan9` `inferno`
