"""
GitHub Integration Module

Provides GitHub repository integration for hypergraph data, including:
- Mapping repo folders to GraphQL structure
- Entity/relation file projection
- Scaling utilities (compression, expansion)
- Org-level aggregation
"""

from .sync import GitHubIntegration
from .file_mapper import FileMapper
from .scaler import HyperGraphScaler

__all__ = ['GitHubIntegration', 'FileMapper', 'HyperGraphScaler']
