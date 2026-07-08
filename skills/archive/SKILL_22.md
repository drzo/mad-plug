---
name: magic-patterns
description: Generate UI components from natural language using Magic Patterns. Use when creating React/HTML components, prototyping interfaces, generating buttons/cards/forms/dashboards, or when the user mentions Magic Patterns, magpat, or UI generation from prompts.
---

# Magic Patterns

Generate production-ready UI components from natural language prompts using the Magic Patterns API.

## Overview

Magic Patterns transforms text descriptions into React/TypeScript components with Tailwind CSS. Use it to rapidly prototype UIs, generate buttons, cards, forms, dashboards, and complete pages.

## Quick Start

### API Generation (Recommended for automation)

```python
import os
import requests

response = requests.post(
    "https://api.magicpatterns.com/api/v2/pattern",
    headers={"x-mp-api-key": os.environ["MP_API_KEY"]},
    data={
        "prompt": "Create a pricing card with three tiers",
        "presetId": "html-tailwind",
        "mode": "fast",
        "modelSelector": "auto"
    },
    timeout=120
)

data = response.json()
# data["sourceFiles"] contains generated code
# data["previewUrl"] is live preview
# data["editorUrl"] opens Magic Patterns editor
```

### MCP Integration (For AI-assisted workflows)

```bash
# List available tools
manus-mcp-cli tool list --server magic-patterns

# Create a design
manus-mcp-cli tool call create_design --server magic-patterns \
  --input '{"prompt": "Create a login form with email and password"}'

# Get design metadata
manus-mcp-cli tool call get_design --server magic-patterns \
  --input '{"designId": "abc123"}'

# Read generated files
manus-mcp-cli tool call read_files --server magic-patterns \
  --input '{"designId": "abc123", "fileNames": ["App.tsx"]}'

# Update existing design
manus-mcp-cli tool call update_design --server magic-patterns \
  --input '{"designId": "abc123", "prompt": "Add a forgot password link"}'
```

## API Reference

### Endpoint
`POST https://api.magicpatterns.com/api/v2/pattern`

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `prompt` | string | Yes | Natural language UI description |
| `presetId` | string | No | Output format: `html-tailwind`, `react-tailwind`, `vue-tailwind` |
| `mode` | string | No | Generation mode: `fast` (default) |
| `modelSelector` | string | No | Model selection: `auto` (default) |
| `images` | file[] | No | Reference images for visual guidance |

### Response Structure

```json
{
  "id": "design-id",
  "sourceFiles": [
    {"name": "App.tsx", "code": "...", "type": "javascript", "isReadOnly": false}
  ],
  "compiledFiles": [
    {"fileName": "index.js", "hostedUrl": "https://cdn.magicpatterns.com/..."}
  ],
  "editorUrl": "https://www.magicpatterns.com/c/design-id",
  "previewUrl": "https://project-name.magicpatterns.app"
}
```

## MCP Tools

| Tool | Purpose | Credits |
|------|---------|---------|
| `create_design` | Generate new UI from prompt | Yes |
| `get_design` | Get design metadata and file list | No |
| `read_files` | Read file contents from design | No |
| `update_design` | Modify existing design with prompt | Yes |

## Effective Prompting

### Structure Your Prompts

Be specific about layout, components, and functionality:

```
Create a dashboard with:
- Header with logo and user avatar dropdown
- Sidebar navigation with icons
- Main content area with 4 stat cards
- Line chart showing weekly data
- Recent activity list with timestamps
Use a dark theme with blue accents.
```

### Component Examples

**Buttons:**
```
Create a gradient button with purple-to-pink gradient, 
rounded corners, shadow, and scale-up hover effect
```

**Cards:**
```
Create a product card with:
- 16:9 image placeholder
- Product name in bold
- Original price crossed out, sale price highlighted
- 4.5 star rating
- Add to Cart button
```

**Forms:**
```
Create a contact form with:
- Name field (required)
- Email with validation styling
- Subject dropdown: General, Support, Sales
- Message textarea
- Submit button
Use floating labels and focus states
```

## Workflow: API Integration

1. **Generate**: Send prompt to API with desired preset
2. **Parse**: Extract `sourceFiles` from response
3. **Save**: Write code files to your project
4. **Preview**: Use `previewUrl` to see live result
5. **Iterate**: Modify prompt and regenerate as needed

## Workflow: MCP Integration

1. **Create**: Use `create_design` with your prompt
2. **Inspect**: Call `get_design` to see generated files
3. **Read**: Use `read_files` to get code content
4. **Refine**: Call `update_design` to iterate on design
5. **Export**: Copy code to your project

## Choosing API vs MCP

| Scenario | Use |
|----------|-----|
| Automated generation in scripts | API |
| CI/CD integration | API |
| Interactive development with AI | MCP |
| Iterative design refinement | MCP |
| Batch component generation | API |
| Cursor/Claude integration | MCP |

## Output Characteristics

- **Framework**: React with TypeScript
- **Styling**: Tailwind CSS classes
- **Accessibility**: ARIA attributes included
- **Responsiveness**: Mobile-first design
- **Dependencies**: `clsx`, `tailwind-merge` for class management

## Tips

- Include specific colors, spacing, and typography in prompts
- Reference existing design systems (e.g., "like Stripe's pricing page")
- Use image references for complex layouts
- Request specific hover/focus states for interactivity
- Specify dark/light theme preferences explicitly
