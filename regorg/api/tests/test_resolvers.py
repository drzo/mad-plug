"""
Tests for HyperGraphQL Resolvers
"""

import unittest

from ..hypergraphql.resolvers.storage import HyperGraphStorage
from ..hypergraphql.resolvers.entity_resolvers import EntityResolver
from ..hypergraphql.resolvers.relation_resolvers import RelationResolver
from ..hypergraphql.resolvers.hypergraph_resolvers import HyperGraphResolver
from ..hypergraphql.resolvers.organization_resolvers import OrganizationResolver
from ..hypergraphql.schema.types import EntityType, RelationType


class TestEntityResolver(unittest.TestCase):
    """Test EntityResolver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.resolver = EntityResolver()
        self.storage = self.resolver.storage
        # Clear storage
        self.storage.entities.clear()
        self.storage.relations.clear()
    
    def test_create_entity(self):
        """Test entity creation."""
        result = self.resolver.resolve_create_entity(
            None, None,
            name="Test Entity",
            type="consciousness",
            attributes={"level": "quantum"},
            orgContext="org1"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test Entity")
        self.assertEqual(result["type"], "consciousness")
        self.assertEqual(result["orgContext"], "org1")
        
        # Verify storage
        entity_id = result["id"]
        stored = self.storage.get_entity(entity_id)
        self.assertIsNotNone(stored)
        self.assertEqual(stored.name, "Test Entity")
    
    def test_resolve_entity(self):
        """Test entity retrieval."""
        # Create entity first
        created = self.resolver.resolve_create_entity(
            None, None,
            name="Test Entity",
            type="test"
        )
        entity_id = created["id"]
        
        # Retrieve it
        result = self.resolver.resolve_entity(None, None, id=entity_id)
        self.assertIsNotNone(result)
        self.assertEqual(result["id"], entity_id)
        self.assertEqual(result["name"], "Test Entity")
    
    def test_resolve_entities_with_filter(self):
        """Test entity listing with filters."""
        # Create multiple entities
        self.resolver.resolve_create_entity(None, None, name="E1", type="type1", orgContext="org1")
        self.resolver.resolve_create_entity(None, None, name="E2", type="type2", orgContext="org1")
        self.resolver.resolve_create_entity(None, None, name="E3", type="type1", orgContext="org2")
        
        # Filter by type
        results = self.resolver.resolve_entities(None, None, type="type1")
        self.assertEqual(len(results), 2)
        
        # Filter by org
        results = self.resolver.resolve_entities(None, None, orgContext="org1")
        self.assertEqual(len(results), 2)
        
        # Filter by both
        results = self.resolver.resolve_entities(None, None, type="type1", orgContext="org1")
        self.assertEqual(len(results), 1)
    
    def test_update_entity(self):
        """Test entity update."""
        # Create entity
        created = self.resolver.resolve_create_entity(None, None, name="Original", type="test")
        entity_id = created["id"]
        
        # Update it
        result = self.resolver.resolve_update_entity(
            None, None,
            id=entity_id,
            name="Updated",
            attributes={"new": "value"}
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Updated")
        self.assertEqual(result["attributes"]["new"], "value")
    
    def test_delete_entity(self):
        """Test entity deletion."""
        # Create entity
        created = self.resolver.resolve_create_entity(None, None, name="To Delete", type="test")
        entity_id = created["id"]
        
        # Delete it
        result = self.resolver.resolve_delete_entity(None, None, id=entity_id)
        self.assertTrue(result)
        
        # Verify it's gone
        retrieved = self.resolver.resolve_entity(None, None, id=entity_id)
        self.assertIsNone(retrieved)


class TestRelationResolver(unittest.TestCase):
    """Test RelationResolver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.entity_resolver = EntityResolver()
        self.resolver = RelationResolver()
        self.storage = self.resolver.storage
        # Clear storage
        self.storage.entities.clear()
        self.storage.relations.clear()
        
        # Create test entities
        e1 = self.entity_resolver.resolve_create_entity(None, None, name="E1", type="test")
        e2 = self.entity_resolver.resolve_create_entity(None, None, name="E2", type="test")
        self.entity1_id = e1["id"]
        self.entity2_id = e2["id"]
    
    def test_create_relation(self):
        """Test relation creation."""
        result = self.resolver.resolve_create_relation(
            None, None,
            self.entity1_id,
            self.entity2_id,
            "evolution",
            0.8,
            {"strength": "strong"},
            "org1"
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result["sourceId"], self.entity1_id)
        self.assertEqual(result["targetId"], self.entity2_id)
        self.assertEqual(result["relationType"], "evolution")
        self.assertEqual(result["weight"], 0.8)
    
    def test_resolve_relations_with_filter(self):
        """Test relation listing with filters."""
        # Create multiple relations
        self.resolver.resolve_create_relation(
            None, None,
            self.entity1_id,
            self.entity2_id,
            "type1"
        )
        self.resolver.resolve_create_relation(
            None, None,
            self.entity2_id,
            self.entity1_id,
            "type2"
        )
        
        # Filter by source
        results = self.resolver.resolve_relations(None, None, sourceId=self.entity1_id)
        self.assertEqual(len(results), 1)
        
        # Filter by type
        results = self.resolver.resolve_relations(None, None, type="type1")
        self.assertEqual(len(results), 1)


class TestHyperGraphResolver(unittest.TestCase):
    """Test HyperGraphResolver."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.entity_resolver = EntityResolver()
        self.relation_resolver = RelationResolver()
        self.resolver = HyperGraphResolver()
        self.storage = self.resolver.storage
        # Clear storage
        self.storage.entities.clear()
        self.storage.relations.clear()
        self.storage.hypergraphs.clear()
    
    def test_create_hypergraph(self):
        """Test hypergraph creation."""
        result = self.resolver.resolve_create_hypergraph(
            None, None,
            "Test HyperGraph",
            "org1",
            {"version": "1.0"}
        )
        
        self.assertIsNotNone(result)
        self.assertEqual(result["name"], "Test HyperGraph")
        self.assertEqual(result["orgContext"], "org1")
    
    def test_navigate_hypergraph(self):
        """Test hypergraph navigation."""
        # Create a chain: e1 -> e2 -> e3
        e1 = self.entity_resolver.resolve_create_entity(None, None, "E1", "test")
        e2 = self.entity_resolver.resolve_create_entity(None, None, "E2", "test")
        e3 = self.entity_resolver.resolve_create_entity(None, None, "E3", "test")
        
        self.relation_resolver.resolve_create_relation(
            None, None, e1["id"], e2["id"], "next"
        )
        self.relation_resolver.resolve_create_relation(
            None, None, e2["id"], e3["id"], "next"
        )
        
        # Navigate from e1
        result = self.resolver.resolve_navigate_hypergraph(
            None, None,
            e1["id"],
            2
        )
        
        self.assertIsNotNone(result)
        self.assertGreaterEqual(len(result["entities"]), 3)
        self.assertGreaterEqual(len(result["relations"]), 2)


if __name__ == '__main__':
    unittest.main()
