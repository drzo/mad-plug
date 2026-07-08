"""
Relation Resolvers

Implements GraphQL resolvers for relation queries and mutations.
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import uuid

from ..schema.types import RelationType
from .storage import get_storage


class RelationResolver:
    """Resolver for relation-related GraphQL operations."""
    
    def __init__(self):
        self.storage = get_storage()
    
    def resolve_relation(self, obj, info, id: str) -> Optional[Dict[str, Any]]:
        """Resolve a single relation by ID."""
        relation = self.storage.get_relation(id)
        if relation:
            result = relation.to_dict()
            # Add entity field resolvers
            result['source'] = lambda: self._get_entity(relation.source_id)
            result['target'] = lambda: self._get_entity(relation.target_id)
            return result
        return None
    
    def resolve_relations(
        self,
        obj,
        info,
        type: Optional[str] = None,
        sourceId: Optional[str] = None,
        targetId: Optional[str] = None,
        orgContext: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Resolve multiple relations with filtering."""
        relations = self.storage.get_relations(
            relation_type=type,
            source_id=sourceId,
            target_id=targetId,
            org_context=orgContext
        )
        results = []
        for relation in relations:
            result = relation.to_dict()
            result['source'] = lambda r=relation: self._get_entity(r.source_id)
            result['target'] = lambda r=relation: self._get_entity(r.target_id)
            results.append(result)
        return results
    
    def _get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get an entity for relation resolution."""
        entity = self.storage.get_entity(entity_id)
        return entity.to_dict() if entity else None
    
    def resolve_create_relation(
        self,
        obj,
        info,
        sourceId: str,
        targetId: str,
        relationType: str,
        weight: float = 1.0,
        properties: Optional[Dict[str, Any]] = None,
        orgContext: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new relation."""
        relation = RelationType(
            id=str(uuid.uuid4()),
            source_id=sourceId,
            target_id=targetId,
            relation_type=relationType,
            weight=weight,
            properties=properties or {},
            org_context=orgContext,
            created_at=datetime.now()
        )
        
        self.storage.add_relation(relation)
        result = relation.to_dict()
        result['source'] = lambda: self._get_entity(sourceId)
        result['target'] = lambda: self._get_entity(targetId)
        return result
    
    def resolve_delete_relation(self, obj, info, id: str) -> bool:
        """Delete a relation."""
        return self.storage.delete_relation(id)
