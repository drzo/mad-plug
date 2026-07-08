"""
Entity Resolvers

Implements GraphQL resolvers for entity queries and mutations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from ..schema.types import EntityType
from .storage import get_storage


class EntityResolver:
    """Resolver for entity-related GraphQL operations."""
    
    def __init__(self):
        self.storage = get_storage()
    
    def resolve_entity(self, obj, info, id: str) -> Optional[Dict[str, Any]]:
        """Resolve a single entity by ID."""
        entity = self.storage.get_entity(id)
        if entity:
            result = entity.to_dict()
            # Add relations field resolver
            result['relations'] = lambda: self._get_entity_relations(id)
            return result
        return None
    
    def resolve_entities(
        self,
        obj,
        info,
        type: Optional[str] = None,
        orgContext: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Resolve multiple entities with filtering."""
        entities = self.storage.get_entities(
            entity_type=type,
            org_context=orgContext,
            limit=limit,
            offset=offset
        )
        results = []
        for entity in entities:
            result = entity.to_dict()
            result['relations'] = lambda eid=entity.id: self._get_entity_relations(eid)
            results.append(result)
        return results
    
    def _get_entity_relations(self, entity_id: str) -> List[Dict[str, Any]]:
        """Get all relations for an entity."""
        from .relation_resolvers import RelationResolver
        resolver = RelationResolver()
        
        relations = self.storage.get_relations(source_id=entity_id)
        relations.extend(self.storage.get_relations(target_id=entity_id))
        
        return [r.to_dict() for r in relations]
    
    def resolve_create_entity(
        self,
        obj,
        info,
        name: str,
        type: str,
        attributes: Optional[Dict[str, Any]] = None,
        orgContext: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new entity."""
        entity = EntityType(
            id=str(uuid.uuid4()),
            name=name,
            type=type,
            attributes=attributes or {},
            org_context=orgContext,
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        self.storage.add_entity(entity)
        result = entity.to_dict()
        result['relations'] = lambda: self._get_entity_relations(entity.id)
        return result
    
    def resolve_update_entity(
        self,
        obj,
        info,
        id: str,
        name: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """Update an existing entity."""
        updates = {}
        if name:
            updates['name'] = name
        if attributes:
            updates['attributes'] = attributes
        
        entity = self.storage.update_entity(id, updates)
        if entity:
            entity.updated_at = datetime.now()
            result = entity.to_dict()
            result['relations'] = lambda: self._get_entity_relations(id)
            return result
        return None
    
    def resolve_delete_entity(self, obj, info, id: str) -> bool:
        """Delete an entity."""
        return self.storage.delete_entity(id)
