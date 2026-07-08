"""
HyperGraph Scaler

Provides utilities for scaling hypergraph data up (expansion) or down (compression)
for different organizational levels (repo -> org -> enterprise).
"""

from typing import List, Dict, Any, Set
from ..schema.types import EntityType, RelationType, HyperGraphType, OrganizationType


class HyperGraphScaler:
    """Utilities for scaling hypergraph data between organizational levels."""
    
    @staticmethod
    def compress_hypergraph(
        hypergraph: HyperGraphType,
        compression_strategy: str = 'type_aggregation'
    ) -> HyperGraphType:
        """
        Compress a hypergraph by aggregating entities and relations.
        
        Useful for storage optimization or creating summary views.
        
        Args:
            hypergraph: The hypergraph to compress
            compression_strategy: Strategy for compression
                - 'type_aggregation': Group entities by type
                - 'cluster': Group by connectivity
        
        Returns:
            Compressed hypergraph
        """
        if compression_strategy == 'type_aggregation':
            return HyperGraphScaler._compress_by_type(hypergraph)
        elif compression_strategy == 'cluster':
            return HyperGraphScaler._compress_by_cluster(hypergraph)
        else:
            return hypergraph
    
    @staticmethod
    def _compress_by_type(hypergraph: HyperGraphType) -> HyperGraphType:
        """Compress hypergraph by aggregating entities of the same type."""
        compressed = HyperGraphType(
            id=f"{hypergraph.id}_compressed",
            name=f"{hypergraph.name} (Compressed)",
            org_context=hypergraph.org_context,
            metadata={
                **hypergraph.metadata,
                'compression': 'type_aggregation',
                'original_entity_count': len(hypergraph.entities),
                'original_relation_count': len(hypergraph.relations)
            }
        )
        
        # Group entities by type
        type_groups: Dict[str, List[EntityType]] = {}
        for entity in hypergraph.entities:
            if entity.type not in type_groups:
                type_groups[entity.type] = []
            type_groups[entity.type].append(entity)
        
        # Create aggregate entities
        entity_mapping: Dict[str, str] = {}  # old_id -> new_id
        
        for entity_type, entities in type_groups.items():
            aggregate_entity = EntityType(
                id=f"agg_{entity_type}",
                name=f"{entity_type} (Aggregated)",
                type=entity_type,
                attributes={
                    'count': len(entities),
                    'entity_ids': [e.id for e in entities]
                },
                org_context=hypergraph.org_context
            )
            compressed.add_entity(aggregate_entity)
            
            for entity in entities:
                entity_mapping[entity.id] = aggregate_entity.id
        
        # Compress relations between aggregated entities
        relation_counts: Dict[tuple, int] = {}
        
        for relation in hypergraph.relations:
            new_source = entity_mapping.get(relation.source_id)
            new_target = entity_mapping.get(relation.target_id)
            
            if new_source and new_target:
                key = (new_source, new_target, relation.relation_type)
                relation_counts[key] = relation_counts.get(key, 0) + 1
        
        # Create compressed relations
        for (source_id, target_id, rel_type), count in relation_counts.items():
            compressed_relation = RelationType(
                id=f"rel_{source_id}_{target_id}_{rel_type}",
                source_id=source_id,
                target_id=target_id,
                relation_type=rel_type,
                weight=count,
                properties={'original_count': count},
                org_context=hypergraph.org_context
            )
            compressed.add_relation(compressed_relation)
        
        return compressed
    
    @staticmethod
    def _compress_by_cluster(hypergraph: HyperGraphType) -> HyperGraphType:
        """Compress hypergraph by clustering connected entities."""
        # Simple connected component clustering
        compressed = HyperGraphType(
            id=f"{hypergraph.id}_clustered",
            name=f"{hypergraph.name} (Clustered)",
            org_context=hypergraph.org_context,
            metadata={
                **hypergraph.metadata,
                'compression': 'cluster'
            }
        )
        
        # Find connected components
        visited: Set[str] = set()
        clusters: List[Set[str]] = []
        
        def dfs(entity_id: str, cluster: Set[str]):
            if entity_id in visited:
                return
            visited.add(entity_id)
            cluster.add(entity_id)
            
            for relation in hypergraph.relations:
                if relation.source_id == entity_id:
                    dfs(relation.target_id, cluster)
                elif relation.target_id == entity_id:
                    dfs(relation.source_id, cluster)
        
        for entity in hypergraph.entities:
            if entity.id not in visited:
                cluster: Set[str] = set()
                dfs(entity.id, cluster)
                clusters.append(cluster)
        
        # Create cluster entities
        for i, cluster in enumerate(clusters):
            cluster_entity = EntityType(
                id=f"cluster_{i}",
                name=f"Cluster {i}",
                type="cluster",
                attributes={
                    'size': len(cluster),
                    'entity_ids': list(cluster)
                },
                org_context=hypergraph.org_context
            )
            compressed.add_entity(cluster_entity)
        
        return compressed
    
    @staticmethod
    def expand_to_org_level(
        repo_hypergraphs: List[HyperGraphType],
        org_name: str
    ) -> OrganizationType:
        """
        Expand multiple repository hypergraphs to organization level.
        
        Args:
            repo_hypergraphs: List of hypergraphs from different repos
            org_name: Name of the organization
        
        Returns:
            Organization containing all hypergraphs
        """
        org = OrganizationType(
            id=f"org_{org_name.lower().replace(' ', '_')}",
            name=org_name,
            type='org',
            metadata={
                'repo_count': len(repo_hypergraphs),
                'total_entities': sum(len(h.entities) for h in repo_hypergraphs),
                'total_relations': sum(len(h.relations) for h in repo_hypergraphs)
            }
        )
        
        for hypergraph in repo_hypergraphs:
            org.add_hypergraph(hypergraph)
        
        return org
    
    @staticmethod
    def expand_to_enterprise_level(
        orgs: List[OrganizationType],
        enterprise_name: str
    ) -> OrganizationType:
        """
        Expand multiple organizations to enterprise level.
        
        Args:
            orgs: List of organizations
            enterprise_name: Name of the enterprise
        
        Returns:
            Enterprise-level organization
        """
        enterprise = OrganizationType(
            id=f"ent_{enterprise_name.lower().replace(' ', '_')}",
            name=enterprise_name,
            type='enterprise',
            metadata={
                'org_count': len(orgs),
                'total_repos': sum(len(o.hypergraphs) for o in orgs)
            }
        )
        
        # Set parent relationships
        for org in orgs:
            org.parent_org_id = enterprise.id
        
        return enterprise
