#!/usr/bin/env python3
"""
Example: Using HyperGraphQL API with RegimA Organizational Data

This example demonstrates how to map RegimA's organizational consciousness
and Zone Concept frameworks to the HyperGraphQL API.
"""

import json
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from api.client import HyperGraphQLClient


def load_regima_data():
    """Load RegimA organizational data."""
    base_path = Path(__file__).parent.parent.parent
    
    with open(base_path / 'regcyc.json', 'r') as f:
        regcyc = json.load(f)
    
    with open(base_path / 'cycleCompletion.json', 'r') as f:
        cycle_completion = json.load(f)
    
    return regcyc, cycle_completion


def create_consciousness_entities(client, org_id, regcyc_data):
    """Create entities for professional development."""
    print("\n=== Creating Professional Development Entities ===")
    
    consciousness_data = regcyc_data.get('organizationalConsciousness', {})
    
    # Create main professional development entity
    consciousness_entity = client.create_entity(
        name="Professional Development",
        entity_type="professional_excellence",
        attributes={
            "state": consciousness_data.get('currentState'),
            "level": consciousness_data.get('evolutionLevel'),
            "capabilities": consciousness_data.get('professionalCapabilities', {})
        },
        org_context=org_id
    )
    
    print(f"Created: {consciousness_entity['name']} (ID: {consciousness_entity['id']})")
    return consciousness_entity


def create_zone_concept_entities(client, org_id, regcyc_data):
    """Create entities for Zone Concept framework."""
    print("\n=== Creating Zone Concept Entities ===")
    
    zone_data = regcyc_data.get('zoneConceptFramework', {}).get('coreElements', {})
    entities = []
    
    for zone_name, zone_info in zone_data.items():
        entity = client.create_entity(
            name=zone_name.replace('_', ' ').title(),
            entity_type="zone_concept",
            attributes={
                "relevance": zone_info.get('relevance'),
                "focus": zone_info.get('focus'),
                "technologies": zone_info.get('keyTechnologies', []),
                "evidence": zone_info.get('clinicalEvidence', {})
            },
            org_context=org_id
        )
        entities.append(entity)
        print(f"Created: {entity['name']} (ID: {entity['id']})")
    
    return entities


def main():
    """Main execution."""
    print("=" * 60)
    print("RegimA HyperGraphQL API Example")
    print("=" * 60)
    
    # Initialize client
    client = HyperGraphQLClient("http://localhost:8080")
    
    # Load RegimA data
    print("\nLoading RegimA organizational data...")
    regcyc_data, cycle_completion = load_regima_data()
    
    # Create organization
    print("\nCreating RegimA organization...")
    org_result = client.create_organization(
        name="RegimA",
        org_type="repo",
        github_repo="/home/runner/work/regorg/regorg"
    )
    org_id = org_result['data']['id']
    print(f"Organization created: {org_id}")
    
    # Create entities for professional development
    consciousness_entity = create_consciousness_entities(client, org_id, regcyc_data)
    
    # Create entities for Zone Concept framework
    zone_entities = create_zone_concept_entities(client, org_id, regcyc_data)
    
    print("\n" + "=" * 60)
    print("Example completed successfully!")
    print(f"Created {1 + len(zone_entities)} entities")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\nError: {e}")
        print("\nMake sure the API server is running:")
        print("  python -m api.server")
        sys.exit(1)
