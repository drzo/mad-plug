#!/usr/bin/env python3
"""
SkinForm Ingredient Lookup

Search and display ingredient information from the vessels database.

Usage:
    python lookup_ingredient.py <search_term>
    python lookup_ingredient.py "hyaluronic acid"
    python lookup_ingredient.py --list-all
"""

import json
import sys
from pathlib import Path
from typing import Any, Optional


def find_vessels_dir() -> Path:
    """Find the vessels directory."""
    # Try common locations
    candidates = [
        Path.cwd() / "vessels",
        Path.cwd().parent / "skinform" / "vessels",
        Path.home() / "skinform" / "vessels",
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    raise FileNotFoundError("Could not find vessels directory. Run from skinform repo root.")


def load_ingredients(vessels_dir: Path) -> list[dict[str, Any]]:
    """Load all ingredient files."""
    ingredients_dir = vessels_dir / "ingredients"
    ingredients = []
    
    if not ingredients_dir.exists():
        return ingredients
    
    for inci_file in ingredients_dir.glob("*.inci"):
        try:
            with open(inci_file, 'r') as f:
                data = json.load(f)
                data['_filename'] = inci_file.name
                ingredients.append(data)
        except (json.JSONDecodeError, IOError):
            continue
    
    return ingredients


def search_ingredients(ingredients: list[dict], search_term: str) -> list[dict]:
    """Search ingredients by name, INCI name, or function."""
    search_lower = search_term.lower()
    results = []
    
    for ing in ingredients:
        # Search in label
        if search_lower in ing.get('label', '').lower():
            results.append(ing)
            continue
        
        # Search in INCI name
        if search_lower in ing.get('inci_name', '').lower():
            results.append(ing)
            continue
        
        # Search in functions
        functions = ing.get('functions', [])
        if any(search_lower in func.lower() for func in functions):
            results.append(ing)
            continue
        
        # Search in category
        if search_lower in ing.get('category', '').lower():
            results.append(ing)
            continue
    
    return results


def format_ingredient(ing: dict) -> str:
    """Format ingredient for display."""
    lines = []
    lines.append("=" * 60)
    lines.append(f"INGREDIENT: {ing.get('label', 'Unknown')}")
    lines.append("=" * 60)
    
    lines.append(f"\nID: {ing.get('id', 'N/A')}")
    lines.append(f"INCI Name: {ing.get('inci_name', 'N/A')}")
    lines.append(f"Category: {ing.get('category', 'N/A')}")
    lines.append(f"Safety Rating: {ing.get('safety_rating', 'N/A')}")
    
    # Concentration range
    conc = ing.get('concentration_range', {})
    if conc:
        lines.append(f"\nConcentration Range:")
        lines.append(f"  Min: {conc.get('min', 'N/A')}%")
        lines.append(f"  Max: {conc.get('max', 'N/A')}%")
        lines.append(f"  Typical: {conc.get('typical', 'N/A')}%")
    
    # pH range
    ph = ing.get('ph_range', {})
    if ph:
        lines.append(f"\npH Range:")
        lines.append(f"  Min: {ph.get('min', 'N/A')}")
        lines.append(f"  Max: {ph.get('max', 'N/A')}")
        lines.append(f"  Optimal: {ph.get('optimal', 'N/A')}")
    
    # Solubility
    lines.append(f"\nSolubility: {ing.get('solubility', 'N/A')}")
    
    # Functions
    functions = ing.get('functions', [])
    if functions:
        lines.append(f"\nFunctions:")
        for func in functions:
            lines.append(f"  • {func}")
    
    # Compatibility
    compat = ing.get('compatibility', {})
    if compat:
        synergistic = compat.get('synergistic', [])
        avoid = compat.get('avoid', [])
        
        if synergistic:
            lines.append(f"\nSynergistic with:")
            for item in synergistic[:5]:  # Limit to 5
                lines.append(f"  ✓ {item}")
        
        if avoid:
            lines.append(f"\nAvoid combining with:")
            for item in avoid[:5]:  # Limit to 5
                lines.append(f"  ✗ {item}")
    
    # Commercial
    pricing = ing.get('pricing_zar')
    if pricing:
        lines.append(f"\nPricing: R{pricing:.2f} per 100g")
    
    suppliers = ing.get('supplier_ids', [])
    if suppliers:
        lines.append(f"Suppliers: {', '.join(suppliers)}")
    
    # Usage stats
    usage = ing.get('usage_frequency')
    if usage:
        lines.append(f"\nUsage Frequency: {usage} products")
    
    criticality = ing.get('criticality_score')
    if criticality:
        lines.append(f"Criticality Score: {criticality}/100")
    
    # Restrictions
    restrictions = ing.get('restrictions', [])
    if restrictions:
        lines.append(f"\n⚠️  Restrictions:")
        for restriction in restrictions:
            lines.append(f"  • {restriction}")
    
    lines.append("")
    return "\n".join(lines)


def list_all_ingredients(ingredients: list[dict]) -> str:
    """List all ingredients in summary format."""
    lines = []
    lines.append("=" * 60)
    lines.append("ALL INGREDIENTS")
    lines.append("=" * 60)
    lines.append(f"\nTotal: {len(ingredients)} ingredients\n")
    
    # Group by category
    by_category: dict[str, list] = {}
    for ing in ingredients:
        cat = ing.get('category', 'Unknown')
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(ing)
    
    for category, items in sorted(by_category.items()):
        lines.append(f"\n{category} ({len(items)}):")
        for ing in sorted(items, key=lambda x: x.get('label', '')):
            lines.append(f"  • {ing.get('label', 'Unknown')} ({ing.get('id', 'N/A')})")
    
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        print("Usage: python lookup_ingredient.py <search_term>")
        print("       python lookup_ingredient.py --list-all")
        print("\nExamples:")
        print("  python lookup_ingredient.py 'hyaluronic acid'")
        print("  python lookup_ingredient.py humectant")
        print("  python lookup_ingredient.py --list-all")
        sys.exit(1)
    
    try:
        vessels_dir = find_vessels_dir()
        ingredients = load_ingredients(vessels_dir)
        
        if not ingredients:
            print("No ingredients found in vessels directory.")
            sys.exit(1)
        
        if sys.argv[1] == "--list-all":
            print(list_all_ingredients(ingredients))
        else:
            search_term = " ".join(sys.argv[1:])
            results = search_ingredients(ingredients, search_term)
            
            if not results:
                print(f"No ingredients found matching: {search_term}")
                sys.exit(1)
            
            print(f"Found {len(results)} ingredient(s) matching '{search_term}':\n")
            for ing in results:
                print(format_ingredient(ing))
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
