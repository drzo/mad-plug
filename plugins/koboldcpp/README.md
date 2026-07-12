# koboldcpp

Build applications with KoboldCpp LLM inference engine. Use for local GGUF model deployment, OpenAI-compatible API integration, multimodal AI (text/image/speech), mobile app backends, and MCP server creation.

**Version:** 0.1.0 | **Category:** code-generation | **Tags:** `inference`

---

## Description

KoboldCpp is a self-contained LLM inference engine supporting GGUF models with multiple APIs and multimodal capabilities.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `koboldcpp_guide` | Provide guidance on koboldcpp topics | `topic` |

---

## Usage Examples

### Get guidance on a topic
```
koboldcpp_guide(topic="core concepts")
```
Returns structured guidance about the core concepts from the koboldcpp knowledge base.

### Get guidance with context
```
koboldcpp_guide(topic="implementation", context="production deployment")
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
