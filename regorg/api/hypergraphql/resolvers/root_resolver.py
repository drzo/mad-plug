"""
Root Resolver

Combines all resolvers into a single root resolver for the GraphQL schema.
"""

from typing import Dict, Any

from .entity_resolvers import EntityResolver
from .relation_resolvers import RelationResolver
from .hypergraph_resolvers import HyperGraphResolver
from .organization_resolvers import OrganizationResolver


def get_root_resolver() -> Dict[str, Any]:
    """
    Get the root resolver with all query and mutation resolvers.
    
    Returns:
        Dictionary mapping GraphQL operations to resolver functions.
    """
    entity_resolver = EntityResolver()
    relation_resolver = RelationResolver()
    hypergraph_resolver = HyperGraphResolver()
    org_resolver = OrganizationResolver()
    
    return {
        'Query': {
            'entity': entity_resolver.resolve_entity,
            'entities': entity_resolver.resolve_entities,
            'relation': relation_resolver.resolve_relation,
            'relations': relation_resolver.resolve_relations,
            'hypergraph': hypergraph_resolver.resolve_hypergraph,
            'hypergraphs': hypergraph_resolver.resolve_hypergraphs,
            'organization': org_resolver.resolve_organization,
            'organizations': org_resolver.resolve_organizations,
            'navigateHypergraph': hypergraph_resolver.resolve_navigate_hypergraph,
        },
        'Mutation': {
            'createEntity': entity_resolver.resolve_create_entity,
            'updateEntity': entity_resolver.resolve_update_entity,
            'deleteEntity': entity_resolver.resolve_delete_entity,
            'createRelation': relation_resolver.resolve_create_relation,
            'deleteRelation': relation_resolver.resolve_delete_relation,
            'createHyperGraph': hypergraph_resolver.resolve_create_hypergraph,
            'createOrganization': org_resolver.resolve_create_organization,
            'syncFromGitHub': org_resolver.resolve_sync_from_github,
            'syncToGitHub': org_resolver.resolve_sync_to_github,
        }
    }
