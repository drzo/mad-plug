"""
GraphQL Schema Builder

Builds the executable GraphQL schema with resolvers.
"""

from graphql import (
    GraphQLSchema, GraphQLObjectType, GraphQLField, GraphQLArgument,
    GraphQLString, GraphQLInt, GraphQLFloat, GraphQLBoolean, GraphQLID,
    GraphQLList, GraphQLNonNull, GraphQLScalarType
)
from ..resolvers import (
    EntityResolver, RelationResolver, HyperGraphResolver, OrganizationResolver
)


# JSON Scalar
def serialize_json(value):
    return value

def parse_json_value(value):
    return value

GraphQLJSON = GraphQLScalarType(
    name='JSON',
    serialize=serialize_json,
    parse_value=parse_json_value,
    parse_literal=lambda ast, variables=None: ast.value
)


def build_schema():
    """
    Build and return the executable GraphQL schema with resolvers attached.
    
    Returns:
        GraphQL Schema object ready for query execution.
    """
    # Initialize resolvers
    entity_resolver = EntityResolver()
    relation_resolver = RelationResolver()
    hypergraph_resolver = HyperGraphResolver()
    org_resolver = OrganizationResolver()
    
    # Forward declare types to resolve circular dependencies
    entity_type_thunk = None
    relation_type_thunk = None
    
    # Define Entity type with deferred relation field resolution
    entity_type = GraphQLObjectType(
        'Entity',
        lambda: {
            'id': GraphQLField(GraphQLNonNull(GraphQLID)),
            'name': GraphQLField(GraphQLNonNull(GraphQLString)),
            'type': GraphQLField(GraphQLNonNull(GraphQLString)),
            'attributes': GraphQLField(GraphQLJSON),
            'metadata': GraphQLField(GraphQLJSON),
            'orgContext': GraphQLField(GraphQLString),
            'createdAt': GraphQLField(GraphQLString),
            'updatedAt': GraphQLField(GraphQLString),
            'relations': GraphQLField(GraphQLList(GraphQLNonNull(relation_type))),
        }
    )
    
    # Define Relation type with deferred entity field resolution
    relation_type = GraphQLObjectType(
        'Relation',
        lambda: {
            'id': GraphQLField(GraphQLNonNull(GraphQLID)),
            'sourceId': GraphQLField(GraphQLNonNull(GraphQLID)),
            'targetId': GraphQLField(GraphQLNonNull(GraphQLID)),
            'relationType': GraphQLField(GraphQLNonNull(GraphQLString)),
            'weight': GraphQLField(GraphQLNonNull(GraphQLFloat)),
            'properties': GraphQLField(GraphQLJSON),
            'orgContext': GraphQLField(GraphQLString),
            'createdAt': GraphQLField(GraphQLString),
            'source': GraphQLField(entity_type),
            'target': GraphQLField(entity_type),
        }
    )
    
    # Define HyperGraph type
    hypergraph_type = GraphQLObjectType(
        'HyperGraph',
        lambda: {
            'id': GraphQLField(GraphQLNonNull(GraphQLID)),
            'name': GraphQLField(GraphQLNonNull(GraphQLString)),
            'entities': GraphQLField(GraphQLNonNull(GraphQLList(GraphQLNonNull(entity_type)))),
            'relations': GraphQLField(GraphQLNonNull(GraphQLList(GraphQLNonNull(relation_type)))),
            'metadata': GraphQLField(GraphQLJSON),
            'orgContext': GraphQLField(GraphQLString),
        }
    )
    
    # Define Organization type  
    organization_type = GraphQLObjectType(
        'Organization',
        lambda: {
            'id': GraphQLField(GraphQLNonNull(GraphQLID)),
            'name': GraphQLField(GraphQLNonNull(GraphQLString)),
            'type': GraphQLField(GraphQLNonNull(GraphQLString)),
            'hypergraphs': GraphQLField(GraphQLNonNull(GraphQLList(GraphQLNonNull(hypergraph_type)))),
            'metadata': GraphQLField(GraphQLJSON),
            'parentOrgId': GraphQLField(GraphQLString),
            'githubRepo': GraphQLField(GraphQLString),
            'childOrganizations': GraphQLField(GraphQLList(GraphQLNonNull(organization_type))),
        }
    )
    
    # Define Query type
    query_type = GraphQLObjectType(
        'Query',
        {
            'entity': GraphQLField(
                entity_type,
                args={'id': GraphQLArgument(GraphQLNonNull(GraphQLID))},
                resolve=entity_resolver.resolve_entity
            ),
            'entities': GraphQLField(
                GraphQLNonNull(GraphQLList(GraphQLNonNull(entity_type))),
                args={
                    'type': GraphQLArgument(GraphQLString),
                    'orgContext': GraphQLArgument(GraphQLString),
                    'limit': GraphQLArgument(GraphQLInt),
                    'offset': GraphQLArgument(GraphQLInt),
                },
                resolve=entity_resolver.resolve_entities
            ),
            'relation': GraphQLField(
                relation_type,
                args={'id': GraphQLArgument(GraphQLNonNull(GraphQLID))},
                resolve=relation_resolver.resolve_relation
            ),
            'relations': GraphQLField(
                GraphQLNonNull(GraphQLList(GraphQLNonNull(relation_type))),
                args={
                    'type': GraphQLArgument(GraphQLString),
                    'sourceId': GraphQLArgument(GraphQLID),
                    'targetId': GraphQLArgument(GraphQLID),
                    'orgContext': GraphQLArgument(GraphQLString),
                },
                resolve=relation_resolver.resolve_relations
            ),
            'hypergraph': GraphQLField(
                hypergraph_type,
                args={'id': GraphQLArgument(GraphQLNonNull(GraphQLID))},
                resolve=hypergraph_resolver.resolve_hypergraph
            ),
            'hypergraphs': GraphQLField(
                GraphQLNonNull(GraphQLList(GraphQLNonNull(hypergraph_type))),
                args={'orgContext': GraphQLArgument(GraphQLString)},
                resolve=hypergraph_resolver.resolve_hypergraphs
            ),
            'organization': GraphQLField(
                organization_type,
                args={'id': GraphQLArgument(GraphQLNonNull(GraphQLID))},
                resolve=org_resolver.resolve_organization
            ),
            'organizations': GraphQLField(
                GraphQLNonNull(GraphQLList(GraphQLNonNull(organization_type))),
                args={
                    'type': GraphQLArgument(GraphQLString),
                    'parentOrgId': GraphQLArgument(GraphQLString),
                },
                resolve=org_resolver.resolve_organizations
            ),
            'navigateHypergraph': GraphQLField(
                hypergraph_type,
                args={
                    'startEntityId': GraphQLArgument(GraphQLNonNull(GraphQLID)),
                    'maxDepth': GraphQLArgument(GraphQLInt),
                    'relationType': GraphQLArgument(GraphQLString),
                },
                resolve=hypergraph_resolver.resolve_navigate_hypergraph
            ),
        }
    )
    
    # Define Mutation type
    mutation_type = GraphQLObjectType(
        'Mutation',
        {
            'createEntity': GraphQLField(
                GraphQLNonNull(entity_type),
                args={
                    'name': GraphQLArgument(GraphQLNonNull(GraphQLString)),
                    'type': GraphQLArgument(GraphQLNonNull(GraphQLString)),
                    'attributes': GraphQLArgument(GraphQLJSON),
                    'orgContext': GraphQLArgument(GraphQLString),
                },
                resolve=entity_resolver.resolve_create_entity
            ),
            'updateEntity': GraphQLField(
                entity_type,
                args={
                    'id': GraphQLArgument(GraphQLNonNull(GraphQLID)),
                    'name': GraphQLArgument(GraphQLString),
                    'attributes': GraphQLArgument(GraphQLJSON),
                },
                resolve=entity_resolver.resolve_update_entity
            ),
            'deleteEntity': GraphQLField(
                GraphQLNonNull(GraphQLBoolean),
                args={'id': GraphQLArgument(GraphQLNonNull(GraphQLID))},
                resolve=entity_resolver.resolve_delete_entity
            ),
            'createRelation': GraphQLField(
                GraphQLNonNull(relation_type),
                args={
                    'sourceId': GraphQLArgument(GraphQLNonNull(GraphQLID)),
                    'targetId': GraphQLArgument(GraphQLNonNull(GraphQLID)),
                    'relationType': GraphQLArgument(GraphQLNonNull(GraphQLString)),
                    'weight': GraphQLArgument(GraphQLFloat),
                    'properties': GraphQLArgument(GraphQLJSON),
                    'orgContext': GraphQLArgument(GraphQLString),
                },
                resolve=relation_resolver.resolve_create_relation
            ),
            'deleteRelation': GraphQLField(
                GraphQLNonNull(GraphQLBoolean),
                args={'id': GraphQLArgument(GraphQLNonNull(GraphQLID))},
                resolve=relation_resolver.resolve_delete_relation
            ),
            'createHyperGraph': GraphQLField(
                GraphQLNonNull(hypergraph_type),
                args={
                    'name': GraphQLArgument(GraphQLNonNull(GraphQLString)),
                    'orgContext': GraphQLArgument(GraphQLString),
                    'metadata': GraphQLArgument(GraphQLJSON),
                },
                resolve=hypergraph_resolver.resolve_create_hypergraph
            ),
            'createOrganization': GraphQLField(
                GraphQLNonNull(organization_type),
                args={
                    'name': GraphQLArgument(GraphQLNonNull(GraphQLString)),
                    'type': GraphQLArgument(GraphQLNonNull(GraphQLString)),
                    'parentOrgId': GraphQLArgument(GraphQLString),
                    'githubRepo': GraphQLArgument(GraphQLString),
                },
                resolve=org_resolver.resolve_create_organization
            ),
            'syncFromGitHub': GraphQLField(
                organization_type,
                args={
                    'orgId': GraphQLArgument(GraphQLNonNull(GraphQLID)),
                    'repoPath': GraphQLArgument(GraphQLNonNull(GraphQLString)),
                },
                resolve=org_resolver.resolve_sync_from_github
            ),
            'syncToGitHub': GraphQLField(
                GraphQLNonNull(GraphQLBoolean),
                args={'orgId': GraphQLArgument(GraphQLNonNull(GraphQLID))},
                resolve=org_resolver.resolve_sync_to_github
            ),
        }
    )
    
    return GraphQLSchema(query=query_type, mutation=mutation_type)
