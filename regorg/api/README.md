# HyperGraphQL API

A comprehensive GraphQL API for managing hypergraph structures with GitHub repository integration, organization-aware data management, and multi-level scaling capabilities.

## Overview

The HyperGraphQL API provides:

- **GraphQL Schema**: Type-safe entity, relation, and hypergraph definitions
- **Resolvers**: Query and mutation resolvers with org-aware filtering
- **GitHub Integration**: Bi-directional sync between GraphQL storage and GitHub repositories
- **Scaling Utilities**: Compression and expansion for different organizational levels
- **REST Endpoints**: Additional endpoints for GitHub sync and organization management

## Architecture

```
api/
├── hypergraphql/
│   ├── schema/              # GraphQL type definitions
│   │   ├── types.py         # Entity, Relation, HyperGraph, Organization types
│   │   └── builder.py       # Schema builder
│   ├── resolvers/           # GraphQL resolvers
│   │   ├── entity_resolvers.py
│   │   ├── relation_resolvers.py
│   │   ├── hypergraph_resolvers.py
│   │   ├── organization_resolvers.py
│   │   └── storage.py       # In-memory storage
│   ├── github_integration/  # GitHub repository integration
│   │   ├── file_mapper.py   # Maps entities/relations to files
│   │   ├── scaler.py        # Compression & expansion utilities
│   │   └── sync.py          # Sync operations
│   └── endpoints/           # HTTP endpoints
│       ├── graphql_endpoint.py
│       └── rest_endpoints.py
├── server.py                # HTTP server
├── client.py                # Python client
└── tests/                   # Test suite
```

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. The API requires:
   - `graphql-core>=3.2.0` for GraphQL functionality
   - `requests>=2.31.0` for HTTP client

## Usage

### Starting the Server

```bash
# Start server on default port (8080)
python -m api.server

# Start on custom port
python -m api.server 3000
```

The server will expose:
- GraphQL endpoint: `http://localhost:8080/graphql`
- REST endpoints: `http://localhost:8080/api/*`
- Health check: `http://localhost:8080/health`

### Using the Python Client

```python
from api.client import HyperGraphQLClient

# Initialize client
client = HyperGraphQLClient("http://localhost:8080")

# Create an organization
org = client.create_organization(
    name="RegimA Main",
    org_type="repo",
    github_repo="/path/to/repo"
)

# Create entities
entity = client.create_entity(
    name="Quantum Consciousness",
    entity_type="consciousness",
    attributes={
        "level": "quantum",
        "capabilities": ["molecular_precision", "predictive_intelligence"]
    },
    org_context=org['data']['id']
)

# Create relations
relation = client.create_relation(
    source_id=entity1_id,
    target_id=entity2_id,
    relation_type="evolution",
    weight=0.9
)

# Navigate hypergraph
nav_result = client.navigate_hypergraph(
    start_entity_id=entity_id,
    max_depth=3,
    relation_type="evolution"
)

# Sync with GitHub
client.sync_to_github(org_id)
```

## GraphQL Schema

### Core Types

#### Entity
```graphql
type Entity {
  id: ID!
  name: String!
  type: String!
  attributes: JSON
  metadata: JSON
  orgContext: String
  createdAt: String
  updatedAt: String
  relations: [Relation!]
}
```

#### Relation
```graphql
type Relation {
  id: ID!
  sourceId: ID!
  targetId: ID!
  relationType: String!
  weight: Float!
  properties: JSON
  orgContext: String
  createdAt: String
  source: Entity
  target: Entity
}
```

#### HyperGraph
```graphql
type HyperGraph {
  id: ID!
  name: String!
  entities: [Entity!]!
  relations: [Relation!]!
  metadata: JSON
  orgContext: String
}
```

#### Organization
```graphql
type Organization {
  id: ID!
  name: String!
  type: String!  # repo, org, enterprise
  hypergraphs: [HyperGraph!]!
  metadata: JSON
  parentOrgId: String
  githubRepo: String
  childOrganizations: [Organization!]
}
```

### Queries

```graphql
query {
  # Get single entity
  entity(id: "entity_id") {
    id
    name
    type
    attributes
  }
  
  # List entities with filters
  entities(type: "consciousness", orgContext: "org1", limit: 10) {
    id
    name
    relations {
      id
      relationType
    }
  }
  
  # Navigate hypergraph
  navigateHypergraph(
    startEntityId: "start_id",
    maxDepth: 3,
    relationType: "evolution"
  ) {
    entities {
      id
      name
    }
    relations {
      sourceId
      targetId
    }
  }
  
  # Get organization
  organization(id: "org_id") {
    name
    hypergraphs {
      id
      name
    }
    childOrganizations {
      id
      name
    }
  }
}
```

### Mutations

```graphql
mutation {
  # Create entity
  createEntity(
    name: "Quantum System",
    type: "consciousness",
    attributes: {level: "quantum"},
    orgContext: "org1"
  ) {
    id
    name
  }
  
  # Create relation
  createRelation(
    sourceId: "e1",
    targetId: "e2",
    relationType: "evolution",
    weight: 0.9
  ) {
    id
    sourceId
    targetId
  }
  
  # Sync from GitHub
  syncFromGitHub(orgId: "org1", repoPath: "/path/to/repo") {
    id
    hypergraphs {
      entities {
        id
        name
      }
    }
  }
  
  # Sync to GitHub
  syncToGitHub(orgId: "org1")
}
```

## REST API Endpoints

### Organization Management

#### Create Organization
```
POST /api/organizations
Content-Type: application/json

{
  "name": "Organization Name",
  "type": "repo|org|enterprise",
  "parentOrgId": "optional_parent_id",
  "githubRepo": "optional/repo/path"
}
```

#### List Organizations
```
GET /api/organizations?type=repo&parentOrgId=parent_id
```

#### Get Organization
```
GET /api/organizations/{org_id}
```

### GitHub Sync

#### Sync from GitHub
```
POST /api/github/sync/from
Content-Type: application/json

{
  "orgId": "organization_id",
  "repoPath": "/path/to/repo"
}
```

#### Sync to GitHub
```
POST /api/github/sync/to
Content-Type: application/json

{
  "orgId": "organization_id"
}
```

#### Initialize Repository Structure
```
POST /api/github/init
Content-Type: application/json

{
  "repoPath": "/path/to/repo"
}
```

### Scaling Operations

#### Compress HyperGraph
```
POST /api/hypergraph/compress
Content-Type: application/json

{
  "hypergraphId": "hypergraph_id",
  "strategy": "type_aggregation|cluster"
}
```

#### Expand to Organization Level
```
POST /api/hypergraph/expand/org
Content-Type: application/json

{
  "hypergraphIds": ["hg1", "hg2"],
  "orgName": "Organization Name"
}
```

## GitHub Repository Structure

The API maps hypergraph data to GitHub repository folders:

```
repo/
├── entities/                # Entity data
│   ├── consciousness/       # Grouped by type
│   │   ├── entity1.json
│   │   └── entity2.json
│   └── zone_concepts/
│       └── entity3.json
├── relations/              # Relation data
│   ├── evolution/          # Grouped by type
│   │   └── relation1.json
│   └── integration/
│       └── relation2.json
├── metadata.json           # Hypergraph metadata
└── README.md              # Auto-generated documentation
```

### Entity File Format
```json
{
  "id": "entity_id",
  "name": "Entity Name",
  "type": "consciousness",
  "attributes": {
    "level": "quantum",
    "capabilities": ["molecular_precision"]
  },
  "metadata": {},
  "orgContext": "org1",
  "createdAt": "2025-10-11T00:00:00Z",
  "updatedAt": "2025-10-11T00:00:00Z"
}
```

### Relation File Format
```json
{
  "id": "relation_id",
  "sourceId": "entity1_id",
  "targetId": "entity2_id",
  "relationType": "evolution",
  "weight": 0.9,
  "properties": {
    "strength": "strong"
  },
  "orgContext": "org1",
  "createdAt": "2025-10-11T00:00:00Z"
}
```

## Scaling Strategies

### Compression

Compress hypergraphs for storage optimization:

**Type Aggregation**: Groups entities by type
- Reduces entity count by aggregating similar entities
- Maintains relation counts between types
- Useful for high-level overviews

**Cluster Analysis**: Groups by connectivity
- Identifies connected components
- Creates cluster entities
- Useful for understanding graph structure

### Expansion

Expand data across organizational levels:

**Repo Level**: Individual repository hypergraphs
- Single project or component
- Fine-grained entity and relation data

**Org Level**: Organization-wide aggregation
- Combines multiple repo hypergraphs
- Provides organization-level view
- Tracks cross-repo relationships

**Enterprise Level**: Multi-organization scaling
- Aggregates multiple organizations
- Enterprise-wide perspective
- Hierarchical organization structure

## Testing

Run the test suite:

```bash
# Run all tests
python -m unittest discover api/tests

# Run specific test modules
python -m unittest api.tests.test_schema
python -m unittest api.tests.test_resolvers
python -m unittest api.tests.test_github_integration
python -m unittest api.tests.test_endpoints
```

## Examples

### Example 1: Creating a Consciousness Hierarchy

```python
client = HyperGraphQLClient()

# Create consciousness entities
quantum = client.create_entity(
    name="Quantum Consciousness",
    entity_type="consciousness",
    attributes={"level": "quantum"}
)

transcendent = client.create_entity(
    name="Transcendent Consciousness",
    entity_type="consciousness",
    attributes={"level": "transcendent"}
)

# Create evolution relation
client.create_relation(
    source_id=quantum['id'],
    target_id=transcendent['id'],
    relation_type="evolution",
    weight=1.0
)

# Navigate from quantum consciousness
nav = client.navigate_hypergraph(
    start_entity_id=quantum['id'],
    max_depth=2
)
```

### Example 2: Syncing with GitHub

```python
# Create organization with GitHub repo
org = client.create_organization(
    name="RegimA",
    org_type="repo",
    github_repo="/home/runner/work/regorg/regorg"
)

# Sync data from GitHub repository
result = client.sync_from_github(
    org_id=org['data']['id'],
    repo_path="/home/runner/work/regorg/regorg"
)

# Make changes via GraphQL...

# Sync back to GitHub
client.sync_to_github(org_id=org['data']['id'])
```

### Example 3: Multi-level Organization

```python
# Create repo-level organizations
repo1_org = client.create_organization(name="Repo 1", org_type="repo")
repo2_org = client.create_organization(name="Repo 2", org_type="repo")

# Expand to org level
result = requests.post(
    "http://localhost:8080/api/hypergraph/expand/org",
    json={
        "hypergraphIds": [hg1_id, hg2_id],
        "orgName": "Main Organization"
    }
)
```

## Integration with RegimA

The HyperGraphQL API integrates with RegimA's organizational consciousness and Zone Concept frameworks:

- **Consciousness Entities**: Map organizational consciousness states to entities
- **Zone Concepts**: Represent as entities with specialized attributes
- **Evolution Relations**: Track consciousness evolution and zone integration
- **Hypergraph Navigation**: Explore consciousness development paths
- **GitHub Sync**: Persist and version hypergraph data in repositories

## Future Enhancements

- [ ] Add authentication and authorization
- [ ] Implement real database backend (PostgreSQL, Neo4j)
- [ ] Add GraphQL subscriptions for real-time updates
- [ ] Enhance scaling algorithms for large graphs
- [ ] Add graph analytics and visualization endpoints
- [ ] Implement batch operations
- [ ] Add caching layer
- [ ] Support multiple storage backends

## Contributing

When contributing to the HyperGraphQL API:

1. Follow existing code structure and patterns
2. Add tests for new features
3. Update documentation
4. Ensure all tests pass
5. Follow Python best practices (PEP 8)

## License

See LICENSE file in the repository root.
