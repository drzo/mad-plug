#!/usr/bin/env python3
"""
SkinForm Formulation Analyzer

Analyzes skincare formulations for compatibility, safety, and optimization opportunities.
Reads .form files from the vessels directory and provides analysis reports.

Usage:
    python analyze_formulation.py <formulation_file>
    python analyze_formulation.py vessels/formulations/retinol_night_cream.form
"""

import json
import sys
from pathlib import Path
from typing import Any


def load_formulation(filepath: str) -> dict[str, Any]:
    """Load a formulation file (.form)."""
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"Formulation file not found: {filepath}")
    
    with open(path, 'r') as f:
        return json.load(f)


def analyze_phases(formulation: dict) -> dict[str, Any]:
    """Analyze formulation phases."""
    phases = formulation.get('formulation_phases', {})
    analysis = {
        'phase_count': len(phases),
        'phases': [],
        'total_concentration': 0
    }
    
    for phase_name, phase_data in phases.items():
        if isinstance(phase_data, dict):
            ingredients = phase_data.get('ingredients', {})
            phase_concentration = sum(ingredients.values()) if isinstance(ingredients, dict) else 0
            analysis['phases'].append({
                'name': phase_name,
                'ingredient_count': len(ingredients) if isinstance(ingredients, dict) else 0,
                'concentration': phase_concentration,
                'temperature': phase_data.get('temperature'),
                'mixing_time': phase_data.get('mixing_time')
            })
            analysis['total_concentration'] += phase_concentration
    
    return analysis


def check_concentration_limits(formulation: dict) -> list[str]:
    """Check for concentration limit violations."""
    warnings = []
    phases = formulation.get('formulation_phases', {})
    
    total = 0
    for phase_name, phase_data in phases.items():
        if isinstance(phase_data, dict):
            ingredients = phase_data.get('ingredients', {})
            if isinstance(ingredients, dict):
                phase_total = sum(ingredients.values())
                total += phase_total
                
                if phase_total > 100:
                    warnings.append(f"Phase {phase_name} exceeds 100%: {phase_total:.1f}%")
    
    if total > 100:
        warnings.append(f"Total formulation exceeds 100%: {total:.1f}%")
    elif total < 95:
        warnings.append(f"Total formulation below 95%: {total:.1f}% (may need adjustment)")
    
    return warnings


def analyze_complexity(formulation: dict) -> dict[str, Any]:
    """Calculate formulation complexity metrics."""
    ingredient_count = formulation.get('ingredient_count', 0)
    phases = formulation.get('formulation_phases', {})
    
    # Count unique categories if available
    unique_categories = set()
    for phase_data in phases.values():
        if isinstance(phase_data, dict):
            # Would need ingredient database to get categories
            pass
    
    complexity_score = (ingredient_count * 2) + (len(phases) * 5)
    
    return {
        'ingredient_count': ingredient_count,
        'phase_count': len(phases),
        'complexity_score': complexity_score,
        'complexity_level': 'High' if complexity_score > 50 else 'Medium' if complexity_score > 25 else 'Low'
    }


def generate_report(formulation: dict, filepath: str) -> str:
    """Generate a comprehensive analysis report."""
    report = []
    report.append("=" * 60)
    report.append("SKINFORM FORMULATION ANALYSIS REPORT")
    report.append("=" * 60)
    report.append(f"\nFile: {filepath}")
    report.append(f"Product: {formulation.get('label', 'Unknown')}")
    report.append(f"ID: {formulation.get('id', 'Unknown')}")
    report.append(f"Category: {formulation.get('category', 'Unknown')}")
    
    # Phase analysis
    report.append("\n" + "-" * 40)
    report.append("PHASE ANALYSIS")
    report.append("-" * 40)
    phase_analysis = analyze_phases(formulation)
    report.append(f"Total phases: {phase_analysis['phase_count']}")
    report.append(f"Total concentration: {phase_analysis['total_concentration']:.1f}%")
    
    for phase in phase_analysis['phases']:
        report.append(f"\n  {phase['name']}:")
        report.append(f"    Ingredients: {phase['ingredient_count']}")
        report.append(f"    Concentration: {phase['concentration']:.1f}%")
        if phase['temperature']:
            report.append(f"    Temperature: {phase['temperature']}°C")
        if phase['mixing_time']:
            report.append(f"    Mixing time: {phase['mixing_time']} min")
    
    # Complexity analysis
    report.append("\n" + "-" * 40)
    report.append("COMPLEXITY ANALYSIS")
    report.append("-" * 40)
    complexity = analyze_complexity(formulation)
    report.append(f"Ingredient count: {complexity['ingredient_count']}")
    report.append(f"Phase count: {complexity['phase_count']}")
    report.append(f"Complexity score: {complexity['complexity_score']}")
    report.append(f"Complexity level: {complexity['complexity_level']}")
    
    # Warnings
    warnings = check_concentration_limits(formulation)
    if warnings:
        report.append("\n" + "-" * 40)
        report.append("WARNINGS")
        report.append("-" * 40)
        for warning in warnings:
            report.append(f"⚠️  {warning}")
    
    # Benefits
    benefits = formulation.get('benefits', [])
    if benefits:
        report.append("\n" + "-" * 40)
        report.append("CLAIMED BENEFITS")
        report.append("-" * 40)
        for benefit in benefits:
            report.append(f"  • {benefit}")
    
    # Target skin types
    skin_types = formulation.get('target_skin_type', [])
    if skin_types:
        report.append("\n" + "-" * 40)
        report.append("TARGET SKIN TYPES")
        report.append("-" * 40)
        for skin_type in skin_types:
            report.append(f"  • {skin_type}")
    
    report.append("\n" + "=" * 60)
    report.append("END OF REPORT")
    report.append("=" * 60)
    
    return "\n".join(report)


def main():
    if len(sys.argv) < 2:
        print("Usage: python analyze_formulation.py <formulation_file>")
        print("Example: python analyze_formulation.py vessels/formulations/retinol_night_cream.form")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    try:
        formulation = load_formulation(filepath)
        report = generate_report(formulation, filepath)
        print(report)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error parsing formulation file: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
