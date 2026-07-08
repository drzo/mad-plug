#!/usr/bin/env python3
"""
Validate multiplatform integration configuration.

Usage:
    python validate_integration.py <config-dir>

Example:
    python validate_integration.py ./config
"""

import argparse
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

import yaml


class ValidationError:
    """Represents a validation error."""
    def __init__(self, file: str, path: str, message: str, severity: str = "error"):
        self.file = file
        self.path = path
        self.message = message
        self.severity = severity
    
    def __str__(self) -> str:
        icon = "❌" if self.severity == "error" else "⚠️"
        return f"{icon} [{self.file}] {self.path}: {self.message}"


def load_yaml_file(path: Path) -> Tuple[Dict[str, Any], List[ValidationError]]:
    """Load and parse a YAML file."""
    errors = []
    try:
        with open(path) as f:
            data = yaml.safe_load(f)
            return data or {}, errors
    except yaml.YAMLError as e:
        errors.append(ValidationError(path.name, "", f"Invalid YAML: {e}"))
        return {}, errors
    except FileNotFoundError:
        errors.append(ValidationError(path.name, "", "File not found"))
        return {}, errors


def validate_platforms(config: Dict[str, Any], file_name: str) -> List[ValidationError]:
    """Validate platforms configuration."""
    errors = []
    platforms = config.get("platforms", {})
    
    if not platforms:
        errors.append(ValidationError(file_name, "platforms", "No platforms defined"))
        return errors
    
    required_fields = ["type", "base_url", "auth"]
    auth_types = ["oauth2", "api_key", "token", "basic"]
    
    for platform_name, platform_config in platforms.items():
        path = f"platforms.{platform_name}"
        
        # Check required fields
        for field in required_fields:
            if field not in platform_config:
                errors.append(ValidationError(file_name, f"{path}.{field}", f"Required field missing"))
        
        # Validate auth configuration
        auth = platform_config.get("auth", {})
        if auth:
            auth_type = auth.get("type")
            if auth_type not in auth_types:
                errors.append(ValidationError(
                    file_name, f"{path}.auth.type",
                    f"Invalid auth type '{auth_type}'. Must be one of: {', '.join(auth_types)}"
                ))
            
            # Check for credential environment variables
            if auth_type == "oauth2":
                if not auth.get("token_env"):
                    errors.append(ValidationError(
                        file_name, f"{path}.auth.token_env",
                        "OAuth2 requires token_env",
                        severity="warning"
                    ))
            elif auth_type == "api_key":
                if not auth.get("key_env"):
                    errors.append(ValidationError(
                        file_name, f"{path}.auth.key_env",
                        "API key auth requires key_env",
                        severity="warning"
                    ))
        
        # Validate rate limit
        rate_limit = platform_config.get("rate_limit", {})
        if rate_limit:
            if "requests" not in rate_limit:
                errors.append(ValidationError(
                    file_name, f"{path}.rate_limit.requests",
                    "Rate limit should specify requests count",
                    severity="warning"
                ))
            if "period" not in rate_limit:
                errors.append(ValidationError(
                    file_name, f"{path}.rate_limit.period",
                    "Rate limit should specify period",
                    severity="warning"
                ))
        
        # Validate base_url format
        base_url = platform_config.get("base_url", "")
        if base_url and not base_url.startswith(("http://", "https://")):
            errors.append(ValidationError(
                file_name, f"{path}.base_url",
                "base_url should start with http:// or https://"
            ))
    
    return errors


def validate_mappings(config: Dict[str, Any], platforms: List[str], file_name: str) -> List[ValidationError]:
    """Validate data mappings configuration."""
    errors = []
    entities = config.get("entities", {})
    
    if not entities:
        errors.append(ValidationError(file_name, "entities", "No entities defined", severity="warning"))
        return errors
    
    for entity_name, entity_config in entities.items():
        path = f"entities.{entity_name}"
        
        # Check canonical fields
        canonical_fields = entity_config.get("canonical_fields", [])
        if not canonical_fields:
            errors.append(ValidationError(file_name, f"{path}.canonical_fields", "No canonical fields defined"))
        
        # Check platform mappings
        platform_mappings = entity_config.get("platform_mappings", {})
        if not platform_mappings:
            errors.append(ValidationError(
                file_name, f"{path}.platform_mappings",
                "No platform mappings defined",
                severity="warning"
            ))
        
        # Validate each platform mapping
        for platform, mapping in platform_mappings.items():
            if platform not in platforms:
                errors.append(ValidationError(
                    file_name, f"{path}.platform_mappings.{platform}",
                    f"Platform '{platform}' not defined in platforms.yaml"
                ))
            
            # Check that all canonical fields have mappings
            for field in canonical_fields:
                if field not in mapping:
                    errors.append(ValidationError(
                        file_name, f"{path}.platform_mappings.{platform}.{field}",
                        f"Missing mapping for canonical field '{field}'",
                        severity="warning"
                    ))
    
    return errors


def validate_commands(config: Dict[str, Any], platforms: List[str], entities: List[str], file_name: str) -> List[ValidationError]:
    """Validate commands configuration."""
    errors = []
    commands = config.get("commands", {})
    
    if not commands:
        errors.append(ValidationError(file_name, "commands", "No commands defined", severity="warning"))
        return errors
    
    valid_orchestration_types = ["single", "parallel", "sequential", "saga"]
    
    for cmd_name, cmd_config in commands.items():
        path = f"commands.{cmd_name}"
        
        # Validate command name format
        if ":" not in cmd_name:
            errors.append(ValidationError(
                file_name, path,
                "Command name should follow 'entity:action' format (e.g., 'customer:create')"
            ))
        
        # Check description
        if not cmd_config.get("description"):
            errors.append(ValidationError(
                file_name, f"{path}.description",
                "Command should have a description",
                severity="warning"
            ))
        
        # Validate args
        args = cmd_config.get("args", [])
        for i, arg in enumerate(args):
            arg_path = f"{path}.args[{i}]"
            if not arg.get("name"):
                errors.append(ValidationError(file_name, arg_path, "Argument must have a name"))
            
            arg_type = arg.get("type", "string")
            valid_types = ["string", "integer", "boolean", "array"]
            if arg_type not in valid_types:
                errors.append(ValidationError(
                    file_name, f"{arg_path}.type",
                    f"Invalid type '{arg_type}'. Must be one of: {', '.join(valid_types)}"
                ))
        
        # Validate orchestration
        orchestration = cmd_config.get("orchestration", {})
        if orchestration:
            orch_type = orchestration.get("type")
            if orch_type not in valid_orchestration_types:
                errors.append(ValidationError(
                    file_name, f"{path}.orchestration.type",
                    f"Invalid orchestration type '{orch_type}'. Must be one of: {', '.join(valid_orchestration_types)}"
                ))
            
            # Validate platform references
            if orch_type == "parallel":
                cmd_platforms = orchestration.get("platforms", [])
                if cmd_platforms != "all":
                    for p in cmd_platforms:
                        if p not in platforms:
                            errors.append(ValidationError(
                                file_name, f"{path}.orchestration.platforms",
                                f"Unknown platform '{p}'"
                            ))
            
            # Validate sequential steps
            if orch_type == "sequential":
                steps = orchestration.get("steps", [])
                if not steps:
                    errors.append(ValidationError(
                        file_name, f"{path}.orchestration.steps",
                        "Sequential orchestration requires steps"
                    ))
                
                valid_actions = ["fetch", "transform", "create", "update", "upsert", "delete"]
                for i, step in enumerate(steps):
                    step_path = f"{path}.orchestration.steps[{i}]"
                    action = step.get("action")
                    if action not in valid_actions:
                        errors.append(ValidationError(
                            file_name, f"{step_path}.action",
                            f"Invalid action '{action}'. Must be one of: {', '.join(valid_actions)}"
                        ))
    
    return errors


def validate_integration(config_dir: Path) -> Tuple[bool, List[ValidationError]]:
    """Validate all configuration files."""
    all_errors = []
    
    # Load platforms.yaml
    platforms_path = config_dir / "platforms.yaml"
    platforms_config, errors = load_yaml_file(platforms_path)
    all_errors.extend(errors)
    
    if platforms_config:
        all_errors.extend(validate_platforms(platforms_config, "platforms.yaml"))
    
    platform_names = list(platforms_config.get("platforms", {}).keys())
    
    # Load mappings.yaml
    mappings_path = config_dir / "mappings.yaml"
    mappings_config, errors = load_yaml_file(mappings_path)
    all_errors.extend(errors)
    
    if mappings_config:
        all_errors.extend(validate_mappings(mappings_config, platform_names, "mappings.yaml"))
    
    entity_names = list(mappings_config.get("entities", {}).keys())
    
    # Load commands.yaml
    commands_path = config_dir / "commands.yaml"
    commands_config, errors = load_yaml_file(commands_path)
    all_errors.extend(errors)
    
    if commands_config:
        all_errors.extend(validate_commands(commands_config, platform_names, entity_names, "commands.yaml"))
    
    # Determine success
    error_count = sum(1 for e in all_errors if e.severity == "error")
    warning_count = sum(1 for e in all_errors if e.severity == "warning")
    
    return error_count == 0, all_errors


def main():
    parser = argparse.ArgumentParser(description="Validate multiplatform integration configuration")
    parser.add_argument("config_dir", help="Configuration directory")
    parser.add_argument("--strict", action="store_true", help="Treat warnings as errors")
    
    args = parser.parse_args()
    config_dir = Path(args.config_dir)
    
    if not config_dir.exists():
        print(f"❌ Configuration directory not found: {config_dir}")
        sys.exit(1)
    
    print(f"🔍 Validating configuration in {config_dir}")
    print()
    
    success, errors = validate_integration(config_dir)
    
    if errors:
        for error in errors:
            print(str(error))
        print()
    
    error_count = sum(1 for e in errors if e.severity == "error")
    warning_count = sum(1 for e in errors if e.severity == "warning")
    
    if args.strict:
        success = error_count == 0 and warning_count == 0
    
    if success:
        print(f"✅ Validation passed")
        if warning_count > 0:
            print(f"   ({warning_count} warning(s))")
    else:
        print(f"❌ Validation failed: {error_count} error(s), {warning_count} warning(s)")
        sys.exit(1)


if __name__ == "__main__":
    main()
