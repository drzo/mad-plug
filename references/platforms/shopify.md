# Shopify Integration Patterns

## Authentication

Shopify uses OAuth 2.0 with offline access tokens:

```yaml
auth:
  type: oauth2
  token_env: SHOPIFY_ACCESS_TOKEN
  # Offline tokens don't expire but can be revoked
```

**Required scopes for common operations:**
- `read_customers`, `write_customers` - Customer management
- `read_orders`, `write_orders` - Order management
- `read_products`, `write_products` - Product management
- `read_inventory`, `write_inventory` - Inventory management

## Rate Limiting

Shopify uses a leaky bucket algorithm:

```typescript
const SHOPIFY_RATE_LIMIT = {
  bucketSize: 40,        // Max requests in bucket
  leakRate: 2,           // Requests per second
  retryAfterHeader: 'Retry-After',
};

// Check remaining capacity from response headers
function getRemainingCapacity(response: Response): number {
  const limit = response.headers.get('X-Shopify-Shop-Api-Call-Limit');
  if (limit) {
    const [used, max] = limit.split('/').map(Number);
    return max - used;
  }
  return SHOPIFY_RATE_LIMIT.bucketSize;
}
```

## Pagination

Shopify uses cursor-based pagination with Link headers:

```typescript
async function* paginateShopify<T>(
  endpoint: string,
  params: Record<string, string> = {}
): AsyncGenerator<T[]> {
  let url = `${baseUrl}${endpoint}?${new URLSearchParams({ ...params, limit: '250' })}`;
  
  while (url) {
    const response = await fetch(url, { headers: getAuthHeaders() });
    const data = await response.json();
    
    yield Object.values(data)[0] as T[];
    
    // Parse Link header for next page
    const linkHeader = response.headers.get('Link');
    url = parseLinkHeader(linkHeader)?.next || '';
  }
}

function parseLinkHeader(header: string | null): { next?: string; previous?: string } | null {
  if (!header) return null;
  
  const links: Record<string, string> = {};
  header.split(',').forEach(part => {
    const match = part.match(/<([^>]+)>;\s*rel="([^"]+)"/);
    if (match) {
      links[match[2]] = match[1];
    }
  });
  
  return links;
}
```

## Common Entity Mappings

### Customer

```yaml
shopify_customer:
  id: customer.id
  email: customer.email
  first_name: customer.first_name
  last_name: customer.last_name
  phone: customer.phone
  created_at: customer.created_at
  updated_at: customer.updated_at
  orders_count: customer.orders_count
  total_spent: customer.total_spent
  tags: customer.tags
  addresses: customer.addresses
  default_address: customer.default_address
  metafields: customer.metafields
```

### Order

```yaml
shopify_order:
  id: order.id
  order_number: order.order_number
  email: order.email
  created_at: order.created_at
  updated_at: order.updated_at
  total_price: order.total_price
  subtotal_price: order.subtotal_price
  total_tax: order.total_tax
  total_discounts: order.total_discounts
  currency: order.currency
  financial_status: order.financial_status
  fulfillment_status: order.fulfillment_status
  customer: order.customer
  line_items: order.line_items
  shipping_address: order.shipping_address
  billing_address: order.billing_address
  note: order.note
  tags: order.tags
```

### Product

```yaml
shopify_product:
  id: product.id
  title: product.title
  body_html: product.body_html
  vendor: product.vendor
  product_type: product.product_type
  created_at: product.created_at
  handle: product.handle
  status: product.status
  tags: product.tags
  variants: product.variants
  images: product.images
  options: product.options
```

## Webhook Events

Common events for synchronization:

```yaml
webhooks:
  - topic: customers/create
    address: https://your-app.com/webhooks/shopify/customers/create
  - topic: customers/update
    address: https://your-app.com/webhooks/shopify/customers/update
  - topic: orders/create
    address: https://your-app.com/webhooks/shopify/orders/create
  - topic: orders/paid
    address: https://your-app.com/webhooks/shopify/orders/paid
  - topic: products/create
    address: https://your-app.com/webhooks/shopify/products/create
  - topic: products/update
    address: https://your-app.com/webhooks/shopify/products/update
```

## Error Handling

Shopify-specific error codes:

```typescript
const SHOPIFY_ERROR_CODES = {
  401: 'Unauthorized - Check access token',
  402: 'Payment Required - Shop is frozen',
  403: 'Forbidden - Missing required scope',
  404: 'Not Found - Resource doesn\'t exist',
  422: 'Unprocessable Entity - Validation error',
  429: 'Too Many Requests - Rate limited',
  500: 'Internal Server Error - Retry later',
  503: 'Service Unavailable - Retry later',
};

function handleShopifyError(response: Response, body: unknown): never {
  const errors = (body as { errors?: unknown })?.errors;
  throw {
    code: `SHOPIFY_${response.status}`,
    message: SHOPIFY_ERROR_CODES[response.status] || 'Unknown error',
    statusCode: response.status,
    details: errors,
    retryable: response.status === 429 || response.status >= 500,
  };
}
```

## GraphQL Admin API

For complex queries, use GraphQL:

```typescript
async function shopifyGraphQL<T>(query: string, variables?: Record<string, unknown>): Promise<T> {
  const response = await fetch(`${baseUrl}/graphql.json`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, variables }),
  });
  
  const data = await response.json();
  if (data.errors) {
    throw new Error(data.errors.map((e: { message: string }) => e.message).join(', '));
  }
  
  return data.data;
}

// Example: Get customer with orders
const query = `
  query getCustomer($id: ID!) {
    customer(id: $id) {
      id
      email
      firstName
      lastName
      orders(first: 10) {
        edges {
          node {
            id
            name
            totalPriceSet {
              shopMoney {
                amount
                currencyCode
              }
            }
          }
        }
      }
    }
  }
`;
```
