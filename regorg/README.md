# regorg

RegimA's professional organizational development and evidence-based Zone Concept advancement repository focused on clinical skincare excellence.

## Professional Excellence Evolution

The repository tracks professional development and cycle completion insights through two configuration files representing RegimA's commitment to evidence-based skincare and Zone Concept mastery:

### cycleCompletion.json
Contains professional development cycle completion insights and progress tracking:
- **Zone Concept Framework Integration**: Complete 3-sphere approach with Anti-inflammatory, Anti-oxidants, and Rejuvenation
- **Professional Education Excellence**: Comprehensive understanding of evidence-based skincare principles
- **Product Portfolio Mastery**: Beta-Endorphin Stimulator, UV filters, Matrixyl 3000 peptides, Power Peels AHA systems
- **Educational Leadership**: Training programs for Zone Concept application and professional protocols
- **Research & Development Focus**: Clinically-effective ingredient concentrations from validated trials
- **Industry Recognition**: Leadership in Zone methodology and clinical-grade formulations

### regcyc.json
Contains comprehensive organizational development and learning cycle tracking with professional insights:
- **Professional Excellence**: Advanced Zone Concept integration with evidence-based education
- **Zone Framework Mastery**: 3-sphere system addressing inflammation and free radical damage
- **Professional Guidance**: Focus areas including Zone application, education, and client outcomes
- **Industry Innovation Scanning**: Analysis of skincare technologies and evidence-based advancements
- **Integration Strategy**: Professional development actions and educational program planning

## Structure

- `cycleCompletion.json` - Professional development cycle completion insights and progress tracking
- `regcyc.json` - Comprehensive organizational development and Zone Concept implementation tracking
- `.github/workflows/regima-learning-cycle.yml` - GitHub Actions workflow for AI-powered professional analysis
- `scripts/regima_ai_processor.py` - Python script for generating evidence-based AI analysis and insights
- `config/ai_models.json` - AI model configurations for professional analysis capabilities
- `outputs/` - Directory for generated professional AI analysis reports
- `api/` - HyperGraphQL API for org-aware repository management with HyperGNN mapping (NEW)

## HyperGraphQL API

A comprehensive GraphQL API for managing hypergraph structures with GitHub repository integration, providing:

- **GraphQL Schema**: Type-safe entity, relation, and hypergraph definitions mapped to HyperGNN structures
- **Org-Aware Queries**: Organization-level filtering and multi-level scaling (repo → org → enterprise)
- **GitHub Integration**: Bi-directional sync between GraphQL data and repository folder structures
- **Hypergraph Navigation**: Traverse entity relationships with depth limits and type filtering
- **Scaling Utilities**: Compression and expansion algorithms for different organizational levels

### Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Start the API server
python -m api.server

# Access GraphQL endpoint at http://localhost:8080/graphql
# Full documentation in api/README.md
```

### Example Usage

```python
from api.client import HyperGraphQLClient

client = HyperGraphQLClient()

# Create professional development entities
entity = client.create_entity(
    name="Zone Concept Framework",
    entity_type="professional_knowledge",
    attributes={"level": "advanced"}
)

# Navigate hypergraph
nav = client.navigate_hypergraph(
    start_entity_id=entity['id'],
    max_depth=3
)
```

See `api/README.md` for complete documentation.

## AI-Powered Learning Cycle Analysis

This repository includes automated AI analysis capabilities that process organizational development data and Zone Concept framework to generate evidence-based insights and professional recommendations.

### GitHub Actions Workflow

The `regima-learning-cycle.yml` workflow automatically:

- **Triggers**: Runs on pushes to main (when JSON files change), pull requests, weekly schedule, or manual dispatch
- **Processes**: Analyzes professional development data and Zone Concept framework implementation
- **Generates**: Evidence-based AI-powered insights, strategic recommendations, and professional guidance
- **Outputs**: Creates detailed analysis reports and automatically opens GitHub issues with findings
- **Artifacts**: Stores generated reports for download and review

### Analysis Types

The workflow supports multiple analysis modes:

- **Full Analysis**: Comprehensive analysis of all organizational development aspects including Zone Concept, professional education, and guidance
- **Zone Concept Only**: Focused analysis of the Zone Concept framework covering Anti-inflammatory, Anti-oxidants, and Rejuvenation spheres
- **Professional Development Only**: Analysis of organizational learning and professional excellence evolution
- **Guidance Only**: Professional guidance analysis with enhancement recommendations

### Manual Execution

Run the AI processor locally:

```bash
# Full analysis (default)
python scripts/regima_ai_processor.py

# Specific analysis type
ANALYSIS_TYPE=zone_concept_only python scripts/regima_ai_processor.py
```

### Generated Outputs

The AI analysis generates:

- Individual analysis reports (Markdown format) for Zone Concept, professional development, and guidance
- Comprehensive JSON data for programmatic access with detailed analytics
- Summary insights for strategic professional development review
- Automated GitHub issues with findings and strategic recommendations