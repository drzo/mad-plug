#!/usr/bin/env python3
"""
Initialize a new multiplatform API integration project.

Usage:
    python init_integration.py <project-name> [--platforms <p1,p2,...>]

Example:
    python init_integration.py ecommerce-hub --platforms shopify,stripe,quickbooks
"""

import argparse
import os
import sys
from pathlib import Path

# Default platform configurations
PLATFORM_TEMPLATES = {
    "shopify": {
        "type": "rest",
        "base_url": "https://{store}.myshopify.com/admin/api/2024-01",
        "auth": {
            "type": "oauth2",
            "token_env": "SHOPIFY_ACCESS_TOKEN"
        },
        "rate_limit": {
            "requests": 40,
            "period": "1s"
        },
        "pagination": {
            "type": "link_header",
            "param": "page_info"
        }
    },
    "stripe": {
        "type": "rest",
        "base_url": "https://api.stripe.com/v1",
        "auth": {
            "type": "api_key",
            "key_env": "STRIPE_SECRET_KEY",
            "header": "Authorization: Bearer {key}"
        },
        "rate_limit": {
            "requests": 100,
            "period": "1s"
        },
        "pagination": {
            "type": "cursor",
            "param": "starting_after"
        }
    },
    "quickbooks": {
        "type": "rest",
        "base_url": "https://quickbooks.api.intuit.com/v3/company/{realm_id}",
        "auth": {
            "type": "oauth2",
            "token_env": "QUICKBOOKS_ACCESS_TOKEN",
            "refresh_env": "QUICKBOOKS_REFRESH_TOKEN"
        },
        "rate_limit": {
            "requests": 500,
            "period": "60s"
        },
        "pagination": {
            "type": "offset",
            "param": "startPosition"
        }
    },
    "slack": {
        "type": "rest",
        "base_url": "https://slack.com/api",
        "auth": {
            "type": "oauth2",
            "token_env": "SLACK_BOT_TOKEN"
        },
        "rate_limit": {
            "requests": 50,
            "period": "60s"
        },
        "pagination": {
            "type": "cursor",
            "param": "cursor"
        }
    },
    "github": {
        "type": "rest",
        "base_url": "https://api.github.com",
        "auth": {
            "type": "token",
            "token_env": "GITHUB_TOKEN",
            "header": "Authorization: Bearer {token}"
        },
        "rate_limit": {
            "requests": 5000,
            "period": "3600s"
        },
        "pagination": {
            "type": "link_header",
            "param": "page"
        }
    }
}

# Common entity mappings
ENTITY_TEMPLATES = {
    "customer": {
        "canonical_fields": ["id", "email", "name", "phone", "created_at", "metadata"],
        "shopify": {
            "id": "customer.id",
            "email": "customer.email",
            "name": "customer.first_name + ' ' + customer.last_name",
            "phone": "customer.phone",
            "created_at": "customer.created_at",
            "metadata": "customer.metafields"
        },
        "stripe": {
            "id": "customer.id",
            "email": "customer.email",
            "name": "customer.name",
            "phone": "customer.phone",
            "created_at": "timestamp(customer.created)",
            "metadata": "customer.metadata"
        },
        "quickbooks": {
            "id": "Customer.Id",
            "email": "Customer.PrimaryEmailAddr.Address",
            "name": "Customer.DisplayName",
            "phone": "Customer.PrimaryPhone.FreeFormNumber",
            "created_at": "Customer.MetaData.CreateTime",
            "metadata": "Customer.Notes"
        }
    },
    "order": {
        "canonical_fields": ["id", "customer_id", "total", "currency", "status", "created_at", "line_items"],
        "shopify": {
            "id": "order.id",
            "customer_id": "order.customer.id",
            "total": "order.total_price",
            "currency": "order.currency",
            "status": "order.financial_status",
            "created_at": "order.created_at",
            "line_items": "order.line_items"
        },
        "stripe": {
            "id": "invoice.id",
            "customer_id": "invoice.customer",
            "total": "invoice.total / 100",
            "currency": "invoice.currency",
            "status": "invoice.status",
            "created_at": "timestamp(invoice.created)",
            "line_items": "invoice.lines.data"
        }
    },
    "product": {
        "canonical_fields": ["id", "name", "description", "price", "sku", "inventory_quantity"],
        "shopify": {
            "id": "product.id",
            "name": "product.title",
            "description": "product.body_html",
            "price": "product.variants[0].price",
            "sku": "product.variants[0].sku",
            "inventory_quantity": "product.variants[0].inventory_quantity"
        },
        "stripe": {
            "id": "product.id",
            "name": "product.name",
            "description": "product.description",
            "price": "price.unit_amount / 100",
            "sku": "product.metadata.sku",
            "inventory_quantity": "null"
        }
    }
}

# Command templates
COMMAND_TEMPLATES = {
    "customer:create": {
        "description": "Create customer across configured platforms",
        "args": [
            {"name": "email", "required": True, "type": "string"},
            {"name": "name", "required": True, "type": "string"},
            {"name": "phone", "required": False, "type": "string"}
        ],
        "orchestration": {
            "type": "parallel",
            "platforms": "all",
            "rollback": True
        }
    },
    "customer:get": {
        "description": "Get customer by ID from primary platform",
        "args": [
            {"name": "id", "required": True, "type": "string"},
            {"name": "platform", "required": False, "type": "string", "default": "primary"}
        ],
        "orchestration": {
            "type": "single",
            "platform": "{platform}"
        }
    },
    "customer:list": {
        "description": "List customers with unified pagination",
        "args": [
            {"name": "limit", "required": False, "type": "integer", "default": 50},
            {"name": "cursor", "required": False, "type": "string"}
        ],
        "orchestration": {
            "type": "single",
            "platform": "primary"
        }
    },
    "customer:sync": {
        "description": "Sync customer data between platforms",
        "args": [
            {"name": "id", "required": True, "type": "string"},
            {"name": "source", "required": True, "type": "string"},
            {"name": "target", "required": True, "type": "string"}
        ],
        "orchestration": {
            "type": "sequential",
            "steps": [
                {"action": "fetch", "platform": "{source}", "entity": "customer"},
                {"action": "transform", "mapping": "customer"},
                {"action": "upsert", "platform": "{target}", "entity": "customer"}
            ]
        }
    },
    "order:sync": {
        "description": "Sync order/invoice between e-commerce and accounting",
        "args": [
            {"name": "order_id", "required": True, "type": "string"},
            {"name": "direction", "required": False, "type": "string", "choices": ["to_accounting", "from_accounting"]}
        ],
        "orchestration": {
            "type": "sequential",
            "steps": [
                {"action": "fetch", "platform": "shopify", "entity": "order"},
                {"action": "transform", "mapping": "order_to_invoice"},
                {"action": "create", "platform": "quickbooks", "entity": "invoice"},
                {"action": "update", "platform": "shopify", "entity": "order", "field": "note"}
            ]
        }
    }
}


def create_yaml_content(data: dict, indent: int = 0) -> str:
    """Convert dict to YAML string with proper formatting."""
    import json
    lines = []
    prefix = "  " * indent
    
    for key, value in data.items():
        if isinstance(value, dict):
            lines.append(f"{prefix}{key}:")
            lines.append(create_yaml_content(value, indent + 1))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key}:")
            for item in value:
                if isinstance(item, dict):
                    first = True
                    for k, v in item.items():
                        if first:
                            lines.append(f"{prefix}  - {k}: {json.dumps(v) if isinstance(v, (list, dict)) else v}")
                            first = False
                        else:
                            lines.append(f"{prefix}    {k}: {json.dumps(v) if isinstance(v, (list, dict)) else v}")
                else:
                    lines.append(f"{prefix}  - {item}")
        else:
            if isinstance(value, str) and ("{" in value or "'" in value or '"' in value):
                lines.append(f'{prefix}{key}: "{value}"')
            else:
                lines.append(f"{prefix}{key}: {value}")
    
    return "\n".join(lines)


def init_integration(project_name: str, platforms: list[str]) -> None:
    """Initialize a new integration project."""
    project_path = Path.cwd() / project_name
    
    if project_path.exists():
        print(f"❌ Directory '{project_name}' already exists")
        sys.exit(1)
    
    print(f"🚀 Initializing integration project: {project_name}")
    
    # Create directory structure
    dirs = [
        "config",
        "src/adapters",
        "src/transformers",
        "src/commands",
        "src/types",
        "tests/unit",
        "tests/integration",
        "bin"
    ]
    
    for d in dirs:
        (project_path / d).mkdir(parents=True, exist_ok=True)
        print(f"   ✓ Created {d}/")
    
    # Generate platforms.yaml
    platforms_config = {"platforms": {}}
    for p in platforms:
        if p in PLATFORM_TEMPLATES:
            platforms_config["platforms"][p] = PLATFORM_TEMPLATES[p]
        else:
            platforms_config["platforms"][p] = {
                "type": "rest",
                "base_url": f"https://api.{p}.com/v1",
                "auth": {"type": "api_key", "key_env": f"{p.upper()}_API_KEY"},
                "rate_limit": {"requests": 100, "period": "1s"}
            }
    
    platforms_yaml = f"""# Platform Configurations
# Generated by multiplatform-api-weaver

{create_yaml_content(platforms_config)}

# Primary platform for single-platform operations
primary_platform: {platforms[0] if platforms else 'shopify'}
"""
    (project_path / "config" / "platforms.yaml").write_text(platforms_yaml)
    print("   ✓ Created config/platforms.yaml")
    
    # Generate mappings.yaml
    mappings_config = {"entities": {}}
    for entity, template in ENTITY_TEMPLATES.items():
        entity_mapping = {"canonical_fields": template["canonical_fields"], "platform_mappings": {}}
        for p in platforms:
            if p in template:
                entity_mapping["platform_mappings"][p] = template[p]
        if entity_mapping["platform_mappings"]:
            mappings_config["entities"][entity] = entity_mapping
    
    mappings_yaml = f"""# Data Mappings
# Maps canonical fields to platform-specific fields

{create_yaml_content(mappings_config)}
"""
    (project_path / "config" / "mappings.yaml").write_text(mappings_yaml)
    print("   ✓ Created config/mappings.yaml")
    
    # Generate commands.yaml
    commands_yaml = f"""# Unified Command Definitions
# Define CLI commands that orchestrate across platforms

commands:
{create_yaml_content({"commands": COMMAND_TEMPLATES}, 0).replace("commands:", "")}
"""
    (project_path / "config" / "commands.yaml").write_text(commands_yaml)
    print("   ✓ Created config/commands.yaml")
    
    # Generate base adapter template
    adapter_template = '''"""
Base adapter interface for platform integrations.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from dataclasses import dataclass


@dataclass
class PaginatedResponse:
    """Unified pagination response."""
    data: List[Dict[str, Any]]
    has_more: bool
    cursor: Optional[str] = None
    total: Optional[int] = None


class BaseAdapter(ABC):
    """Base class for all platform adapters."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.base_url = config.get("base_url", "")
        self.auth_config = config.get("auth", {})
        self.rate_limit = config.get("rate_limit", {})
        self._client = None
    
    @abstractmethod
    async def authenticate(self) -> None:
        """Authenticate with the platform."""
        pass
    
    @abstractmethod
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make an authenticated request to the platform."""
        pass
    
    @abstractmethod
    async def paginate(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        limit: int = 50
    ) -> PaginatedResponse:
        """Fetch paginated results."""
        pass
    
    def transform(self, data: Dict[str, Any], entity: str, mapping: Dict[str, str]) -> Dict[str, Any]:
        """Transform platform data to canonical format."""
        result = {}
        for canonical_field, platform_path in mapping.items():
            result[canonical_field] = self._extract_value(data, platform_path)
        return result
    
    def _extract_value(self, data: Dict, path: str) -> Any:
        """Extract value from nested dict using dot notation."""
        if "+" in path:
            # Handle concatenation
            parts = [p.strip() for p in path.split("+")]
            values = [self._extract_value(data, p.strip("' \\"")) for p in parts]
            return " ".join(str(v) for v in values if v)
        
        keys = path.split(".")
        value = data
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
            elif isinstance(value, list) and key.isdigit():
                value = value[int(key)] if len(value) > int(key) else None
            else:
                return None
        return value
'''
    (project_path / "src" / "adapters" / "base.py").write_text(adapter_template)
    print("   ✓ Created src/adapters/base.py")
    
    # Generate platform-specific adapter stubs
    for p in platforms:
        adapter_stub = f'''"""
{p.title()} platform adapter.
"""

from typing import Any, Dict, List, Optional
from .base import BaseAdapter, PaginatedResponse


class {p.title()}Adapter(BaseAdapter):
    """Adapter for {p.title()} API."""
    
    async def authenticate(self) -> None:
        """Authenticate with {p.title()}."""
        # TODO: Implement authentication
        pass
    
    async def request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Make request to {p.title()} API."""
        # TODO: Implement request handling
        pass
    
    async def paginate(
        self,
        endpoint: str,
        params: Optional[Dict] = None,
        limit: int = 50
    ) -> PaginatedResponse:
        """Fetch paginated results from {p.title()}."""
        # TODO: Implement pagination
        pass
    
    # Entity-specific methods
    async def get_customer(self, customer_id: str) -> Dict[str, Any]:
        """Get customer by ID."""
        # TODO: Implement
        pass
    
    async def create_customer(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new customer."""
        # TODO: Implement
        pass
    
    async def list_customers(self, limit: int = 50, cursor: Optional[str] = None) -> PaginatedResponse:
        """List customers with pagination."""
        # TODO: Implement
        pass
'''
        (project_path / "src" / "adapters" / f"{p}.py").write_text(adapter_stub)
        print(f"   ✓ Created src/adapters/{p}.py")
    
    # Generate adapters __init__.py
    adapters_init = f'''"""
Platform adapters for multiplatform integration.
"""

from .base import BaseAdapter, PaginatedResponse
{chr(10).join(f"from .{p} import {p.title()}Adapter" for p in platforms)}

__all__ = [
    "BaseAdapter",
    "PaginatedResponse",
{chr(10).join(f'    "{p.title()}Adapter",' for p in platforms)}
]
'''
    (project_path / "src" / "adapters" / "__init__.py").write_text(adapters_init)
    print("   ✓ Created src/adapters/__init__.py")
    
    # Generate unified client
    client_template = f'''"""
Unified client for multiplatform API integration.
"""

from typing import Any, Dict, List, Optional, Type
from .adapters import BaseAdapter, {", ".join(f"{p.title()}Adapter" for p in platforms)}


class UnifiedClient:
    """Unified client that orchestrates multiple platform adapters."""
    
    ADAPTERS: Dict[str, Type[BaseAdapter]] = {{
{chr(10).join(f'        "{p}": {p.title()}Adapter,' for p in platforms)}
    }}
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.adapters: Dict[str, BaseAdapter] = {{}}
        self._init_adapters()
    
    def _init_adapters(self) -> None:
        """Initialize configured platform adapters."""
        platforms_config = self.config.get("platforms", {{}})
        for platform, platform_config in platforms_config.items():
            if platform in self.ADAPTERS:
                self.adapters[platform] = self.ADAPTERS[platform](platform_config)
    
    async def execute(self, command: str, **kwargs) -> Dict[str, Any]:
        """Execute a unified command."""
        # Parse command (e.g., "customer:create")
        entity, action = command.split(":")
        
        # Get command config
        cmd_config = self.config.get("commands", {{}}).get(command, {{}})
        orchestration = cmd_config.get("orchestration", {{}})
        
        if orchestration.get("type") == "parallel":
            return await self._execute_parallel(entity, action, orchestration, kwargs)
        elif orchestration.get("type") == "sequential":
            return await self._execute_sequential(entity, action, orchestration, kwargs)
        else:
            return await self._execute_single(entity, action, orchestration, kwargs)
    
    async def _execute_parallel(
        self,
        entity: str,
        action: str,
        orchestration: Dict,
        kwargs: Dict
    ) -> Dict[str, Any]:
        """Execute command across multiple platforms in parallel."""
        import asyncio
        
        platforms = orchestration.get("platforms", [])
        if platforms == "all":
            platforms = list(self.adapters.keys())
        
        tasks = []
        for platform in platforms:
            adapter = self.adapters.get(platform)
            if adapter:
                method = getattr(adapter, f"{{action}}_{{entity}}", None)
                if method:
                    tasks.append((platform, method(**kwargs)))
        
        results = {{}}
        for platform, task in tasks:
            try:
                results[platform] = await task
            except Exception as e:
                results[platform] = {{"error": str(e)}}
        
        return results
    
    async def _execute_sequential(
        self,
        entity: str,
        action: str,
        orchestration: Dict,
        kwargs: Dict
    ) -> Dict[str, Any]:
        """Execute command steps sequentially."""
        steps = orchestration.get("steps", [])
        context = {{**kwargs}}
        results = []
        
        for step in steps:
            step_action = step.get("action")
            platform = step.get("platform", "").format(**kwargs)
            
            adapter = self.adapters.get(platform)
            if not adapter:
                continue
            
            if step_action == "fetch":
                entity_type = step.get("entity")
                method = getattr(adapter, f"get_{{entity_type}}", None)
                if method:
                    result = await method(context.get("id") or context.get(f"{{entity_type}}_id"))
                    context[entity_type] = result
                    results.append({{"step": step_action, "platform": platform, "result": result}})
            
            elif step_action == "transform":
                # Apply transformation
                pass
            
            elif step_action in ("create", "upsert", "update"):
                entity_type = step.get("entity")
                method = getattr(adapter, f"{{step_action}}_{{entity_type}}", None)
                if method:
                    result = await method(context.get(entity_type, {{}}))
                    results.append({{"step": step_action, "platform": platform, "result": result}})
        
        return {{"steps": results, "context": context}}
    
    async def _execute_single(
        self,
        entity: str,
        action: str,
        orchestration: Dict,
        kwargs: Dict
    ) -> Dict[str, Any]:
        """Execute command on a single platform."""
        platform = orchestration.get("platform", self.config.get("primary_platform"))
        if platform == "{{platform}}":
            platform = kwargs.pop("platform", self.config.get("primary_platform"))
        
        adapter = self.adapters.get(platform)
        if not adapter:
            return {{"error": f"Platform {{platform}} not configured"}}
        
        method = getattr(adapter, f"{{action}}_{{entity}}", None)
        if not method:
            return {{"error": f"Action {{action}} not supported for {{entity}} on {{platform}}"}}
        
        return await method(**kwargs)
'''
    (project_path / "src" / "client.py").write_text(client_template)
    print("   ✓ Created src/client.py")
    
    # Generate CLI entry point
    cli_template = f'''#!/usr/bin/env python3
"""
Unified CLI for multiplatform API integration.

Usage:
    weaver <command> [options]
    
Commands:
    customer:create    Create customer across platforms
    customer:get       Get customer by ID
    customer:list      List customers
    customer:sync      Sync customer between platforms
    order:sync         Sync order to accounting system
"""

import argparse
import asyncio
import json
import sys
import yaml
from pathlib import Path
from typing import Any, Dict

from .client import UnifiedClient


def load_config(config_dir: str = "./config") -> Dict[str, Any]:
    """Load configuration from YAML files."""
    config_path = Path(config_dir)
    config = {{}}
    
    for yaml_file in config_path.glob("*.yaml"):
        with open(yaml_file) as f:
            config.update(yaml.safe_load(f) or {{}})
    
    return config


def format_output(data: Any, format_type: str = "json") -> str:
    """Format output data."""
    if format_type == "json":
        return json.dumps(data, indent=2, default=str)
    elif format_type == "table":
        # Simple table formatting
        if isinstance(data, list):
            if not data:
                return "No results"
            headers = list(data[0].keys())
            rows = [[str(item.get(h, "")) for h in headers] for item in data]
            widths = [max(len(h), max(len(r[i]) for r in rows)) for i, h in enumerate(headers)]
            header_line = " | ".join(h.ljust(w) for h, w in zip(headers, widths))
            separator = "-+-".join("-" * w for w in widths)
            data_lines = ["\\n".join(" | ".join(r[i].ljust(widths[i]) for i in range(len(headers))) for r in rows)]
            return f"{{header_line}}\\n{{separator}}\\n{{'\\n'.join(data_lines)}}"
        return str(data)
    else:
        return str(data)


async def main():
    parser = argparse.ArgumentParser(description="Unified multiplatform CLI")
    parser.add_argument("command", help="Command to execute (e.g., customer:create)")
    parser.add_argument("--config", default="./config", help="Config directory")
    parser.add_argument("--format", choices=["json", "table", "raw"], default="json")
    parser.add_argument("--id", help="Entity ID")
    parser.add_argument("--email", help="Email address")
    parser.add_argument("--name", help="Name")
    parser.add_argument("--phone", help="Phone number")
    parser.add_argument("--platform", help="Target platform")
    parser.add_argument("--source", help="Source platform for sync")
    parser.add_argument("--target", help="Target platform for sync")
    parser.add_argument("--limit", type=int, default=50, help="Result limit")
    parser.add_argument("--cursor", help="Pagination cursor")
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Initialize client
    client = UnifiedClient(config)
    
    # Build kwargs from args
    kwargs = {{}}
    for key in ["id", "email", "name", "phone", "platform", "source", "target", "limit", "cursor"]:
        value = getattr(args, key, None)
        if value is not None:
            kwargs[key] = value
    
    # Execute command
    try:
        result = await client.execute(args.command, **kwargs)
        print(format_output(result, args.format))
    except Exception as e:
        print(f"Error: {{e}}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
'''
    (project_path / "src" / "cli.py").write_text(cli_template)
    print("   ✓ Created src/cli.py")
    
    # Generate package files
    pyproject = f'''[project]
name = "{project_name}"
version = "0.1.0"
description = "Unified multiplatform API integration"
requires-python = ">=3.10"
dependencies = [
    "httpx>=0.25.0",
    "pyyaml>=6.0",
    "pydantic>=2.0",
]

[project.scripts]
weaver = "{project_name.replace('-', '_')}.cli:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"
'''
    (project_path / "pyproject.toml").write_text(pyproject)
    print("   ✓ Created pyproject.toml")
    
    # Generate .env.example
    env_example = "\n".join(f"{p.upper()}_API_KEY=your_{p}_api_key_here" for p in platforms)
    env_example += "\n# OAuth tokens (if applicable)\n"
    env_example += "\n".join(f"{p.upper()}_ACCESS_TOKEN=your_{p}_access_token_here" for p in platforms)
    (project_path / ".env.example").write_text(env_example)
    print("   ✓ Created .env.example")
    
    # Generate README
    readme = f'''# {project_name}

Unified multiplatform API integration built with [multiplatform-api-weaver](https://github.com/your-org/multiplatform-api-weaver).

## Platforms

{chr(10).join(f"- {p.title()}" for p in platforms)}

## Quick Start

```bash
# Install dependencies
pip install -e .

# Configure credentials
cp .env.example .env
# Edit .env with your API keys

# Run commands
weaver customer:list --format table
weaver customer:create --email "user@example.com" --name "John Doe"
weaver customer:sync --id "123" --source shopify --target quickbooks
```

## Configuration

- `config/platforms.yaml` - Platform API configurations
- `config/mappings.yaml` - Data field mappings between platforms
- `config/commands.yaml` - Unified command definitions

## Development

```bash
# Run tests
pytest tests/

# Type checking
mypy src/
```
'''
    (project_path / "README.md").write_text(readme)
    print("   ✓ Created README.md")
    
    print(f"\n✅ Integration project '{project_name}' initialized successfully!")
    print(f"\nNext steps:")
    print(f"  1. cd {project_name}")
    print(f"  2. Edit config/*.yaml files")
    print(f"  3. Implement adapter methods in src/adapters/")
    print(f"  4. pip install -e .")
    print(f"  5. weaver --help")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Initialize multiplatform integration project")
    parser.add_argument("project_name", help="Name of the project")
    parser.add_argument(
        "--platforms",
        default="shopify,stripe,quickbooks",
        help="Comma-separated list of platforms (default: shopify,stripe,quickbooks)"
    )
    
    args = parser.parse_args()
    platforms = [p.strip().lower() for p in args.platforms.split(",")]
    
    init_integration(args.project_name, platforms)
