# cog253 — Universal Pattern Language Template

A topological skeleton for organizing cognitive capabilities across domains.
Based on Christopher Alexander's *A Pattern Language* (253 patterns) and the
UIA *Patterns & Metaphors* (253 patterns), with 102 archetypal cross-domain templates.

## Entry Points

| What you need | Where to go |
|---------------|-------------|
| **Find a skill by name or domain** | [../SKILL.md](../SKILL.md) — unified skill lattice |
| **Read a specific APL pattern** | [markdown/apl/](markdown/apl/) — `apl001.md`–`apl253.md` |
| **Read a UIA organizational pattern** | [markdown/uia/](markdown/uia/) — by numeric ID |
| **Cross-domain archetypal templates** | [markdown/arc/](markdown/arc/) — 102 generic patterns |
| **System architecture** | [docs/architecture_overview.md](docs/architecture_overview.md) |
| **JSON schemas & data** | [schemas/](schemas/) |
| **Python scripts** | [scripts/](scripts/) |
| **Generated analysis docs** | [generated/](generated/) |
| **OpenCog Atomese** | [opencog_atomese/](opencog_atomese/) |

## Structure

```
cog253-main/
├── README.md              ← you are here
├── CLAUDE.md              ← project conventions for AI agents
├── markdown/
│   ├── apl/               253 APL patterns (apl001–apl253.md)
│   ├── uia/               253 UIA patterns (by numeric ID)
│   ├── arc/               102 archetypal cross-domain patterns
│   └── apl_arc/           APL-archetypal fusion docs
├── docs/                  Architecture, Z++ formal specs
├── schemas/               JSON data & schema files
├── scripts/               Python generators, validators, analyzers
├── generated/             Summary & analysis reports
├── assets/                Images (diagrams, visualizations)
├── opencog_atomese/       Scheme knowledge representation
├── apl/                   Original HTML source (APL)
├── uia/                   Original HTML source (UIA)
├── pattern/               Individual pattern directories
└── .github/agents/        Agent/persona definitions
```

## Pattern Topology

Three scales, one hierarchy:

| Category | Patterns | Scale | Skill Mapping |
|----------|----------|-------|---------------|
| **Towns** | 1–94 | Ecosystem / System | Orchestration, meta-design, platforms |
| **Buildings** | 95–204 | Component / Module | Architectures, frameworks, applications |
| **Construction** | 205–253 | Implementation / Material | Nodes, specs, formulations |

## Domain Dimensions

Archetypal patterns transform across 4+2 dimensions:

- `dim0` Archetypal — the abstract template
- `dim2` Physical — spatial, material, architectural
- `dim3` Social — organizational, community, institutional
- `dim4` Conceptual — knowledge, theoretical, paradigmatic
- `dim5` Interpersonal — relational, communicative
- Psychic — awareness, consciousness, mental

## Quick Commands

```bash
cd scripts/
python3 generate_pattern_schema.py       # Regenerate APL schema
python3 generate_archetypal_schema.py    # Regenerate archetypal schema
python3 validate_schema.py              # Validate all schemas
python3 test_archetypal_schema.py       # Run archetypal tests
```

## Related

- **[../SKILL.md](../SKILL.md)** — 53 skills organized by this pattern topology
- **[generated/FORMAL_SPECIFICATION_SUMMARY.md](generated/FORMAL_SPECIFICATION_SUMMARY.md)** — Z++ formal specs
- **[opencog_atomese/README.md](opencog_atomese/README.md)** — Atomese knowledge graph