"""
GraphQL Type Definitions for HyperGraphQL

Defines entity types, relation types, and hypergraph structures
for RegimA's HyperGNN mapping.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class EntityType:
    """
    Represents an entity in the hypergraph.
    
    Entities can be consciousness elements, zone concepts, or organizational components.
    """
    id: str
    name: str
    type: str
    attributes: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    org_context: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert entity to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'attributes': self.attributes,
            'metadata': self.metadata,
            'orgContext': self.org_context,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }


@dataclass
class RelationType:
    """
    Represents a relation between entities in the hypergraph.
    
    Relations capture connections like consciousness evolution, zone integration,
    or organizational dependencies.
    """
    id: str
    source_id: str
    target_id: str
    relation_type: str
    weight: float = 1.0
    properties: Dict[str, Any] = field(default_factory=dict)
    org_context: Optional[str] = None
    created_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert relation to dictionary representation."""
        return {
            'id': self.id,
            'sourceId': self.source_id,
            'targetId': self.target_id,
            'relationType': self.relation_type,
            'weight': self.weight,
            'properties': self.properties,
            'orgContext': self.org_context,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }


@dataclass
class HyperGraphType:
    """
    Represents a hypergraph structure containing entities and relations.
    
    Supports multi-way relationships and hierarchical organization mapping.
    """
    id: str
    name: str
    entities: List[EntityType] = field(default_factory=list)
    relations: List[RelationType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    org_context: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert hypergraph to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'entities': [e.to_dict() for e in self.entities],
            'relations': [r.to_dict() for r in self.relations],
            'metadata': self.metadata,
            'orgContext': self.org_context,
        }
    
    def add_entity(self, entity: EntityType) -> None:
        """Add an entity to the hypergraph."""
        self.entities.append(entity)
    
    def add_relation(self, relation: RelationType) -> None:
        """Add a relation to the hypergraph."""
        self.relations.append(relation)
    
    def get_entity_by_id(self, entity_id: str) -> Optional[EntityType]:
        """Retrieve an entity by its ID."""
        for entity in self.entities:
            if entity.id == entity_id:
                return entity
        return None
    
    def get_relations_for_entity(self, entity_id: str) -> List[RelationType]:
        """Get all relations involving a specific entity."""
        return [
            r for r in self.relations
            if r.source_id == entity_id or r.target_id == entity_id
        ]


@dataclass
class OrganizationType:
    """
    Represents an organization context for hypergraph structures.
    
    Supports org-level aggregation, repo mapping, and enterprise scaling.
    """
    id: str
    name: str
    type: str  # 'repo', 'org', 'enterprise'
    hypergraphs: List[HyperGraphType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    parent_org_id: Optional[str] = None
    github_repo: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert organization to dictionary representation."""
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'hypergraphs': [h.to_dict() for h in self.hypergraphs],
            'metadata': self.metadata,
            'parentOrgId': self.parent_org_id,
            'githubRepo': self.github_repo,
        }
    
    def add_hypergraph(self, hypergraph: HyperGraphType) -> None:
        """Add a hypergraph to this organization."""
        hypergraph.org_context = self.id
        self.hypergraphs.append(hypergraph)


# GraphQL Schema Definition String
GRAPHQL_SCHEMA = """
type Entity {
  id: ID!
  name: String!
  type: String!
  attributes: JSON
  metadata: JSON
  orgContext: String
  createdAt: String
  updatedAt: String
  relations: [Relation!]
}

type Relation {
  id: ID!
  sourceId: ID!
  targetId: ID!
  relationType: String!
  weight: Float!
  properties: JSON
  orgContext: String
  createdAt: String
  source: Entity
  target: Entity
}

type HyperGraph {
  id: ID!
  name: String!
  entities: [Entity!]!
  relations: [Relation!]!
  metadata: JSON
  orgContext: String
}

type Organization {
  id: ID!
  name: String!
  type: String!
  hypergraphs: [HyperGraph!]!
  metadata: JSON
  parentOrgId: String
  githubRepo: String
  childOrganizations: [Organization!]
}

type Query {
  entity(id: ID!): Entity
  entities(type: String, orgContext: String, limit: Int, offset: Int): [Entity!]!
  
  relation(id: ID!): Relation
  relations(type: String, sourceId: ID, targetId: ID, orgContext: String): [Relation!]!
  
  hypergraph(id: ID!): HyperGraph
  hypergraphs(orgContext: String): [HyperGraph!]!
  
  organization(id: ID!): Organization
  organizations(type: String, parentOrgId: String): [Organization!]!
  
  navigateHypergraph(startEntityId: ID!, maxDepth: Int, relationType: String): HyperGraph
}

type Mutation {
  createEntity(name: String!, type: String!, attributes: JSON, orgContext: String): Entity!
  updateEntity(id: ID!, name: String, attributes: JSON): Entity!
  deleteEntity(id: ID!): Boolean!
  
  createRelation(sourceId: ID!, targetId: ID!, relationType: String!, weight: Float, properties: JSON, orgContext: String): Relation!
  deleteRelation(id: ID!): Boolean!
  
  createHyperGraph(name: String!, orgContext: String, metadata: JSON): HyperGraph!
  
  createOrganization(name: String!, type: String!, parentOrgId: String, githubRepo: String): Organization!
  
  syncFromGitHub(orgId: ID!, repoPath: String!): Organization!
  syncToGitHub(orgId: ID!): Boolean!
}

scalar JSON
"""
