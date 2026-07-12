# ggml-spec

Build minimal GGML tensor library implementations from formal specifications. Use when creating custom ML inference engines, porting GGML to new architectures, implementing subset of operations for specific models (LLaMA, Whisper), or optimizing quantized inference for target hardware (ARM64, x86-64, WASM).

**Version:** 0.1.0 | **Category:** code-generation | **Tags:** `inference`

---

## Description

Build minimal, efficient GGML implementations by selecting only the operations, types, and architecture-specific code needed for your use case.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `ggml_spec_guide` | Provide guidance on ggml-spec topics | `topic` |

---

## Usage Examples

### Get guidance on a topic
```
ggml_spec_guide(topic="core concepts")
```
Returns structured guidance about the core concepts from the ggml-spec knowledge base.

### Get guidance with context
```
ggml_spec_guide(topic="implementation", context="production deployment")
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

Category: `code-generation`

Tags: `inference`
