# clawcog

Develop, configure, extend, and operate OpenCog (clawcog) — a personal AI assistant gateway with multi-channel messaging, cognitive architecture, skills, plugins, and multi-agent routing. Use when working on the cogpy/clawcog repository, building OpenCog extensions or skills, configuring the gateway, debugging channel integrations, or contributing to the codebase.

**Version:** 0.1.0 | **Category:** skill-engineering | **Tags:** `skill` `cognitive` `opencog`

---

## Description

OpenCog is a personal AI assistant gateway you run on your own devices. It connects to channels (WhatsApp, Telegram, Slack, Discord, Signal, iMessage, Google Chat, MS Teams, WebChat, and more), runs an embedded agent runtime, and exposes a WebSocket control plane.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `clawcog_guide` | Provide guidance on clawcog topics | `topic` |

---

## Usage Examples

### Get guidance on a topic
```
clawcog_guide(topic="core concepts")
```
Returns structured guidance about the core concepts from the clawcog knowledge base.

### Get guidance with context
```
clawcog_guide(topic="implementation", context="production deployment")
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

Tags: `skill` `cognitive` `opencog`
