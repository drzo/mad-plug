# Magic Patterns API Reference

## REST API

### Base URL
```
https://api.magicpatterns.com/api/v2/pattern
```

### Authentication
Include your API key in the request header:
```
x-mp-api-key: YOUR_API_KEY
```

The API key is stored in the `MP_API_KEY` environment variable.

### Request Format
Content-Type: `multipart/form-data`

### Request Parameters

| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| `prompt` | string | **Yes** | - | Natural language description of the UI to generate |
| `presetId` | string | No | `react-tailwind` | Output technology stack |
| `mode` | string | No | `fast` | Generation speed mode |
| `modelSelector` | string | No | `auto` | AI model selection strategy |
| `images` | file[] | No | - | Reference images for visual guidance |

### Available Presets

| Preset ID | Description |
|-----------|-------------|
| `html-tailwind` | Plain HTML with Tailwind CSS classes |
| `react-tailwind` | React/TypeScript components with Tailwind CSS |
| `vue-tailwind` | Vue.js components with Tailwind CSS |

### Response Format

```json
{
  "id": "string",
  "sourceFiles": [
    {
      "id": "uuid",
      "name": "string",
      "code": "string",
      "type": "string",
      "isReadOnly": boolean
    }
  ],
  "compiledFiles": [
    {
      "id": "uuid",
      "fileName": "string",
      "hostedUrl": "string",
      "type": "string"
    }
  ],
  "editorUrl": "string",
  "previewUrl": "string",
  "chatMessages": [...]
}
```

### Response Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | string | Unique identifier for the generated design |
| `sourceFiles` | array | Array of generated source code files |
| `sourceFiles[].name` | string | Filename (e.g., `App.tsx`, `index.css`) |
| `sourceFiles[].code` | string | The actual source code content |
| `sourceFiles[].type` | string | File type (`javascript`, `css`, etc.) |
| `sourceFiles[].isReadOnly` | boolean | Whether the file is a template (read-only) |
| `compiledFiles` | array | Array of bundled/compiled assets |
| `compiledFiles[].hostedUrl` | string | CDN URL for the compiled asset |
| `editorUrl` | string | URL to edit the design in Magic Patterns web editor |
| `previewUrl` | string | Live preview URL for the generated component |
| `chatMessages` | array | Internal AI conversation log |

### Common Source Files

| File | Description |
|------|-------------|
| `App.tsx` | Main component code (editable) |
| `index.tsx` | Entry point (editable) |
| `index.css` | Tailwind imports (read-only) |
| `tailwind.config.js` | Tailwind configuration (read-only) |
| `components/*.tsx` | Additional component files |

### Error Handling

| Status Code | Description |
|-------------|-------------|
| 200 | Success |
| 307 | Redirect (follow with `-L` flag in curl) |
| 401 | Invalid or missing API key |
| 402 | Insufficient credits |
| 429 | Rate limit exceeded |
| 500 | Server error |

### Example: Python

```python
import os
import json
import requests

def generate_ui(prompt: str, preset: str = "html-tailwind") -> dict:
    """Generate UI component from prompt."""
    response = requests.post(
        "https://api.magicpatterns.com/api/v2/pattern",
        headers={"x-mp-api-key": os.environ["MP_API_KEY"]},
        data={
            "prompt": prompt,
            "presetId": preset,
            "mode": "fast",
            "modelSelector": "auto"
        },
        timeout=120,
        allow_redirects=True
    )
    return response.json()

# Usage
result = generate_ui("Create a blue button with hover effect")
for file in result["sourceFiles"]:
    if not file["isReadOnly"]:
        print(f"=== {file['name']} ===")
        print(file["code"])
```

### Example: cURL

```bash
curl -L --request POST \
  --url https://api.magicpatterns.com/api/v2/pattern \
  --header 'Content-Type: multipart/form-data' \
  --header "x-mp-api-key: $MP_API_KEY" \
  --form 'prompt=Create a simple button' \
  --form mode=fast \
  --form presetId=html-tailwind \
  --form modelSelector=auto
```

## MCP Server

### Server URL
```
https://mcp.magicpatterns.com/mcp
```

### Authentication
OAuth 2.0 (automatically triggered when using `manus-mcp-cli`)

### Available Tools

#### create_design
Creates a new design from a prompt.

**Parameters:**
- `prompt` (string, required): Natural language UI description
- `imageUrls` (string[], optional): Array of image URLs for reference

**Returns:** Design ID, editor URL, preview URL, list of generated files

**Credits:** Yes

#### get_design
Retrieves metadata about an existing design.

**Parameters:**
- `designId` (string, required): The design ID

**Returns:** Design name and list of available files

**Credits:** No

#### read_files
Reads the contents of files from a design.

**Parameters:**
- `designId` (string, required): The design ID
- `fileNames` (string[], required): Array of filenames to read

**Returns:** File contents

**Credits:** No

#### update_design
Updates an existing design with a new prompt.

**Parameters:**
- `designId` (string, required): The design ID
- `prompt` (string, required): Natural language description of changes

**Returns:** Updated design information

**Credits:** Yes

### MCP Usage Examples

```bash
# Create a new design
manus-mcp-cli tool call create_design --server magic-patterns \
  --input '{"prompt": "Create a login form"}'

# Get design info
manus-mcp-cli tool call get_design --server magic-patterns \
  --input '{"designId": "abc123"}'

# Read specific files
manus-mcp-cli tool call read_files --server magic-patterns \
  --input '{"designId": "abc123", "fileNames": ["App.tsx", "index.tsx"]}'

# Update design
manus-mcp-cli tool call update_design --server magic-patterns \
  --input '{"designId": "abc123", "prompt": "Add a forgot password link"}'
```
