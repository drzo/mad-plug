"""
HyperGraphQL API Client

Python client for interacting with the HyperGraphQL API.
"""

import json
from typing import Dict, Any, Optional, List
import requests


class HyperGraphQLClient:
    """Client for HyperGraphQL API."""
    
    def __init__(self, base_url: str = "http://localhost:8080"):
        """
        Initialize the client.
        
        Args:
            base_url: Base URL of the API server
        """
        self.base_url = base_url.rstrip('/')
        self.graphql_url = f"{self.base_url}/graphql"
    
    # GraphQL Methods
    
    def query(
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
            Query result
        """
        payload = {
            'query': query,
            'variables': variables,
            'operationName': operation_name
        }
        
        response = requests.post(self.graphql_url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def get_entity(self, entity_id: str) -> Optional[Dict[str, Any]]:
        """Get a single entity by ID."""
        query = """
        query GetEntity($id: ID!) {
          entity(id: $id) {
            id
            name
            type
            attributes
            metadata
            orgContext
            createdAt
            updatedAt
          }
        }
        """
        result = self.query(query, variables={'id': entity_id})
        return result.get('data', {}).get('entity')
    
    def list_entities(
        self,
        entity_type: Optional[str] = None,
        org_context: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """List entities with optional filtering."""
        query = """
        query ListEntities($type: String, $orgContext: String, $limit: Int) {
          entities(type: $type, orgContext: $orgContext, limit: $limit) {
            id
            name
            type
            attributes
            orgContext
          }
        }
        """
        result = self.query(query, variables={
            'type': entity_type,
            'orgContext': org_context,
            'limit': limit
        })
        return result.get('data', {}).get('entities', [])
    
    def create_entity(
        self,
        name: str,
        entity_type: str,
        attributes: Optional[Dict[str, Any]] = None,
        org_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new entity."""
        query = """
        mutation CreateEntity($name: String!, $type: String!, $attributes: JSON, $orgContext: String) {
          createEntity(name: $name, type: $type, attributes: $attributes, orgContext: $orgContext) {
            id
            name
            type
            attributes
            orgContext
          }
        }
        """
        result = self.query(query, variables={
            'name': name,
            'type': entity_type,
            'attributes': attributes,
            'orgContext': org_context
        })
        return result.get('data', {}).get('createEntity', {})
    
    def create_relation(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        weight: float = 1.0,
        properties: Optional[Dict[str, Any]] = None,
        org_context: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new relation."""
        query = """
        mutation CreateRelation(
          $sourceId: ID!,
          $targetId: ID!,
          $relationType: String!,
          $weight: Float,
          $properties: JSON,
          $orgContext: String
        ) {
          createRelation(
            sourceId: $sourceId,
            targetId: $targetId,
            relationType: $relationType,
            weight: $weight,
            properties: $properties,
            orgContext: $orgContext
          ) {
            id
            sourceId
            targetId
            relationType
            weight
            properties
          }
        }
        """
        result = self.query(query, variables={
            'sourceId': source_id,
            'targetId': target_id,
            'relationType': relation_type,
            'weight': weight,
            'properties': properties,
            'orgContext': org_context
        })
        return result.get('data', {}).get('createRelation', {})
    
    def navigate_hypergraph(
        self,
        start_entity_id: str,
        max_depth: Optional[int] = None,
        relation_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """Navigate hypergraph from a starting entity."""
        query = """
        query NavigateHypergraph($startEntityId: ID!, $maxDepth: Int, $relationType: String) {
          navigateHypergraph(startEntityId: $startEntityId, maxDepth: $maxDepth, relationType: $relationType) {
            id
            name
            entities {
              id
              name
              type
            }
            relations {
              id
              sourceId
              targetId
              relationType
            }
          }
        }
        """
        result = self.query(query, variables={
            'startEntityId': start_entity_id,
            'maxDepth': max_depth,
            'relationType': relation_type
        })
        return result.get('data', {}).get('navigateHypergraph', {})
    
    # REST Methods
    
    def create_organization(
        self,
        name: str,
        org_type: str = 'repo',
        parent_org_id: Optional[str] = None,
        github_repo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new organization."""
        url = f"{self.base_url}/api/organizations"
        payload = {
            'name': name,
            'type': org_type,
            'parentOrgId': parent_org_id,
            'githubRepo': github_repo
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def list_organizations(
        self,
        org_type: Optional[str] = None,
        parent_org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """List organizations."""
        url = f"{self.base_url}/api/organizations"
        params = {}
        if org_type:
            params['type'] = org_type
        if parent_org_id:
            params['parentOrgId'] = parent_org_id
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    
    def sync_from_github(self, org_id: str, repo_path: str) -> Dict[str, Any]:
        """Sync hypergraph data from GitHub repository."""
        url = f"{self.base_url}/api/github/sync/from"
        payload = {
            'orgId': org_id,
            'repoPath': repo_path
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def sync_to_github(self, org_id: str) -> Dict[str, Any]:
        """Sync hypergraph data to GitHub repository."""
        url = f"{self.base_url}/api/github/sync/to"
        payload = {
            'orgId': org_id
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()
    
    def compress_hypergraph(
        self,
        hypergraph_id: str,
        strategy: str = 'type_aggregation'
    ) -> Dict[str, Any]:
        """Compress a hypergraph."""
        url = f"{self.base_url}/api/hypergraph/compress"
        payload = {
            'hypergraphId': hypergraph_id,
            'strategy': strategy
        }
        response = requests.post(url, json=payload)
        response.raise_for_status()
        return response.json()


# Example usage
if __name__ == '__main__':
    # Initialize client
    client = HyperGraphQLClient()
    
    # Create an organization
    org_result = client.create_organization(
        name="RegimA Main",
        org_type="repo",
        github_repo="/home/runner/work/regorg/regorg"
    )
    print("Created organization:", json.dumps(org_result, indent=2))
    
    # Create entities
    entity1 = client.create_entity(
        name="Quantum Consciousness",
        entity_type="consciousness",
        attributes={
            "level": "quantum",
            "capabilities": ["molecular_precision", "predictive_intelligence"]
        },
        org_context=org_result['data']['id']
    )
    print("Created entity:", json.dumps(entity1, indent=2))
    
    # List entities
    entities = client.list_entities(entity_type="consciousness")
    print(f"Found {len(entities)} consciousness entities")
