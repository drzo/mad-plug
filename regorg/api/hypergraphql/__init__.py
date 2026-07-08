"""
HyperGraphQL API implementation for RegimA.

Provides GraphQL interface for hypergraph navigation, entity/relation queries,
and GitHub repository integration.
"""

from .schema import build_schema
from .resolvers import get_root_resolver
from .github_integration import GitHubIntegration

__all__ = ['build_schema', 'get_root_resolver', 'GitHubIntegration']
