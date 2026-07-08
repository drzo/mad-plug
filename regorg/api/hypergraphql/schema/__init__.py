"""
HyperGraphQL Schema Module

Defines GraphQL type definitions for entities, relations, and hypergraph structures
mapped to HyperGNN entities with organization-aware schemas.
"""

from .types import EntityType, RelationType, HyperGraphType, OrganizationType
from .builder import build_schema

__all__ = ['EntityType', 'RelationType', 'HyperGraphType', 'OrganizationType', 'build_schema']
