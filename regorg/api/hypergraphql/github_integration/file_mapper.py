"""
File Mapper

Maps GitHub repository folder structure to/from HyperGraphQL entities and relations.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from ..schema.types import EntityType, RelationType, HyperGraphType


class FileMapper:
    """Maps hypergraph data to/from GitHub repository file structure."""
    
    ENTITIES_DIR = "entities"
    RELATIONS_DIR = "relations"
    METADATA_FILE = "metadata.json"
    
    def __init__(self, base_path: str):
        """
        Initialize the file mapper.
        
        Args:
            base_path: Base directory path for the repository
        """
        self.base_path = Path(base_path)
        self.entities_path = self.base_path / self.ENTITIES_DIR
        self.relations_path = self.base_path / self.RELATIONS_DIR
    
    def load_entities_from_repo(self, org_context: str) -> List[EntityType]:
        """
        Load entities from repository folder structure.
        
        Expected structure:
        entities/
          consciousness/
            entity1.json
            entity2.json
          zone_concepts/
            entity3.json
        """
        entities = []
        
        if not self.entities_path.exists():
            return entities
        
        for entity_type_dir in self.entities_path.iterdir():
            if not entity_type_dir.is_dir():
                continue
            
            entity_type = entity_type_dir.name
            
            for entity_file in entity_type_dir.glob("*.json"):
                try:
                    with open(entity_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    entity = EntityType(
                        id=data.get('id', entity_file.stem),
                        name=data.get('name', entity_file.stem),
                        type=entity_type,
                        attributes=data.get('attributes', {}),
                        metadata=data.get('metadata', {}),
                        org_context=org_context,
                        created_at=self._parse_datetime(data.get('createdAt')),
                        updated_at=self._parse_datetime(data.get('updatedAt'))
                    )
                    entities.append(entity)
                except Exception as e:
                    print(f"Error loading entity from {entity_file}: {e}")
        
        return entities
    
    def load_relations_from_repo(self, org_context: str) -> List[RelationType]:
        """
        Load relations from repository folder structure.
        
        Expected structure:
        relations/
          consciousness_evolution/
            relation1.json
          zone_integration/
            relation2.json
        """
        relations = []
        
        if not self.relations_path.exists():
            return relations
        
        for relation_type_dir in self.relations_path.iterdir():
            if not relation_type_dir.is_dir():
                continue
            
            relation_type = relation_type_dir.name
            
            for relation_file in relation_type_dir.glob("*.json"):
                try:
                    with open(relation_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    
                    relation = RelationType(
                        id=data.get('id', relation_file.stem),
                        source_id=data['sourceId'],
                        target_id=data['targetId'],
                        relation_type=relation_type,
                        weight=data.get('weight', 1.0),
                        properties=data.get('properties', {}),
                        org_context=org_context,
                        created_at=self._parse_datetime(data.get('createdAt'))
                    )
                    relations.append(relation)
                except Exception as e:
                    print(f"Error loading relation from {relation_file}: {e}")
        
        return relations
    
    def save_entities_to_repo(self, entities: List[EntityType]) -> None:
        """Save entities to repository folder structure."""
        self.entities_path.mkdir(parents=True, exist_ok=True)
        
        # Group entities by type
        entities_by_type: Dict[str, List[EntityType]] = {}
        for entity in entities:
            if entity.type not in entities_by_type:
                entities_by_type[entity.type] = []
            entities_by_type[entity.type].append(entity)
        
        # Save each type to its own directory
        for entity_type, type_entities in entities_by_type.items():
            type_dir = self.entities_path / entity_type
            type_dir.mkdir(exist_ok=True)
            
            for entity in type_entities:
                file_path = type_dir / f"{entity.id}.json"
                data = {
                    'id': entity.id,
                    'name': entity.name,
                    'type': entity.type,
                    'attributes': entity.attributes,
                    'metadata': entity.metadata,
                    'orgContext': entity.org_context,
                    'createdAt': entity.created_at.isoformat() if entity.created_at else None,
                    'updatedAt': entity.updated_at.isoformat() if entity.updated_at else None,
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_relations_to_repo(self, relations: List[RelationType]) -> None:
        """Save relations to repository folder structure."""
        self.relations_path.mkdir(parents=True, exist_ok=True)
        
        # Group relations by type
        relations_by_type: Dict[str, List[RelationType]] = {}
        for relation in relations:
            if relation.relation_type not in relations_by_type:
                relations_by_type[relation.relation_type] = []
            relations_by_type[relation.relation_type].append(relation)
        
        # Save each type to its own directory
        for relation_type, type_relations in relations_by_type.items():
            type_dir = self.relations_path / relation_type
            type_dir.mkdir(exist_ok=True)
            
            for relation in type_relations:
                file_path = type_dir / f"{relation.id}.json"
                data = {
                    'id': relation.id,
                    'sourceId': relation.source_id,
                    'targetId': relation.target_id,
                    'relationType': relation.relation_type,
                    'weight': relation.weight,
                    'properties': relation.properties,
                    'orgContext': relation.org_context,
                    'createdAt': relation.created_at.isoformat() if relation.created_at else None,
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
    
    def save_metadata(self, metadata: Dict[str, Any]) -> None:
        """Save metadata about the hypergraph."""
        metadata_path = self.base_path / self.METADATA_FILE
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2, ensure_ascii=False)
    
    def load_metadata(self) -> Dict[str, Any]:
        """Load metadata about the hypergraph."""
        metadata_path = self.base_path / self.METADATA_FILE
        if metadata_path.exists():
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}
    
    @staticmethod
    def _parse_datetime(date_str: Optional[str]) -> Optional[datetime]:
        """Parse ISO format datetime string."""
        if date_str:
            try:
                return datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            except:
                pass
        return None
