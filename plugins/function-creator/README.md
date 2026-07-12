# function-creator

Higher-order skill transformation engine that maps existing skills into analogous domains. Use when transforming a skill to a new domain/context, generating skill families from a single source, composing transformation chains, parameterizing skills into reusable templates, or packaging templates for community sharing. Composes with skill-creator for final packaging.

**Version:** 0.1.0 | **Category:** skill-engineering | **Tags:** `skill` `transform` `template`

---

## Description

Transform existing skills into analogous domains by decomposing them into abstract templates, parameterizing domain-specific bindings, and applying new domain mappings. A **functor** over the skill space.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `function_creator_guide` | Provide guidance on function-creator topics | `topic` |

---

## Usage Examples

### Get guidance on a topic
```
function_creator_guide(topic="core concepts")
```
Returns structured guidance about the core concepts from the function-creator knowledge base.

### Get guidance with context
```
function_creator_guide(topic="implementation", context="production deployment")
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

Tags: `skill` `transform` `template`
