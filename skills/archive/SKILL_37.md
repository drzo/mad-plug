---
name: regimorg
description: RegimA skincare expertise with Zone Concept framework. Use for skincare consultations, product recommendations based on skin concerns, generating training materials for professionals, creating educational content about evidence-based skincare, and applying the 3-sphere approach (Anti-inflammatory, Anti-oxidants, Rejuvenation).
---

# RegimA Organization Skill

Evidence-based skincare expertise using RegimA's Zone Concept framework for professional consultations, product recommendations, and training material generation.

## Core Concept: The Zone

RegimA's Zone Concept addresses skin health through three interconnected spheres:

| Sphere | Focus | Primary Concern Addressed |
|--------|-------|---------------------------|
| **Anti-inflammatory** | Reduce inflammation as the "silent killer" of skin | Redness, sensitivity, premature aging |
| **Anti-oxidants** | Combat free radical damage from UV and environment | Sun damage, oxidative stress, pigmentation |
| **Rejuvenation** | Promote cellular renewal and repair | Fine lines, texture, loss of firmness |

The goal is to bring skin "into the Zone" by addressing all three spheres simultaneously.

## Workflows

### 1. Skincare Consultation

Assess client needs and provide Zone-based recommendations:

1. **Identify primary concerns** → Map to Zone sphere(s)
2. **Assess skin type and sensitivity** → Determine product strength
3. **Apply Zone Concept** → Ensure all 3 spheres are addressed
4. **Select products** → See `references/products.md`
5. **Create protocol** → See `references/protocols.md`

**Consultation output template:**

```markdown
## Skin Assessment
- Primary concerns: [list]
- Skin type: [dry/oily/combination/sensitive]
- Zone focus: [primary sphere]

## Recommended Protocol
### Morning Routine
[products with application order]

### Evening Routine
[products with application order]

### Weekly Treatments
[professional treatments if applicable]

## Zone Concept Rationale
- Anti-inflammatory: [how addressed]
- Anti-oxidants: [how addressed]
- Rejuvenation: [how addressed]
```

### 2. Product Recommendation

Match skin concerns to appropriate products:

**Concern → Zone → Product mapping:**
- Redness/sensitivity → Anti-inflammatory → Beta-Endorphin Stimulator products
- Sun damage/pigmentation → Anti-oxidants → UV protection with Uvinul A Plus, Tinosorb S
- Fine lines/texture → Rejuvenation → Matrixyl 3000, Power Peels

For detailed product information, read `references/products.md`.

### 3. Training Material Generation

Create educational content for skincare professionals:

1. **Select topic** from Zone Concept areas
2. **Read relevant reference** for technical details
3. **Structure content** with evidence-based approach
4. **Include practical applications**

**Training content types:**
- **Zone Concept fundamentals** → Read `references/zone-concept.md`
- **Product knowledge** → Read `references/products.md`
- **Treatment protocols** → Read `references/protocols.md`
- **Educational frameworks** → Read `references/training.md`

## Key Ingredients Quick Reference

| Ingredient | Zone Sphere | Key Benefit |
|------------|-------------|-------------|
| Beta-Endorphin Stimulator | Anti-inflammatory | Wellbeing + anti-inflammatory action |
| Bisabolol | Anti-inflammatory | Powerful skin soothing |
| Centella Asiatica | Anti-inflammatory | Healing + collagen synthesis |
| Uvinul A Plus | Anti-oxidants | 95% free radical reduction |
| Tinosorb S | Anti-oxidants | Photostable broad-spectrum UV |
| Matrixyl 3000 | Rejuvenation | Activates extracellular matrix renewal |
| Power Peels (AHA) | Rejuvenation | Controlled exfoliation |
| Centelastin | Rejuvenation | Elastin + anti-glycation |

## Reference Files

Load these as needed based on the task:

- **`references/zone-concept.md`** - Deep dive into the 3-sphere framework, scientific basis, and integration principles
- **`references/products.md`** - Complete product portfolio with ingredients, concentrations, and indications
- **`references/protocols.md`** - Treatment protocols for home care and professional procedures
- **`references/training.md`** - Educational program structures and training material templates

## Evidence-Based Principles

When creating content or recommendations, always emphasize:

1. **Clinically effective concentrations** - Ingredients at levels proven in trials
2. **Scientific mechanism of action** - Explain how products work
3. **Holistic approach** - Address all Zone spheres, not just symptoms
4. **Professional standards** - Clinical-grade formulations

## API Integration

The skill includes a HyperGraphQL API for programmatic access to organizational knowledge:

```bash
# Start API server
cd /home/ubuntu/skills/regimorg/regorg
python -m api.server
# Access at http://localhost:8080/graphql
```

See `regorg/api/README.md` for full API documentation.
