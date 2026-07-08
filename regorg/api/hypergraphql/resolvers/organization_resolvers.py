"""
Organization Resolvers

Implements GraphQL resolvers for organization queries and mutations.
"""

from typing import Dict, List, Any, Optional
import uuid

from ..schema.types import OrganizationType
from .storage import get_storage


class OrganizationResolver:
    """Resolver for organization-related GraphQL operations."""
    
    def __init__(self):
        self.storage = get_storage()
    
    def resolve_organization(self, obj, info, id: str) -> Optional[Dict[str, Any]]:
        """Resolve a single organization by ID."""
        org = self.storage.get_organization(id)
        if org:
            result = org.to_dict()
            # Add child organizations resolver
            result['childOrganizations'] = lambda: self._get_child_organizations(id)
            return result
        return None
    
    def resolve_organizations(
        self,
        obj,
        info,
        type: Optional[str] = None,
        parentOrgId: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Resolve multiple organizations with filtering."""
        orgs = self.storage.get_organizations(
            org_type=type,
            parent_org_id=parentOrgId
        )
        results = []
        for org in orgs:
            result = org.to_dict()
            result['childOrganizations'] = lambda oid=org.id: self._get_child_organizations(oid)
            results.append(result)
        return results
    
    def _get_child_organizations(self, org_id: str) -> List[Dict[str, Any]]:
        """Get child organizations for a parent org."""
        children = self.storage.get_organizations(parent_org_id=org_id)
        return [c.to_dict() for c in children]
    
    def resolve_create_organization(
        self,
        obj,
        info,
        name: str,
        type: str,
        parentOrgId: Optional[str] = None,
        githubRepo: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new organization."""
        org = OrganizationType(
            id=str(uuid.uuid4()),
            name=name,
            type=type,
            parent_org_id=parentOrgId,
            github_repo=githubRepo
        )
        
        self.storage.add_organization(org)
        result = org.to_dict()
        result['childOrganizations'] = lambda: self._get_child_organizations(org.id)
        return result
    
    def resolve_sync_from_github(
        self,
        info,
        orgId: str,
        repoPath: str
    ) -> Optional[Dict[str, Any]]:
        """
        Sync hypergraph data from GitHub repository.
        
        This will be implemented in the GitHub integration module.
        """
        from ..github_integration import GitHubIntegration
        
        github = GitHubIntegration()
        org = self.storage.get_organization(orgId)
        
        if not org:
            return None
        
        # Sync entities and relations from GitHub
        github.sync_from_github(org, repoPath)
        
        return org.to_dict()
    
    def resolve_sync_to_github(
        self,
        info,
        orgId: str
    ) -> bool:
        """
        Sync hypergraph data to GitHub repository.
        
        This will be implemented in the GitHub integration module.
        """
        from ..github_integration import GitHubIntegration
        
        github = GitHubIntegration()
        org = self.storage.get_organization(orgId)
        
        if not org:
            return False
        
        # Sync entities and relations to GitHub
        return github.sync_to_github(org)
