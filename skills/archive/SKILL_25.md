---
name: multiplatform-api-weaver
description: Guide for integrating multiple platform APIs into unified CLI-like hybrid applications and SDKs. Use when building apps that orchestrate multiple services (Shopify, Stripe, QuickBooks, Slack, GitHub, etc.), creating SDKs that abstract platform differences, implementing advanced command combinations across APIs, or designing unified interfaces for heterogeneous backend systems.
---

# Multiplatform API Weaver

Build unified interfaces that weave multiple platform APIs into coherent CLI-like hybrid applications. This skill enables orchestration of heterogeneous services into a single, consistent developer experience.

## Core Concepts

**API Weaving** combines multiple platform APIs into unified operations. A single command like `order:sync` might coordinate Shopify orders, Stripe payments, and QuickBooks invoices simultaneously.

**Unified CLI Hybrid** presents a consistent command interface regardless of underlying platform. Users interact with logical operations (`customer:create`, `invoice:send`) rather than platform-specific endpoints.

**Platform Adapters** normalize each platform's quirks (auth, pagination, rate limits, data formats) behind a common interface.

## Workflow

### Phase 1: Analyze Integration Requirements

Identify platforms and map data flows:

```bash
python /home/ubuntu/skills/multiplatform-api-weaver/scripts/init_integration.py <project-name>
```

This creates the integration scaffold with `config/platforms.yaml` for platform definitions, `config/mappings.yaml` for data field mappings, `config/commands.yaml` for unified command definitions, and `src/adapters/` for platform adapter stubs.

### Phase 2: Configure Platforms

Edit `config/platforms.yaml` to define each platform:

```yaml
platforms:
  shopify:
    type: rest
    base_url: "https://{store}.myshopify.com/admin/api/2024-01"
    auth:
      type: oauth2
      token_env: SHOPIFY_ACCESS_TOKEN
    rate_limit:
      requests: 40
      period: 1s
      
  stripe:
    type: rest
    base_url: "https://api.stripe.com/v1"
    auth:
      type: api_key
      key_env: STRIPE_SECRET_KEY
      header: "Authorization: Bearer {key}"
```

For platform-specific patterns, see [platforms reference](references/platforms/).

### Phase 3: Define Data Mappings

Map fields between platforms in `config/mappings.yaml`:

```yaml
entities:
  customer:
    canonical_fields: [id, email, name, phone, created_at]
    platform_mappings:
      shopify:
        id: customer.id
        email: customer.email
        name: "customer.first_name + ' ' + customer.last_name"
      stripe:
        id: customer.id
        email: customer.email
        name: customer.name
      quickbooks:
        id: Customer.Id
        email: Customer.PrimaryEmailAddr.Address
        name: Customer.DisplayName
```

### Phase 4: Define Unified Commands

Create command definitions in `config/commands.yaml`:

```yaml
commands:
  customer:create:
    description: "Create customer across all platforms"
    args:
      - name: email
        required: true
      - name: name
        required: true
    orchestration:
      type: parallel
      platforms: [shopify, stripe, quickbooks]
      rollback: true
      
  order:sync:
    description: "Sync order data between platforms"
    orchestration:
      type: sequential
      steps:
        - fetch: shopify.orders.get
        - transform: order_to_invoice
        - create: quickbooks.invoices.create
```

### Phase 5: Generate Unified Client

Generate the unified client code:

```bash
python /home/ubuntu/skills/multiplatform-api-weaver/scripts/generate_client.py \
  --config ./config --output ./src --language typescript
```

### Phase 6: Build CLI Interface

The generated CLI provides consistent commands:

```bash
weaver customer:create --email "user@example.com" --name "John Doe"
weaver order:sync --order-id "ORD-123" --direction shopify_to_qb
weaver customer:list --format table --limit 50
```

## Advanced Patterns

For complex multi-platform workflows, consult these references:

| Pattern | Reference | Use Case |
|---------|-----------|----------|
| Orchestration | [orchestration-patterns.md](references/orchestration-patterns.md) | Sequential, parallel, saga, event-driven workflows |
| Authentication | [auth-strategies.md](references/auth-strategies.md) | OAuth, API keys, multi-tenant credentials |
| Error Handling | [error-handling.md](references/error-handling.md) | Retries, circuit breakers, compensation |
| CLI Design | [cli-design.md](references/cli-design.md) | Command naming, output formatting, config |

## Validation

Validate your integration configuration:

```bash
python /home/ubuntu/skills/multiplatform-api-weaver/scripts/validate_integration.py ./config
```

## Quick Reference

| Script | Purpose |
|--------|---------|
| `init_integration.py <name>` | Scaffold new integration project |
| `generate_client.py --config <dir>` | Generate unified client from config |
| `validate_integration.py <config>` | Validate configuration files |
