# dgen

Integrates with the DreamGen (dgen) API for advanced creative writing and role-playing. Use for story generation, character-based dialogue, interactive fiction, and fine-tuned control over DreamGen's `lucid-v1` models. Supports both native and OpenAI-compatible APIs.

**Version:** 0.1.0 | **Category:** cognitive-computing | **Tags:** `cognitive-computing`

---

## Description

This skill provides tools and workflows to interact with the DreamGen API, which is specialized for high-quality creative writing, role-playing, and story generation using the `lucid-v1` family of models.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `dgen_guide` | Provide guidance on dgen topics | `topic` |

---

## Usage Examples

### Get guidance on a topic
```
dgen_guide(topic="core concepts")
```
Returns structured guidance about the core concepts from the dgen knowledge base.

### Get guidance with context
```
dgen_guide(topic="implementation", context="production deployment")
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

Category: `cognitive-computing`

Tags: `cognitive-computing`
