# get-shit-done

Meta-prompting, context engineering, and spec-driven development system for Claude Code, OpenCode, and Gemini CLI. Use when building software with AI coding assistants, structuring multi-phase development workflows, solving context rot in long AI sessions, or when the user mentions GSD, get-shit-done, spec-driven development, or context engineering for AI coding.

**Version:** 0.1.0 | **Category:** code-generation | **Tags:** `cognitive-computing`

---

## Description

Context engineering layer that makes AI coding assistants reliable at scale. Solves **context rot** — quality degradation as the AI fills its context window — by giving each execution task a fresh 200k-token context.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `get_shit_done_guide` | Provide guidance on get-shit-done topics | `topic` |

---

## Usage Examples

### Get guidance on a topic
```
get_shit_done_guide(topic="core concepts")
```
Returns structured guidance about the core concepts from the get-shit-done knowledge base.

### Get guidance with context
```
get_shit_done_guide(topic="implementation", context="production deployment")
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

Tags: `cognitive-computing`
