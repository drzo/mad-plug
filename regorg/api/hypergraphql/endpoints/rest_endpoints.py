"""
REST Endpoints

Provides REST API endpoints for GitHub sync and organization management.
"""

from typing import Dict, Any, Optional, List
import json

from ..github_integration import GitHubIntegration, HyperGraphScaler
from ..resolvers.storage import get_storage
from ..schema.types import OrganizationType, HyperGraphType


class RESTEndpoints:
    """REST API endpoint handlers."""
    
    def __init__(self):
        self.storage = get_storage()
        self.github_integration = GitHubIntegration()
        self.scaler = HyperGraphScaler()
    
    # Organization Management
    
    def get_organization(self, org_id: str) -> Optional[Dict[str, Any]]:
        """
        GET /api/organizations/{org_id}
        
        Get organization details.
        """
        org = self.storage.get_organization(org_id)
        if org:
            return {
                'success': True,
                'data': org.to_dict()
            }
        return {
            'success': False,
            'error': 'Organization not found'
        }
    
    def list_organizations(
        self,
        org_type: Optional[str] = None,
        parent_org_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        GET /api/organizations
        
        List organizations with optional filtering.
        """
        orgs = self.storage.get_organizations(
            org_type=org_type,
            parent_org_id=parent_org_id
        )
        return {
            'success': True,
            'data': [org.to_dict() for org in orgs],
            'count': len(orgs)
        }
    
    def create_organization(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/organizations
        
        Create a new organization.
        
        Request body:
        {
            "name": "Organization Name",
            "type": "repo|org|enterprise",
            "parentOrgId": "optional_parent_id",
            "githubRepo": "optional/repo/path"
        }
        """
        import uuid
        
        name = data.get('name')
        org_type = data.get('type', 'repo')
        
        if not name:
            return {
                'success': False,
                'error': 'Name is required'
            }
        
        org = OrganizationType(
            id=str(uuid.uuid4()),
            name=name,
            type=org_type,
            parent_org_id=data.get('parentOrgId'),
            github_repo=data.get('githubRepo')
        )
        
        self.storage.add_organization(org)
        
        return {
            'success': True,
            'data': org.to_dict()
        }
    
    # GitHub Sync Endpoints
    
    def sync_from_github(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/github/sync/from
        
        Sync hypergraph data from GitHub repository.
        
        Request body:
        {
            "orgId": "organization_id",
            "repoPath": "/path/to/repo"
        }
        """
        org_id = data.get('orgId')
        repo_path = data.get('repoPath')
        
        if not org_id or not repo_path:
            return {
                'success': False,
                'error': 'orgId and repoPath are required'
            }
        
        org = self.storage.get_organization(org_id)
        if not org:
            return {
                'success': False,
                'error': 'Organization not found'
            }
        
        try:
            self.github_integration.sync_from_github(org, repo_path)
            return {
                'success': True,
                'message': f'Successfully synced from {repo_path}',
                'data': org.to_dict()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Sync failed: {str(e)}'
            }
    
    def sync_to_github(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/github/sync/to
        
        Sync hypergraph data to GitHub repository.
        
        Request body:
        {
            "orgId": "organization_id"
        }
        """
        org_id = data.get('orgId')
        
        if not org_id:
            return {
                'success': False,
                'error': 'orgId is required'
            }
        
        org = self.storage.get_organization(org_id)
        if not org:
            return {
                'success': False,
                'error': 'Organization not found'
            }
        
        if not org.github_repo:
            return {
                'success': False,
                'error': 'Organization does not have a GitHub repository configured'
            }
        
        try:
            success = self.github_integration.sync_to_github(org)
            if success:
                return {
                    'success': True,
                    'message': f'Successfully synced to {org.github_repo}'
                }
            else:
                return {
                    'success': False,
                    'error': 'Sync failed'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Sync failed: {str(e)}'
            }
    
    def create_repo_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/github/init
        
        Initialize repository structure for hypergraph data.
        
        Request body:
        {
            "repoPath": "/path/to/repo"
        }
        """
        repo_path = data.get('repoPath')
        
        if not repo_path:
            return {
                'success': False,
                'error': 'repoPath is required'
            }
        
        try:
            self.github_integration.create_repo_structure(repo_path)
            return {
                'success': True,
                'message': f'Repository structure created at {repo_path}'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create structure: {str(e)}'
            }
    
    # Scaling Endpoints
    
    def compress_hypergraph(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/hypergraph/compress
        
        Compress a hypergraph for storage optimization.
        
        Request body:
        {
            "hypergraphId": "hypergraph_id",
            "strategy": "type_aggregation|cluster"
        }
        """
        hypergraph_id = data.get('hypergraphId')
        strategy = data.get('strategy', 'type_aggregation')
        
        if not hypergraph_id:
            return {
                'success': False,
                'error': 'hypergraphId is required'
            }
        
        hypergraph = self.storage.get_hypergraph(hypergraph_id)
        if not hypergraph:
            return {
                'success': False,
                'error': 'Hypergraph not found'
            }
        
        try:
            compressed = self.scaler.compress_hypergraph(hypergraph, strategy)
            self.storage.add_hypergraph(compressed)
            
            return {
                'success': True,
                'data': compressed.to_dict(),
                'compression_ratio': {
                    'entities': f"{len(hypergraph.entities)} -> {len(compressed.entities)}",
                    'relations': f"{len(hypergraph.relations)} -> {len(compressed.relations)}"
                }
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Compression failed: {str(e)}'
            }
    
    def expand_to_org_level(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        POST /api/hypergraph/expand/org
        
        Expand multiple repo hypergraphs to organization level.
        
        Request body:
        {
            "hypergraphIds": ["id1", "id2", ...],
            "orgName": "Organization Name"
        }
        """
        hypergraph_ids = data.get('hypergraphIds', [])
        org_name = data.get('orgName')
        
        if not hypergraph_ids or not org_name:
            return {
                'success': False,
                'error': 'hypergraphIds and orgName are required'
            }
        
        hypergraphs = []
        for hg_id in hypergraph_ids:
            hg = self.storage.get_hypergraph(hg_id)
            if hg:
                hypergraphs.append(hg)
        
        if not hypergraphs:
            return {
                'success': False,
                'error': 'No valid hypergraphs found'
            }
        
        try:
            org = self.scaler.expand_to_org_level(hypergraphs, org_name)
            self.storage.add_organization(org)
            
            return {
                'success': True,
                'data': org.to_dict()
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Expansion failed: {str(e)}'
            }
