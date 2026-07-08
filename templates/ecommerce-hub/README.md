# E-commerce Hub Template

A complete example integrating Shopify, Stripe, and QuickBooks for e-commerce operations.

## Features

- **Customer Sync**: Synchronize customers across all platforms
- **Order to Invoice**: Automatically create QuickBooks invoices from Shopify orders
- **Payment Reconciliation**: Match Stripe payments with QuickBooks records
- **Inventory Sync**: Keep product data consistent across platforms

## Quick Start

```bash
# Copy this template
cp -r /home/ubuntu/skills/multiplatform-api-weaver/templates/ecommerce-hub ./my-integration

# Install dependencies
cd my-integration
pip install -e .

# Configure credentials
cp .env.example .env
# Edit .env with your API keys

# Validate configuration
python -m scripts.validate ./config

# Run CLI
weaver customer:list --format table
```

## Configuration Files

### config/platforms.yaml

Pre-configured for Shopify, Stripe, and QuickBooks with:
- Authentication settings
- Rate limiting
- Pagination handling

### config/mappings.yaml

Field mappings for:
- Customer entity
- Order/Invoice entity
- Product/Item entity

### config/commands.yaml

Unified commands:
- `customer:create` - Create customer on all platforms
- `customer:sync` - Sync customer between platforms
- `order:sync` - Create QuickBooks invoice from Shopify order
- `payment:reconcile` - Match Stripe payments with invoices

## Directory Structure

```
ecommerce-hub/
├── config/
│   ├── platforms.yaml
│   ├── mappings.yaml
│   └── commands.yaml
├── src/
│   ├── adapters/
│   │   ├── base.py
│   │   ├── shopify.py
│   │   ├── stripe.py
│   │   └── quickbooks.py
│   ├── transformers/
│   │   ├── order_to_invoice.py
│   │   └── customer_sync.py
│   ├── client.py
│   └── cli.py
├── tests/
│   ├── unit/
│   └── integration/
├── .env.example
├── pyproject.toml
└── README.md
```

## Workflow Examples

### Sync New Shopify Order to QuickBooks

```bash
# When a new order comes in from Shopify
weaver order:sync --order-id "5123456789" --direction shopify_to_qb

# This will:
# 1. Fetch the order from Shopify
# 2. Check if customer exists in QuickBooks (create if not)
# 3. Map order line items to QuickBooks invoice lines
# 4. Create the invoice in QuickBooks
# 5. Update the Shopify order with the QB invoice number
```

### Create Customer Across All Platforms

```bash
weaver customer:create \
  --email "customer@example.com" \
  --name "John Doe" \
  --phone "+1-555-0123"

# This will create the customer in:
# - Shopify (for order management)
# - Stripe (for payment processing)
# - QuickBooks (for accounting)
# All with linked IDs stored in metadata
```

### Reconcile Stripe Payments

```bash
weaver payment:reconcile --date "2024-01-15"

# This will:
# 1. Fetch all Stripe payments for the date
# 2. Match with QuickBooks invoices by amount and customer
# 3. Create payment records in QuickBooks
# 4. Report any unmatched payments
```

## Environment Variables

```bash
# Shopify
SHOPIFY_STORE=your-store
SHOPIFY_ACCESS_TOKEN=shpat_xxx

# Stripe
STRIPE_SECRET_KEY=sk_live_xxx

# QuickBooks
QUICKBOOKS_REALM_ID=123456789
QUICKBOOKS_ACCESS_TOKEN=xxx
QUICKBOOKS_REFRESH_TOKEN=xxx
QUICKBOOKS_CLIENT_ID=xxx
QUICKBOOKS_CLIENT_SECRET=xxx
```

## Testing

```bash
# Run unit tests
pytest tests/unit/

# Run integration tests (requires credentials)
pytest tests/integration/ --env-file .env

# Test specific adapter
pytest tests/unit/test_shopify_adapter.py -v
```

## Extending

To add a new platform:

1. Add configuration to `config/platforms.yaml`
2. Create adapter in `src/adapters/`
3. Add field mappings to `config/mappings.yaml`
4. Update commands in `config/commands.yaml`

See the [multiplatform-api-weaver documentation](/home/ubuntu/skills/multiplatform-api-weaver/SKILL.md) for detailed guidance.
