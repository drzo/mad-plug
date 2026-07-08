# Stripe Integration Patterns

## Authentication

Stripe uses API keys:

```yaml
auth:
  type: api_key
  key_env: STRIPE_SECRET_KEY
  header: "Authorization: Bearer {key}"
```

**Key types:**
- `sk_test_*` - Test mode secret key
- `sk_live_*` - Live mode secret key
- `rk_test_*` / `rk_live_*` - Restricted keys (recommended for production)

## Rate Limiting

Stripe has generous rate limits:

```typescript
const STRIPE_RATE_LIMIT = {
  requests: 100,           // Per second in test mode
  liveRequests: 100,       // Per second in live mode
  readRequests: 100,       // Per second for read operations
  writeRequests: 100,      // Per second for write operations
};

// Stripe returns 429 with Retry-After header
function handleRateLimit(response: Response): number {
  const retryAfter = response.headers.get('Retry-After');
  return retryAfter ? parseInt(retryAfter) * 1000 : 1000;
}
```

## Pagination

Stripe uses cursor-based pagination:

```typescript
async function* paginateStripe<T>(
  endpoint: string,
  params: Record<string, string> = {}
): AsyncGenerator<T[]> {
  let startingAfter: string | undefined;
  
  while (true) {
    const queryParams = new URLSearchParams({
      ...params,
      limit: '100',
      ...(startingAfter && { starting_after: startingAfter }),
    });
    
    const response = await fetch(`${baseUrl}${endpoint}?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    const data = await response.json();
    
    yield data.data;
    
    if (!data.has_more) break;
    startingAfter = data.data[data.data.length - 1].id;
  }
}
```

## Common Entity Mappings

### Customer

```yaml
stripe_customer:
  id: customer.id
  email: customer.email
  name: customer.name
  phone: customer.phone
  description: customer.description
  created: customer.created  # Unix timestamp
  currency: customer.currency
  default_source: customer.default_source
  metadata: customer.metadata
  address: customer.address
  shipping: customer.shipping
```

### Invoice

```yaml
stripe_invoice:
  id: invoice.id
  customer: invoice.customer
  subscription: invoice.subscription
  status: invoice.status  # draft, open, paid, uncollectible, void
  total: invoice.total  # In cents
  subtotal: invoice.subtotal
  tax: invoice.tax
  currency: invoice.currency
  created: invoice.created
  due_date: invoice.due_date
  paid: invoice.paid
  lines: invoice.lines.data
  metadata: invoice.metadata
```

### Product & Price

```yaml
stripe_product:
  id: product.id
  name: product.name
  description: product.description
  active: product.active
  metadata: product.metadata
  images: product.images
  created: product.created

stripe_price:
  id: price.id
  product: price.product
  unit_amount: price.unit_amount  # In cents
  currency: price.currency
  type: price.type  # one_time, recurring
  recurring: price.recurring  # interval, interval_count
  active: price.active
```

### Payment Intent

```yaml
stripe_payment_intent:
  id: payment_intent.id
  amount: payment_intent.amount  # In cents
  currency: payment_intent.currency
  status: payment_intent.status
  customer: payment_intent.customer
  payment_method: payment_intent.payment_method
  created: payment_intent.created
  metadata: payment_intent.metadata
```

## Webhook Events

Common events for synchronization:

```yaml
webhooks:
  - type: customer.created
  - type: customer.updated
  - type: invoice.created
  - type: invoice.paid
  - type: invoice.payment_failed
  - type: payment_intent.succeeded
  - type: payment_intent.payment_failed
  - type: subscription.created
  - type: subscription.updated
  - type: subscription.deleted
```

**Webhook signature verification:**

```typescript
import Stripe from 'stripe';

function verifyWebhook(
  payload: string,
  signature: string,
  endpointSecret: string
): Stripe.Event {
  const stripe = new Stripe(process.env.STRIPE_SECRET_KEY!);
  return stripe.webhooks.constructEvent(payload, signature, endpointSecret);
}
```

## Error Handling

Stripe-specific error types:

```typescript
const STRIPE_ERROR_TYPES = {
  api_error: 'API Error - Retry later',
  card_error: 'Card Error - Payment failed',
  idempotency_error: 'Idempotency Error - Request conflict',
  invalid_request_error: 'Invalid Request - Check parameters',
  rate_limit_error: 'Rate Limit - Slow down',
  authentication_error: 'Authentication Error - Check API key',
  api_connection_error: 'Connection Error - Network issue',
};

function handleStripeError(error: Stripe.StripeError): never {
  throw {
    code: `STRIPE_${error.type}`,
    message: error.message,
    statusCode: error.statusCode,
    details: {
      type: error.type,
      code: error.code,
      param: error.param,
      decline_code: error.decline_code,
    },
    retryable: error.type === 'rate_limit_error' || error.type === 'api_error',
  };
}
```

## Idempotency

Use idempotency keys for safe retries:

```typescript
async function createWithIdempotency<T>(
  endpoint: string,
  data: Record<string, unknown>,
  idempotencyKey?: string
): Promise<T> {
  const key = idempotencyKey || `${endpoint}-${JSON.stringify(data)}-${Date.now()}`;
  
  const response = await fetch(`${baseUrl}${endpoint}`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/x-www-form-urlencoded',
      'Idempotency-Key': key,
    },
    body: new URLSearchParams(flattenObject(data)),
  });
  
  return response.json();
}

// Flatten nested objects for form encoding
function flattenObject(obj: Record<string, unknown>, prefix = ''): Record<string, string> {
  const result: Record<string, string> = {};
  
  for (const [key, value] of Object.entries(obj)) {
    const newKey = prefix ? `${prefix}[${key}]` : key;
    
    if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
      Object.assign(result, flattenObject(value as Record<string, unknown>, newKey));
    } else {
      result[newKey] = String(value);
    }
  }
  
  return result;
}
```

## Expand Related Objects

Fetch related data in a single request:

```typescript
// Expand customer and payment method with invoice
const invoice = await stripe.invoices.retrieve('inv_xxx', {
  expand: ['customer', 'payment_intent.payment_method'],
});

// Access expanded data
console.log(invoice.customer.email);  // Instead of just customer ID
```
