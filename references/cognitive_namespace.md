# Cognitive Namespace Reference

The cognitive namespace is the function-creator transform of Total Commander (tc) file management into the Inferno-OS 9P namespace for cognitive kernel services.

## Transform Mapping: tc → Cognitive 9P

| TC Concept | Cognitive 9P Equivalent |
|-----------|------------------------|
| File system tree | `/cognitive/` namespace hierarchy |
| Directory | Cognitive service group |
| File | Individual atom, rule, or configuration |
| File properties | Atom metadata (type, STI, LTI, truth value) |
| Search (wildcard) | Pattern matching across namespaces |
| Copy/Move | Atom migration between partitions |
| Archive pack | Namespace snapshot to persistent storage |
| Archive unpack | Namespace restore from snapshot |
| Batch rename | Bulk atom type conversion |

## Namespace Hierarchy

```
/cognitive/
├── atomspace/
│   ├── atoms/          # ConceptNode, PredicateNode, LinkType instances
│   ├── types/          # Type hierarchy (inherits-from relations)
│   └── indices/        # Hash indices, type indices for fast lookup
├── inference/
│   ├── rules/          # PLN rules (ModusPonens, DeductionRule, etc.)
│   ├── queue/          # Pending inference tasks
│   └── results/        # Cached inference results with truth values
├── attention/
│   ├── bank/           # STI/LTI values per atom
│   └── agents/         # HebbianUpdating, ImportanceSpreading agents
├── learning/
│   ├── populations/    # MOSES candidate program populations
│   └── fitness/        # Fitness function configurations
├── temporal/
│   ├── levels/         # 9 time crystal hierarchy level configs
│   └── phases/         # Current phase state per level
└── autognosis/
    ├── images/         # Hierarchical self-images (Level 0, 1, 2+)
    ├── insights/       # Meta-cognitive insight records
    └── metrics/        # Self-monitoring metric time series
```

## 9P Protocol Operations

Each namespace path is accessible via 9P/Styx protocol:

| 9P Operation | Cognitive Meaning |
|-------------|-------------------|
| `open` | Acquire handle to cognitive resource |
| `read` | Query atom value, rule definition, or metric |
| `write` | Update atom truth value, submit inference task |
| `create` | Create new atom, rule, or agent |
| `remove` | Delete atom or deactivate agent |
| `stat` | Get atom metadata (type, STI, LTI, creation time) |
| `walk` | Navigate namespace hierarchy |

## CLI Operations (tc-style)

```bash
# Tree: display cognitive namespace
cognitive_devkernel.py transform

# Search: find atoms by pattern
# (uses CognitiveFileSystem.search internally)
python cognitive_devkernel.py promise .  # validates namespace exists

# Validate: check all namespace paths are configured
python cognitive_devkernel.py validate .
```

## Temporal Binding

Each namespace path is bound to a temporal level from the time-crystal-nn hierarchy:

| Namespace | Temporal Level | Update Period |
|-----------|---------------|---------------|
| `/cognitive/atomspace/` | L0-L1 | 8-26ms |
| `/cognitive/inference/` | L2 | 52ms |
| `/cognitive/attention/` | L3 | 110ms |
| `/cognitive/learning/` | L4 | 160ms |
| `/cognitive/temporal/` | L5-L6 | 250-330ms |
| `/cognitive/autognosis/` | L7-L8 | 500-1000ms |

Fast-changing data (atoms, patterns) updates at millisecond scales. Slow-changing data (self-images, insights) updates at second scales. This mirrors the biological time crystal hierarchy from Nanobrain.
