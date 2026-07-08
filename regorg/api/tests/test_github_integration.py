"""
Tests for GitHub Integration
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path

from ..hypergraphql.github_integration.file_mapper import FileMapper
from ..hypergraphql.github_integration.scaler import HyperGraphScaler
from ..hypergraphql.schema.types import EntityType, RelationType, HyperGraphType


class TestFileMapper(unittest.TestCase):
    """Test FileMapper."""
    
    def setUp(self):
        """Set up test directory."""
        self.test_dir = tempfile.mkdtemp()
        self.mapper = FileMapper(self.test_dir)
    
    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)
    
    def test_save_and_load_entities(self):
        """Test saving and loading entities."""
        entities = [
            EntityType(
                id="e1",
                name="Entity 1",
                type="consciousness",
                attributes={"level": "quantum"}
            ),
            EntityType(
                id="e2",
                name="Entity 2",
                type="consciousness",
                attributes={"level": "transcendent"}
            )
        ]
        
        # Save entities
        self.mapper.save_entities_to_repo(entities)
        
        # Verify directory structure
        entities_dir = Path(self.test_dir) / "entities" / "consciousness"
        self.assertTrue(entities_dir.exists())
        self.assertTrue((entities_dir / "e1.json").exists())
        
        # Load entities back
        loaded = self.mapper.load_entities_from_repo("org1")
        self.assertEqual(len(loaded), 2)
        # Check that we have both entities (order may vary)
        names = {e.name for e in loaded}
        self.assertIn("Entity 1", names)
        self.assertIn("Entity 2", names)
        # Check attributes
        entity1 = next(e for e in loaded if e.name == "Entity 1")
        self.assertEqual(entity1.attributes["level"], "quantum")
    
    def test_save_and_load_relations(self):
        """Test saving and loading relations."""
        relations = [
            RelationType(
                id="r1",
                source_id="e1",
                target_id="e2",
                relation_type="evolution",
                weight=0.9
            )
        ]
        
        # Save relations
        self.mapper.save_relations_to_repo(relations)
        
        # Verify directory structure
        relations_dir = Path(self.test_dir) / "relations" / "evolution"
        self.assertTrue(relations_dir.exists())
        self.assertTrue((relations_dir / "r1.json").exists())
        
        # Load relations back
        loaded = self.mapper.load_relations_from_repo("org1")
        self.assertEqual(len(loaded), 1)
        self.assertEqual(loaded[0].source_id, "e1")
        self.assertEqual(loaded[0].weight, 0.9)
    
    def test_save_and_load_metadata(self):
        """Test metadata operations."""
        metadata = {
            "version": "1.0",
            "organization": "Test Org",
            "entity_count": 10
        }
        
        self.mapper.save_metadata(metadata)
        loaded = self.mapper.load_metadata()
        
        self.assertEqual(loaded["version"], "1.0")
        self.assertEqual(loaded["entity_count"], 10)


class TestHyperGraphScaler(unittest.TestCase):
    """Test HyperGraphScaler."""
    
    def setUp(self):
        """Set up test hypergraph."""
        self.hypergraph = HyperGraphType(
            id="hg1",
            name="Test HyperGraph"
        )
        
        # Add entities of different types
        for i in range(3):
            self.hypergraph.add_entity(EntityType(
                id=f"e1_{i}",
                name=f"Type1 Entity {i}",
                type="type1"
            ))
        
        for i in range(2):
            self.hypergraph.add_entity(EntityType(
                id=f"e2_{i}",
                name=f"Type2 Entity {i}",
                type="type2"
            ))
        
        # Add relations
        self.hypergraph.add_relation(RelationType(
            id="r1",
            source_id="e1_0",
            target_id="e1_1",
            relation_type="same_type"
        ))
        self.hypergraph.add_relation(RelationType(
            id="r2",
            source_id="e1_1",
            target_id="e2_0",
            relation_type="cross_type"
        ))
    
    def test_compress_by_type(self):
        """Test type-based compression."""
        scaler = HyperGraphScaler()
        compressed = scaler.compress_hypergraph(
            self.hypergraph,
            compression_strategy='type_aggregation'
        )
        
        # Should have 2 aggregate entities (type1 and type2)
        self.assertEqual(len(compressed.entities), 2)
        
        # Check metadata
        self.assertEqual(
            compressed.metadata['original_entity_count'],
            5
        )
        
        # Check aggregate entity attributes
        type1_entity = next(e for e in compressed.entities if e.type == "type1")
        self.assertEqual(type1_entity.attributes['count'], 3)
    
    def test_compress_by_cluster(self):
        """Test cluster-based compression."""
        scaler = HyperGraphScaler()
        compressed = scaler.compress_hypergraph(
            self.hypergraph,
            compression_strategy='cluster'
        )
        
        # Should have clusters based on connectivity
        self.assertGreater(len(compressed.entities), 0)
    
    def test_expand_to_org_level(self):
        """Test expansion to organization level."""
        scaler = HyperGraphScaler()
        
        hg1 = HyperGraphType(id="hg1", name="HG1")
        hg2 = HyperGraphType(id="hg2", name="HG2")
        
        org = scaler.expand_to_org_level([hg1, hg2], "Test Organization")
        
        self.assertEqual(org.name, "Test Organization")
        self.assertEqual(org.type, "org")
        self.assertEqual(len(org.hypergraphs), 2)
        self.assertEqual(org.metadata['repo_count'], 2)


if __name__ == '__main__':
    unittest.main()
