#!/usr/bin/env python3
"""
Magic Patterns API Client

A reusable client for generating UI components from natural language prompts.

Usage:
    from magpat_client import MagicPatternsClient
    
    client = MagicPatternsClient()
    result = client.generate("Create a login form")
    
    for file in result.source_files:
        print(f"{file.name}: {file.code[:100]}...")
"""

import os
import json
import requests
from typing import Optional, List
from dataclasses import dataclass, field


@dataclass
class SourceFile:
    """A generated source file."""
    id: str
    name: str
    code: str
    file_type: str
    is_read_only: bool = False


@dataclass
class CompiledFile:
    """A compiled/bundled file with CDN URL."""
    id: str
    filename: str
    hosted_url: str
    file_type: str


@dataclass
class GenerationResult:
    """Result from Magic Patterns generation."""
    success: bool
    design_id: str = ""
    editor_url: str = ""
    preview_url: str = ""
    source_files: List[SourceFile] = field(default_factory=list)
    compiled_files: List[CompiledFile] = field(default_factory=list)
    error: str = ""


class MagicPatternsClient:
    """
    Client for Magic Patterns API.
    
    Generates UI components from natural language prompts.
    
    Example:
        client = MagicPatternsClient()
        result = client.generate(
            prompt="Create a pricing card with three tiers",
            preset="html-tailwind"
        )
        
        if result.success:
            print(f"Preview: {result.preview_url}")
            for f in result.source_files:
                if not f.is_read_only:
                    print(f"=== {f.name} ===")
                    print(f.code)
    """
    
    BASE_URL = "https://api.magicpatterns.com/api/v2/pattern"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize client.
        
        Args:
            api_key: API key. Defaults to MP_API_KEY env var.
        """
        self.api_key = api_key or os.environ.get("MP_API_KEY")
        if not self.api_key:
            raise ValueError("MP_API_KEY environment variable not set")
    
    def generate(
        self,
        prompt: str,
        preset: str = "html-tailwind",
        mode: str = "fast",
        model: str = "auto",
        timeout: int = 120
    ) -> GenerationResult:
        """
        Generate UI from prompt.
        
        Args:
            prompt: Natural language UI description
            preset: Output format (html-tailwind, react-tailwind, vue-tailwind)
            mode: Generation mode (fast)
            model: Model selector (auto)
            timeout: Request timeout in seconds
        
        Returns:
            GenerationResult with generated files and URLs
        """
        try:
            response = requests.post(
                self.BASE_URL,
                headers={"x-mp-api-key": self.api_key},
                data={
                    "prompt": prompt,
                    "presetId": preset,
                    "mode": mode,
                    "modelSelector": model
                },
                timeout=timeout,
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return GenerationResult(
                    success=False,
                    error=f"HTTP {response.status_code}: {response.text[:200]}"
                )
            
            data = response.json()
            
            source_files = [
                SourceFile(
                    id=f.get("id", ""),
                    name=f.get("name", ""),
                    code=f.get("code", ""),
                    file_type=f.get("type", ""),
                    is_read_only=f.get("isReadOnly", False)
                )
                for f in data.get("sourceFiles", [])
            ]
            
            compiled_files = [
                CompiledFile(
                    id=f.get("id", ""),
                    filename=f.get("fileName", ""),
                    hosted_url=f.get("hostedUrl", ""),
                    file_type=f.get("type", "")
                )
                for f in data.get("compiledFiles", [])
            ]
            
            return GenerationResult(
                success=True,
                design_id=data.get("id", ""),
                editor_url=data.get("editorUrl", ""),
                preview_url=data.get("previewUrl", ""),
                source_files=source_files,
                compiled_files=compiled_files
            )
            
        except requests.exceptions.Timeout:
            return GenerationResult(
                success=False,
                error=f"Request timed out after {timeout} seconds"
            )
        except Exception as e:
            return GenerationResult(
                success=False,
                error=str(e)
            )
    
    def save_files(self, result: GenerationResult, output_dir: str) -> List[str]:
        """
        Save generated files to directory.
        
        Args:
            result: Generation result
            output_dir: Directory to save files
        
        Returns:
            List of saved file paths
        """
        from pathlib import Path
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        saved = []
        for f in result.source_files:
            if f.is_read_only:
                continue
            
            file_path = output_path / f.name
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(f.code)
            saved.append(str(file_path))
        
        # Save metadata
        metadata = {
            "design_id": result.design_id,
            "editor_url": result.editor_url,
            "preview_url": result.preview_url
        }
        meta_path = output_path / "metadata.json"
        meta_path.write_text(json.dumps(metadata, indent=2))
        saved.append(str(meta_path))
        
        return saved


def main():
    """Demo usage."""
    client = MagicPatternsClient()
    
    print("Generating UI component...")
    result = client.generate(
        prompt="Create a simple blue button with hover effect",
        preset="html-tailwind"
    )
    
    if result.success:
        print(f"\n✅ Success!")
        print(f"Design ID: {result.design_id}")
        print(f"Preview: {result.preview_url}")
        print(f"Editor: {result.editor_url}")
        
        print("\nGenerated files:")
        for f in result.source_files:
            if not f.is_read_only:
                print(f"\n=== {f.name} ===")
                print(f.code)
    else:
        print(f"\n❌ Error: {result.error}")


if __name__ == "__main__":
    main()
