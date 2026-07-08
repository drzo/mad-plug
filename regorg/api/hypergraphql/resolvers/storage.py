"""
In-Memory Storage for HyperGraph Data

Provides a simple storage layer for entities, relations, hypergraphs, and organizations.
In production, this would be replaced with a proper database.
"""

from typing import Dict, List, Optional
from ..schema.types import EntityType, RelationType, HyperGraphType, OrganizationType


class HyperGraphStorage:
    """In-memory storage for hypergraph data."""
    
    def __init__(self):
        self.entities: Dict[str, EntityType] = {}
        self.relations: Dict[str, RelationType] = {}
        self.hypergraphs: Dict[str, HyperGraphType] = {}
        self.organizations: Dict[str, OrganizationType] = {}
    
    # Entity operations
    def add_entity(self, entity: EntityType) -> EntityType:
        """Add an entity to storage."""
        self.entities[entity.id] = entity
        return entity
    
    def get_entity(self, entity_id: str) -> Optional[EntityType]:
        """Retrieve an entity by ID."""
        return self.entities.get(entity_id)
    
    def get_entities(
        self,
        entity_type: Optional[str] = None,
        org_context: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[EntityType]:
        """Get entities with optional filtering."""
        entities = list(self.entities.values())
        
        if entity_type:
            entities = [e for e in entities if e.type == entity_type]
        
        if org_context:
            entities = [e for e in entities if e.org_context == org_context]
        
        return entities[offset:offset + limit]
    
    def update_entity(self, entity_id: str, updates: Dict) -> Optional[EntityType]:
        """Update an entity."""
        entity = self.entities.get(entity_id)
        if entity:
            if 'name' in updates:
                entity.name = updates['name']
            if 'attributes' in updates:
                entity.attributes.update(updates['attributes'])
        return entity
    
    def delete_entity(self, entity_id: str) -> bool:
        """Delete an entity."""
        if entity_id in self.entities:
            del self.entities[entity_id]
            # Clean up relations
            self.relations = {
                k: v for k, v in self.relations.items()
                if v.source_id != entity_id and v.target_id != entity_id
            }
            return True
        return False
    
    # Relation operations
    def add_relation(self, relation: RelationType) -> RelationType:
        """Add a relation to storage."""
        self.relations[relation.id] = relation
        return relation
    
    def get_relation(self, relation_id: str) -> Optional[RelationType]:
        """Retrieve a relation by ID."""
        return self.relations.get(relation_id)
    
    def get_relations(
        self,
        relation_type: Optional[str] = None,
        source_id: Optional[str] = None,
        target_id: Optional[str] = None,
        org_context: Optional[str] = None
    ) -> List[RelationType]:
        """Get relations with optional filtering."""
        relations = list(self.relations.values())
        
        if relation_type:
            relations = [r for r in relations if r.relation_type == relation_type]
        
        if source_id:
            relations = [r for r in relations if r.source_id == source_id]
        
        if target_id:
            relations = [r for r in relations if r.target_id == target_id]
        
        if org_context:
            relations = [r for r in relations if r.org_context == org_context]
        
        return relations
    
    def delete_relation(self, relation_id: str) -> bool:
        """Delete a relation."""
        if relation_id in self.relations:
            del self.relations[relation_id]
            return True
        return False
    
    # HyperGraph operations
    def add_hypergraph(self, hypergraph: HyperGraphType) -> HyperGraphType:
        """Add a hypergraph to storage."""
        self.hypergraphs[hypergraph.id] = hypergraph
        return hypergraph
    
    def get_hypergraph(self, hypergraph_id: str) -> Optional[HyperGraphType]:
        """Retrieve a hypergraph by ID."""
        return self.hypergraphs.get(hypergraph_id)
    
    def get_hypergraphs(self, org_context: Optional[str] = None) -> List[HyperGraphType]:
        """Get hypergraphs with optional filtering."""
        hypergraphs = list(self.hypergraphs.values())
        
        if org_context:
            hypergraphs = [h for h in hypergraphs if h.org_context == org_context]
        
        return hypergraphs
    
    # Organization operations
    def add_organization(self, org: OrganizationType) -> OrganizationType:
        """Add an organization to storage."""
        self.organizations[org.id] = org
        return org
    
    def get_organization(self, org_id: str) -> Optional[OrganizationType]:
        """Retrieve an organization by ID."""
        return self.organizations.get(org_id)
    
    def get_organizations(
        self,
        org_type: Optional[str] = None,
        parent_org_id: Optional[str] = None
    ) -> List[OrganizationType]:
        """Get organizations with optional filtering."""
        orgs = list(self.organizations.values())
        
        if org_type:
            orgs = [o for o in orgs if o.type == org_type]
        
        if parent_org_id:
            orgs = [o for o in orgs if o.parent_org_id == parent_org_id]
        
        return orgs


# Global storage instance
_storage = HyperGraphStorage()


def get_storage() -> HyperGraphStorage:
    """Get the global storage instance."""
    return _storage
