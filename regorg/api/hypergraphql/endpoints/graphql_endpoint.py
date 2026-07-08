"""
GraphQL Endpoint

Provides HTTP endpoint for executing HyperGraphQL queries.
"""

from typing import Dict, Any, Optional
import json
from graphql import graphql_sync

from ..schema import build_schema
from ..resolvers import get_root_resolver


class GraphQLEndpoint:
    """HTTP endpoint handler for GraphQL queries."""
    
    def __init__(self):
        self.schema = build_schema()
        self.root_resolver = get_root_resolver()
    
    def execute_query(
        self,
        query: str,
        variables: Optional[Dict[str, Any]] = None,
        operation_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Execute a GraphQL query.
        
        Args:
            query: GraphQL query string
            variables: Optional query variables
            operation_name: Optional operation name
        
        Returns:
            Query result as dictionary
        """
        result = graphql_sync(
            self.schema,
            query,
            variable_values=variables,
            operation_name=operation_name
        )
        
        response = {}
        
        if result.data:
            response['data'] = result.data
        
        if result.errors:
            response['errors'] = [
                {
                    'message': str(error.message),
                    'locations': [
                        {'line': loc.line, 'column': loc.column}
                        for loc in (error.locations or [])
                    ]
                }
                for error in result.errors
            ]
        
        return response
    
    def handle_http_request(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Handle HTTP POST request with GraphQL query.
        
        Expected request format:
        {
            "query": "query string",
            "variables": {...},
            "operationName": "..."
        }
        
        Args:
            request_data: Parsed JSON request body
        
        Returns:
            GraphQL response
        """
        query = request_data.get('query')
        variables = request_data.get('variables')
        operation_name = request_data.get('operationName')
        
        if not query:
            return {
                'errors': [{
                    'message': 'Query is required'
                }]
            }
        
        return self.execute_query(query, variables, operation_name)
    
    def get_introspection_query(self) -> str:
        """
        Get GraphQL introspection query for schema exploration.
        
        Returns:
            Introspection query string
        """
        return """
        query IntrospectionQuery {
          __schema {
            queryType { name }
            mutationType { name }
            types {
              name
              kind
              description
              fields {
                name
                description
                args {
                  name
                  type {
                    name
                    kind
                  }
                }
                type {
                  name
                  kind
                }
              }
            }
          }
        }
        """
