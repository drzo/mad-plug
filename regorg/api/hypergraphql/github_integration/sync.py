"""
GitHub Sync

Synchronizes hypergraph data between GraphQL storage and GitHub repositories.
"""

from typing import Optional
from pathlib import Path

from ..schema.types import OrganizationType, HyperGraphType
from ..resolvers.storage import get_storage
from .file_mapper import FileMapper


class GitHubIntegration:
    """Handles synchronization between hypergraph data and GitHub repositories."""
    
    def __init__(self):
        self.storage = get_storage()
    
    def sync_from_github(
        self,
        org: OrganizationType,
        repo_path: str
    ) -> None:
        """
        Sync hypergraph data from a GitHub repository to storage.
        
        Args:
            org: Organization to sync data into
            repo_path: Path to the repository directory
        """
        mapper = FileMapper(repo_path)
        
        # Load entities and relations from repo
        entities = mapper.load_entities_from_repo(org.id)
        relations = mapper.load_relations_from_repo(org.id)
        
        # Load metadata
        metadata = mapper.load_metadata()
        
        # Create or update hypergraph
        hypergraph_id = f"{org.id}_main"
        hypergraph = self.storage.get_hypergraph(hypergraph_id)
        
        if not hypergraph:
            hypergraph = HyperGraphType(
                id=hypergraph_id,
                name=f"{org.name} Main HyperGraph",
                org_context=org.id,
                metadata=metadata
            )
            self.storage.add_hypergraph(hypergraph)
        else:
            hypergraph.metadata.update(metadata)
        
        # Add entities to storage and hypergraph
        for entity in entities:
            self.storage.add_entity(entity)
            if entity not in hypergraph.entities:
                hypergraph.add_entity(entity)
        
        # Add relations to storage and hypergraph
        for relation in relations:
            self.storage.add_relation(relation)
            if relation not in hypergraph.relations:
                hypergraph.add_relation(relation)
        
        # Add hypergraph to organization if not already there
        if hypergraph not in org.hypergraphs:
            org.add_hypergraph(hypergraph)
    
    def sync_to_github(
        self,
        org: OrganizationType
    ) -> bool:
        """
        Sync hypergraph data from storage to GitHub repository.
        
        Args:
            org: Organization to sync data from
        
        Returns:
            True if sync was successful, False otherwise
        """
        if not org.github_repo:
            return False
        
        repo_path = org.github_repo
        mapper = FileMapper(repo_path)
        
        # Collect all entities and relations from org's hypergraphs
        all_entities = []
        all_relations = []
        
        for hypergraph in org.hypergraphs:
            all_entities.extend(hypergraph.entities)
            all_relations.extend(hypergraph.relations)
        
        # Save to repo
        try:
            mapper.save_entities_to_repo(all_entities)
            mapper.save_relations_to_repo(all_relations)
            
            # Save metadata
            metadata = {
                'organization': org.name,
                'org_id': org.id,
                'type': org.type,
                'hypergraph_count': len(org.hypergraphs),
                'entity_count': len(all_entities),
                'relation_count': len(all_relations)
            }
            mapper.save_metadata(metadata)
            
            return True
        except Exception as e:
            print(f"Error syncing to GitHub: {e}")
            return False
    
    def create_repo_structure(self, repo_path: str) -> None:
        """
        Create the standard repository structure for hypergraph data.
        
        Args:
            repo_path: Path where to create the structure
        """
        base_path = Path(repo_path)
        base_path.mkdir(parents=True, exist_ok=True)
        
        # Create entities and relations directories
        (base_path / "entities").mkdir(exist_ok=True)
        (base_path / "relations").mkdir(exist_ok=True)
        
        # Create README
        readme_path = base_path / "README.md"
        if not readme_path.exists():
            readme_content = """# HyperGraph Repository

This repository contains hypergraph data structured for HyperGraphQL API.

## Structure

- `entities/` - Entity data organized by type
- `relations/` - Relation data organized by type
- `metadata.json` - Metadata about the hypergraph

## Entity Structure

Entities are stored as JSON files in type-specific directories:
```
entities/
  <entity_type>/
    <entity_id>.json
```

## Relation Structure

Relations are stored as JSON files in type-specific directories:
```
relations/
  <relation_type>/
    <relation_id>.json
```
"""
            with open(readme_path, 'w') as f:
                f.write(readme_content)
