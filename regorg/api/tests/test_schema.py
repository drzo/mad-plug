"""
Tests for HyperGraphQL Schema
"""

import unittest
from datetime import datetime

from ..hypergraphql.schema.types import (
    EntityType, RelationType, HyperGraphType, OrganizationType
)
from ..hypergraphql.schema.builder import build_schema


class TestSchemaTypes(unittest.TestCase):
    """Test schema type definitions."""
    
    def test_entity_type_creation(self):
        """Test EntityType creation and conversion."""
        entity = EntityType(
            id="e1",
            name="Test Entity",
            type="consciousness",
            attributes={"level": "quantum"},
            org_context="org1"
        )
        
        self.assertEqual(entity.id, "e1")
        self.assertEqual(entity.name, "Test Entity")
        self.assertEqual(entity.type, "consciousness")
        self.assertEqual(entity.attributes["level"], "quantum")
        
        # Test to_dict
        data = entity.to_dict()
        self.assertEqual(data["id"], "e1")
        self.assertEqual(data["name"], "Test Entity")
        self.assertEqual(data["orgContext"], "org1")
    
    def test_relation_type_creation(self):
        """Test RelationType creation and conversion."""
        relation = RelationType(
            id="r1",
            source_id="e1",
            target_id="e2",
            relation_type="evolution",
            weight=0.8,
            org_context="org1"
        )
        
        self.assertEqual(relation.id, "r1")
        self.assertEqual(relation.source_id, "e1")
        self.assertEqual(relation.target_id, "e2")
        self.assertEqual(relation.weight, 0.8)
        
        # Test to_dict
        data = relation.to_dict()
        self.assertEqual(data["sourceId"], "e1")
        self.assertEqual(data["targetId"], "e2")
        self.assertEqual(data["relationType"], "evolution")
    
    def test_hypergraph_type(self):
        """Test HyperGraphType operations."""
        hypergraph = HyperGraphType(
            id="hg1",
            name="Test HyperGraph",
            org_context="org1"
        )
        
        # Add entity
        entity = EntityType(id="e1", name="Entity 1", type="test")
        hypergraph.add_entity(entity)
        self.assertEqual(len(hypergraph.entities), 1)
        
        # Add relation
        relation = RelationType(
            id="r1",
            source_id="e1",
            target_id="e2",
            relation_type="test"
        )
        hypergraph.add_relation(relation)
        self.assertEqual(len(hypergraph.relations), 1)
        
        # Get entity by ID
        found = hypergraph.get_entity_by_id("e1")
        self.assertIsNotNone(found)
        self.assertEqual(found.id, "e1")
        
        # Get relations for entity
        relations = hypergraph.get_relations_for_entity("e1")
        self.assertEqual(len(relations), 1)
    
    def test_organization_type(self):
        """Test OrganizationType operations."""
        org = OrganizationType(
            id="org1",
            name="Test Org",
            type="repo",
            github_repo="/path/to/repo"
        )
        
        hypergraph = HyperGraphType(id="hg1", name="HG1")
        org.add_hypergraph(hypergraph)
        
        self.assertEqual(len(org.hypergraphs), 1)
        self.assertEqual(hypergraph.org_context, "org1")
        
        # Test to_dict
        data = org.to_dict()
        self.assertEqual(data["name"], "Test Org")
        self.assertEqual(data["type"], "repo")
        self.assertEqual(data["githubRepo"], "/path/to/repo")
    
    def test_schema_build(self):
        """Test schema building."""
        schema = build_schema()
        self.assertIsNotNone(schema)
        self.assertIsNotNone(schema.query_type)
        self.assertIsNotNone(schema.mutation_type)


if __name__ == '__main__':
    unittest.main()
