"""
Tests for API Endpoints
"""

import unittest

from ..hypergraphql.endpoints.graphql_endpoint import GraphQLEndpoint
from ..hypergraphql.endpoints.rest_endpoints import RESTEndpoints
from ..hypergraphql.resolvers.storage import get_storage


class TestGraphQLEndpoint(unittest.TestCase):
    """Test GraphQL endpoint."""
    
    def setUp(self):
        """Set up endpoint."""
        self.endpoint = GraphQLEndpoint()
        self.storage = get_storage()
        # Clear storage
        self.storage.entities.clear()
        self.storage.relations.clear()
        self.storage.hypergraphs.clear()
        self.storage.organizations.clear()
    
    def test_execute_simple_query(self):
        """Test executing a simple query."""
        query = """
        mutation {
          createEntity(name: "Test", type: "consciousness") {
            id
            name
            type
          }
        }
        """
        
        result = self.endpoint.execute_query(query)
        
        self.assertIn('data', result)
        self.assertIn('createEntity', result['data'])
        self.assertEqual(result['data']['createEntity']['name'], "Test")
    
    def test_execute_query_with_variables(self):
        """Test query with variables."""
        query = """
        mutation CreateEntity($name: String!, $type: String!) {
          createEntity(name: $name, type: $type) {
            id
            name
            type
          }
        }
        """
        
        variables = {
            "name": "Variable Test",
            "type": "test"
        }
        
        result = self.endpoint.execute_query(query, variables)
        
        self.assertIn('data', result)
        self.assertEqual(
            result['data']['createEntity']['name'],
            "Variable Test"
        )
    
    def test_handle_http_request(self):
        """Test HTTP request handling."""
        request = {
            "query": """
            mutation {
              createEntity(name: "HTTP Test", type: "test") {
                id
                name
              }
            }
            """
        }
        
        result = self.endpoint.handle_http_request(request)
        
        self.assertIn('data', result)
        self.assertEqual(
            result['data']['createEntity']['name'],
            "HTTP Test"
        )
    
    def test_handle_invalid_request(self):
        """Test handling invalid request."""
        request = {}  # Missing query
        
        result = self.endpoint.handle_http_request(request)
        
        self.assertIn('errors', result)
        self.assertEqual(result['errors'][0]['message'], 'Query is required')


class TestRESTEndpoints(unittest.TestCase):
    """Test REST endpoints."""
    
    def setUp(self):
        """Set up endpoints."""
        self.endpoints = RESTEndpoints()
        self.storage = get_storage()
        # Clear storage
        self.storage.entities.clear()
        self.storage.relations.clear()
        self.storage.hypergraphs.clear()
        self.storage.organizations.clear()
    
    def test_create_organization(self):
        """Test organization creation."""
        data = {
            "name": "Test Org",
            "type": "repo",
            "githubRepo": "/test/repo"
        }
        
        result = self.endpoints.create_organization(data)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['name'], "Test Org")
        self.assertEqual(result['data']['type'], "repo")
    
    def test_list_organizations(self):
        """Test listing organizations."""
        # Create some organizations
        self.endpoints.create_organization({
            "name": "Org 1",
            "type": "repo"
        })
        self.endpoints.create_organization({
            "name": "Org 2",
            "type": "org"
        })
        
        result = self.endpoints.list_organizations()
        
        self.assertTrue(result['success'])
        self.assertEqual(result['count'], 2)
        
        # Filter by type
        result = self.endpoints.list_organizations(org_type="repo")
        self.assertEqual(result['count'], 1)
    
    def test_get_organization(self):
        """Test getting single organization."""
        # Create organization
        created = self.endpoints.create_organization({
            "name": "Get Test",
            "type": "repo"
        })
        org_id = created['data']['id']
        
        result = self.endpoints.get_organization(org_id)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['data']['name'], "Get Test")
    
    def test_get_nonexistent_organization(self):
        """Test getting non-existent organization."""
        result = self.endpoints.get_organization("nonexistent")
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)
    
    def test_create_organization_missing_name(self):
        """Test creating organization without name."""
        result = self.endpoints.create_organization({
            "type": "repo"
        })
        
        self.assertFalse(result['success'])
        self.assertIn('error', result)


if __name__ == '__main__':
    unittest.main()
