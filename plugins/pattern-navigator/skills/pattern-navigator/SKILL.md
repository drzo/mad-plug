---
name: pattern-navigator
description: >
  Navigate and query the GH253 pattern topology — Christopher Alexander's 253 patterns
  mapped to GitHub/software domains. Discover pattern relationships, look up domain
  mappings, and traverse the enterprise/organisation/repository hierarchy.
tools:
  - scripts/query_patterns.py
  - scripts/query_patterns_1.py
  - scripts/transform_patterns.py
  - scripts/build_relationships.py
resources:
  - gh253_domain_mappings.json
  - patterns/
---

# Pattern Navigator Plugin

Provides tools for navigating the COG253 pattern topology — a mapping of Christopher
Alexander's 253 architectural patterns onto the GitHub/software development domain.

## Capabilities

- **Query patterns** by number, name, category, or keyword
- **Traverse** the hierarchy: Enterprises (Towns) → Organisations (Buildings) → Repositories (Construction)
- **Map** between APL (A Pattern Language) and GH (GitHub) domain terminology
- **Build relationships** between patterns to discover connected design decisions
- **Transform** pattern concepts across domain boundaries

## Usage

Invoke when the user asks about:
- Pattern discovery ("what pattern covers X?")
- Architecture navigation ("show me enterprise-level patterns")
- Domain mapping ("what's the GitHub equivalent of Pattern 153?")
- Relationship exploration ("which patterns connect to Protected Branches?")

## Related Resources

- `gh253_domain_mappings.json` — Full 253-pattern domain mapping table
- `patterns/` — Pattern definitions organized by category and dimension
