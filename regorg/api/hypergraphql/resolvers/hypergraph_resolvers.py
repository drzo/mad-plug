"""
HyperGraph Resolvers

Implements GraphQL resolvers for hypergraph queries, navigation, and mutations.
"""

from typing import Dict, List, Any, Optional, Set
from datetime import datetime
import uuid

from ..schema.types import HyperGraphType, EntityType, RelationType
from .storage import get_storage


class HyperGraphResolver:
    """Resolver for hypergraph-related GraphQL operations."""
    
    def __init__(self):
        self.storage = get_storage()
    
    def resolve_hypergraph(self, obj, info, id: str) -> Optional[Dict[str, Any]]:
        """Resolve a single hypergraph by ID."""
        hypergraph = self.storage.get_hypergraph(id)
        if hypergraph:
            return hypergraph.to_dict()
        return None
    
    def resolve_hypergraphs(
        self,
        obj,
        info,
        orgContext: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Resolve multiple hypergraphs with filtering."""
        hypergraphs = self.storage.get_hypergraphs(org_context=orgContext)
        return [h.to_dict() for h in hypergraphs]
    
    def resolve_navigate_hypergraph(
        self,
        obj,
        info,
        startEntityId: str,
        maxDepth: Optional[int] = None,
        relationType: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Navigate hypergraph from a starting entity, following relations.
        
        This implements hypergraph traversal with depth limits and relation filtering.
        """
        start_entity = self.storage.get_entity(startEntityId)
        if not start_entity:
            return None
        
        # Create a new hypergraph for the navigation result
        nav_hypergraph = HyperGraphType(
            id=str(uuid.uuid4()),
            name=f"Navigation from {start_entity.name}",
            org_context=start_entity.org_context
        )
        
        # Track visited entities to avoid cycles
        visited: Set[str] = set()
        
        # Breadth-first traversal
        current_depth = 0
        current_level = [startEntityId]
        
        while current_level and (maxDepth is None or current_depth <= maxDepth):
            next_level = []
            
            for entity_id in current_level:
                if entity_id in visited:
                    continue
                
                visited.add(entity_id)
                
                # Add entity to result hypergraph
                entity = self.storage.get_entity(entity_id)
                if entity:
                    nav_hypergraph.add_entity(entity)
                
                # Get relations for this entity
                relations = self.storage.get_relations(source_id=entity_id)
                relations.extend(self.storage.get_relations(target_id=entity_id))
                
                for relation in relations:
                    # Filter by relation type if specified
                    if relationType and relation.relation_type != relationType:
                        continue
                    
                    # Add relation to result
                    nav_hypergraph.add_relation(relation)
                    
                    # Add connected entities to next level
                    if relation.source_id == entity_id and relation.target_id not in visited:
                        next_level.append(relation.target_id)
                    elif relation.target_id == entity_id and relation.source_id not in visited:
                        next_level.append(relation.source_id)
            
            current_level = next_level
            current_depth += 1
        
        return nav_hypergraph.to_dict()
    
    def resolve_create_hypergraph(
        self,
        obj,
        info,
        name: str,
        orgContext: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create a new hypergraph."""
        hypergraph = HyperGraphType(
            id=str(uuid.uuid4()),
            name=name,
            org_context=orgContext,
            metadata=metadata or {}
        )
        
        self.storage.add_hypergraph(hypergraph)
        return hypergraph.to_dict()
