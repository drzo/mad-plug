# pattern-navigator

Navigate and query the GH253 pattern topology — 253 Christopher Alexander patterns mapped to GitHub/software domains, with relationship traversal and cross-domain mapping.

**Version:** 0.1.0 | **Category:** Pattern Recognition & Navigation | **Tags:** `pattern` `topology` `navigation` `graph`

---

## Description

`pattern-navigator` exposes the COG253 Unified Skill Lattice as queryable tools. The 253 patterns from Alexander's *A Pattern Language* are mapped to GitHub concepts (enterprises, organisations, repositories) and indexed for navigation by ID, keyword, and graph relationships. Use it to discover which patterns govern a design decision and how they connect.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `pattern_query` | Query by ID, search term, or graph relationship | `command` |
| `pattern_transform` | Map an APL pattern to its GitHub domain equivalent | `pattern_id` |
| `pattern_relationships` | Explore the broader/narrower relationship graph | `pattern_id` |

### `pattern_query` commands

| Command | Example | Description |
|---|---|---|
| `get` | `get 107` | Retrieve a single pattern by ID |
| `search` | `search api` | Full-text search across all patterns |
| `broader` | `broader 107` | Find parent (broader) patterns |
| `narrower` | `narrower 107` | Find child (narrower) patterns |
| `roots` | `roots` | List all root patterns |
| `hubs` | `hubs` | List most-connected hub patterns |
| `path` | `path 1 253` | Find path between two patterns |

---

## Usage Examples

### Get a pattern by ID
```
pattern_query(command="get", args="107")
```
Returns details for pattern 107 (MODULAR DESIGN) including description, connections, and GitHub mapping.

### Search for patterns about contributor onboarding
```
pattern_query(command="search", args="contributor")
```
Returns all patterns matching "contributor" with relevance scores.

### Explore the relationship graph for a pattern
```
pattern_relationships(pattern_id="107", depth="2")
```
Returns the 2-hop broader/narrower graph around pattern 107.

### Transform an APL pattern to GitHub domain
```
pattern_transform(pattern_id="95", target_domain="github")
```
Maps APL pattern 95 (BUILDING COMPLEX) to its GitHub equivalent (REPOSITORY COMPLEX).

---

## Dependencies

None

---

## Scripts

Backend Python scripts in `scripts/`:
- `query_patterns.py` — pattern lookup and search
- `transform_patterns.py` — APL→GitHub domain mapping
- `build_relationships.py` — relationship graph traversal
