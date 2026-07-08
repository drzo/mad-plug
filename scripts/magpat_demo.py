#!/usr/bin/env python3
"""
Magic Patterns API Demo Script

This script demonstrates the capabilities of the Magic Patterns API (magpat)
for generating UI components and pages from natural language prompts.

Features demonstrated:
1. Basic UI component generation
2. Different preset configurations
3. Parsing and extracting generated code
4. Saving generated components to files

Usage:
    python magpat_demo.py

Environment:
    Requires MP_API_KEY environment variable to be set
"""

import os
import json
import requests
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from pathlib import Path


@dataclass
class SourceFile:
    """Represents a source file from Magic Patterns"""
    id: str
    name: str
    code: str
    file_type: str
    is_read_only: bool = False


@dataclass
class CompiledFile:
    """Represents a compiled/bundled file from Magic Patterns"""
    id: str
    filename: str
    hosted_url: str
    file_type: str


@dataclass
class MagicPatternsResponse:
    """Parsed response from Magic Patterns API"""
    success: bool
    design_id: str
    editor_url: str
    preview_url: str
    source_files: List[SourceFile] = field(default_factory=list)
    compiled_files: List[CompiledFile] = field(default_factory=list)
    chat_messages: List[Dict] = field(default_factory=list)
    raw_response: Dict[str, Any] = field(default_factory=dict)
    error_message: str = ""


class MagicPatternsClient:
    """
    Client for interacting with the Magic Patterns API.
    
    The Magic Patterns API generates UI components and pages from natural
    language prompts. It supports various output presets including:
    - html-tailwind: HTML with Tailwind CSS
    - react-tailwind: React components with Tailwind (default)
    - vue-tailwind: Vue components with Tailwind
    
    API Response Structure:
    - id: Design ID
    - sourceFiles: Array of source code files
    - compiledFiles: Array of bundled/compiled files with CDN URLs
    - editorUrl: URL to edit the design in Magic Patterns
    - previewUrl: Live preview URL
    - chatMessages: Conversation history with the AI
    
    Example:
        client = MagicPatternsClient()
        response = client.generate("Create a login form")
        for file in response.source_files:
            print(f"Generated: {file.name}")
    """
    
    BASE_URL = "https://api.magicpatterns.com/api/v2/pattern"
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Magic Patterns client.
        
        Args:
            api_key: API key for authentication. If not provided,
                    reads from MP_API_KEY environment variable.
        """
        self.api_key = api_key or os.environ.get("MP_API_KEY")
        if not self.api_key:
            raise ValueError("API key required. Set MP_API_KEY environment variable.")
    
    def generate(
        self,
        prompt: str,
        preset_id: str = "html-tailwind",
        mode: str = "fast",
        model_selector: str = "auto",
        image_urls: Optional[List[str]] = None
    ) -> MagicPatternsResponse:
        """
        Generate UI components from a natural language prompt.
        
        Args:
            prompt: Natural language description of the UI to create.
                   Be specific about layout, components, and functionality.
            preset_id: Output format preset. Options:
                      - "html-tailwind": HTML with Tailwind CSS
                      - "react-tailwind": React with Tailwind
                      - "vue-tailwind": Vue with Tailwind
            mode: Generation mode. Default "fast".
            model_selector: Model selection strategy. Default "auto".
            image_urls: Optional list of image URLs for visual reference.
        
        Returns:
            MagicPatternsResponse containing generated files and metadata.
        
        Example prompts:
            - "Create a modern login form with email and password fields"
            - "Build a dashboard with sidebar navigation and stats cards"
            - "Design a pricing page with three tier cards"
            - "Create a user profile card with avatar, name, and bio"
        """
        headers = {
            "x-mp-api-key": self.api_key,
        }
        
        # Build multipart form data
        data = {
            "prompt": prompt,
            "mode": mode,
            "presetId": preset_id,
            "modelSelector": model_selector,
        }
        
        if image_urls:
            data["images"] = json.dumps(image_urls)
        
        print(f"🎨 Generating UI for: '{prompt[:60]}...'")
        print(f"   Preset: {preset_id}, Mode: {mode}")
        
        try:
            response = requests.post(
                self.BASE_URL,
                headers=headers,
                data=data,
                timeout=120,  # Generation can take time
                allow_redirects=True
            )
            
            if response.status_code != 200:
                return MagicPatternsResponse(
                    success=False,
                    design_id="",
                    editor_url="",
                    preview_url="",
                    error_message=f"API Error: {response.status_code} - {response.text[:200]}",
                    raw_response={"error": response.text}
                )
            
            return self._parse_response(response.json())
            
        except requests.exceptions.Timeout:
            return MagicPatternsResponse(
                success=False,
                design_id="",
                editor_url="",
                preview_url="",
                error_message="Request timed out after 120 seconds"
            )
        except Exception as e:
            return MagicPatternsResponse(
                success=False,
                design_id="",
                editor_url="",
                preview_url="",
                error_message=str(e)
            )
    
    def _parse_response(self, raw_response: Dict[str, Any]) -> MagicPatternsResponse:
        """Parse the API response and extract generated files."""
        
        # Extract source files
        source_files = []
        for sf in raw_response.get("sourceFiles", []):
            source_files.append(SourceFile(
                id=sf.get("id", ""),
                name=sf.get("name", ""),
                code=sf.get("code", ""),
                file_type=sf.get("type", ""),
                is_read_only=sf.get("isReadOnly", False)
            ))
        
        # Extract compiled files
        compiled_files = []
        for cf in raw_response.get("compiledFiles", []):
            compiled_files.append(CompiledFile(
                id=cf.get("id", ""),
                filename=cf.get("fileName", ""),
                hosted_url=cf.get("hostedUrl", ""),
                file_type=cf.get("type", "")
            ))
        
        return MagicPatternsResponse(
            success=True,
            design_id=raw_response.get("id", ""),
            editor_url=raw_response.get("editorUrl", ""),
            preview_url=raw_response.get("previewUrl", ""),
            source_files=source_files,
            compiled_files=compiled_files,
            chat_messages=raw_response.get("chatMessages", []),
            raw_response=raw_response
        )


def save_generated_files(response: MagicPatternsResponse, output_dir: str):
    """Save generated source files to disk."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    for file in response.source_files:
        if file.is_read_only:
            continue  # Skip read-only template files
        
        file_path = output_path / file.name
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, "w") as f:
            f.write(file.code)
        print(f"   💾 Saved: {file_path}")
    
    # Save metadata
    metadata = {
        "design_id": response.design_id,
        "editor_url": response.editor_url,
        "preview_url": response.preview_url,
        "compiled_files": [
            {"filename": cf.filename, "url": cf.hosted_url}
            for cf in response.compiled_files
        ]
    }
    
    with open(output_path / "metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)
    print(f"   💾 Saved: {output_path / 'metadata.json'}")


def print_file_preview(response: MagicPatternsResponse, max_lines: int = 25):
    """Print a preview of generated files."""
    for file in response.source_files:
        if file.is_read_only:
            continue
        print(f"\n📄 {file.name} ({file.file_type}):")
        print("-" * 50)
        lines = file.code.split("\n")
        preview = "\n".join(lines[:max_lines])
        print(preview)
        if len(lines) > max_lines:
            print(f"... ({len(lines) - max_lines} more lines)")


def demo_button_generation():
    """Demonstrate simple button generation."""
    print("\n" + "="*60)
    print("DEMO 1: Simple Button Generation")
    print("="*60)
    
    client = MagicPatternsClient()
    
    response = client.generate(
        prompt="Create a gradient button with text 'Subscribe Now' that has a purple to pink gradient, rounded corners, and a subtle shadow. Add a hover effect that makes it slightly larger.",
        preset_id="html-tailwind"
    )
    
    if response.success:
        print(f"\n✅ Generation successful!")
        print(f"   Design ID: {response.design_id}")
        print(f"   Editor URL: {response.editor_url}")
        print(f"   Preview URL: {response.preview_url}")
        print(f"\n   Generated {len(response.source_files)} source file(s):")
        for f in response.source_files:
            status = "📖 (read-only)" if f.is_read_only else "✏️"
            print(f"   {status} {f.name}")
        return response
    else:
        print(f"\n❌ Generation failed: {response.error_message}")
        return None


def demo_card_generation():
    """Demonstrate card component generation."""
    print("\n" + "="*60)
    print("DEMO 2: Card Component Generation")
    print("="*60)
    
    client = MagicPatternsClient()
    
    response = client.generate(
        prompt="""Create a product card component with:
        - Product image placeholder (16:9 aspect ratio)
        - Product name in bold
        - Price with original price crossed out and sale price
        - Star rating (4.5 stars)
        - Add to Cart button
        Use a clean white card with subtle shadow.""",
        preset_id="html-tailwind"
    )
    
    if response.success:
        print(f"\n✅ Generation successful!")
        print(f"   Design ID: {response.design_id}")
        print(f"   Editor URL: {response.editor_url}")
        print(f"   Preview URL: {response.preview_url}")
        print(f"\n   Generated {len(response.source_files)} source file(s):")
        for f in response.source_files:
            status = "📖 (read-only)" if f.is_read_only else "✏️"
            print(f"   {status} {f.name}")
        return response
    else:
        print(f"\n❌ Generation failed: {response.error_message}")
        return None


def demo_form_generation():
    """Demonstrate form component generation."""
    print("\n" + "="*60)
    print("DEMO 3: Form Component Generation")
    print("="*60)
    
    client = MagicPatternsClient()
    
    response = client.generate(
        prompt="""Create a contact form with:
        - Name field (required)
        - Email field (required, with validation styling)
        - Subject dropdown with options: General, Support, Sales
        - Message textarea
        - Submit button
        Use a modern design with floating labels and focus states.""",
        preset_id="html-tailwind"
    )
    
    if response.success:
        print(f"\n✅ Generation successful!")
        print(f"   Design ID: {response.design_id}")
        print(f"   Editor URL: {response.editor_url}")
        print(f"   Preview URL: {response.preview_url}")
        print(f"\n   Generated {len(response.source_files)} source file(s):")
        for f in response.source_files:
            status = "📖 (read-only)" if f.is_read_only else "✏️"
            print(f"   {status} {f.name}")
        return response
    else:
        print(f"\n❌ Generation failed: {response.error_message}")
        return None


def main():
    """Run all demos."""
    print("🚀 Magic Patterns API Demo")
    print("=" * 60)
    print("This demo showcases the Magic Patterns API capabilities")
    print("for generating UI components from natural language prompts.")
    print("=" * 60)
    
    # Check API key
    if not os.environ.get("MP_API_KEY"):
        print("\n❌ Error: MP_API_KEY environment variable not set")
        print("   Please set your Magic Patterns API key:")
        print("   export MP_API_KEY='your-api-key'")
        return
    
    # Run demos
    results = []
    
    # Demo 1: Button
    result1 = demo_button_generation()
    if result1:
        results.append(("gradient-button", result1))
        save_generated_files(result1, "/home/ubuntu/magic-patterns-demo/output/gradient-button")
        print_file_preview(result1)
    
    # Demo 2: Card
    result2 = demo_card_generation()
    if result2:
        results.append(("product-card", result2))
        save_generated_files(result2, "/home/ubuntu/magic-patterns-demo/output/product-card")
        print_file_preview(result2)
    
    # Demo 3: Form
    result3 = demo_form_generation()
    if result3:
        results.append(("contact-form", result3))
        save_generated_files(result3, "/home/ubuntu/magic-patterns-demo/output/contact-form")
        print_file_preview(result3)
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 DEMO SUMMARY")
    print("=" * 60)
    print(f"Total demos run: 3")
    print(f"Successful: {len(results)}")
    print(f"\nGenerated components saved to: /home/ubuntu/magic-patterns-demo/output/")
    
    for name, result in results:
        print(f"\n📦 {name}:")
        print(f"   Preview: {result.preview_url}")
        print(f"   Editor: {result.editor_url}")
        for f in result.source_files:
            if not f.is_read_only:
                print(f"   - {f.name}")


if __name__ == "__main__":
    main()
