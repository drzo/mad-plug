# QuickBooks Online Integration Patterns

## Authentication

QuickBooks uses OAuth 2.0 with short-lived tokens:

```yaml
auth:
  type: oauth2
  token_env: QUICKBOOKS_ACCESS_TOKEN
  refresh_env: QUICKBOOKS_REFRESH_TOKEN
  token_url: https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer
  # Access tokens expire in 1 hour
  # Refresh tokens expire in 100 days
```

**Token refresh implementation:**

```typescript
async function refreshQuickBooksToken(): Promise<TokenResponse> {
  const response = await fetch('https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Authorization': `Basic ${Buffer.from(`${clientId}:${clientSecret}`).toString('base64')}`,
    },
    body: new URLSearchParams({
      grant_type: 'refresh_token',
      refresh_token: process.env.QUICKBOOKS_REFRESH_TOKEN!,
    }),
  });
  
  const data = await response.json();
  // Store new tokens
  process.env.QUICKBOOKS_ACCESS_TOKEN = data.access_token;
  if (data.refresh_token) {
    process.env.QUICKBOOKS_REFRESH_TOKEN = data.refresh_token;
  }
  
  return data;
}
```

## Rate Limiting

QuickBooks has per-minute rate limits:

```typescript
const QUICKBOOKS_RATE_LIMIT = {
  requests: 500,           // Per minute per realm
  concurrentRequests: 10,  // Concurrent requests
};
```

## Pagination

QuickBooks uses offset-based pagination:

```typescript
async function* paginateQuickBooks<T>(
  entity: string,
  query?: string
): AsyncGenerator<T[]> {
  let startPosition = 1;
  const maxResults = 1000;
  
  while (true) {
    const queryStr = query 
      ? `${query} STARTPOSITION ${startPosition} MAXRESULTS ${maxResults}`
      : `SELECT * FROM ${entity} STARTPOSITION ${startPosition} MAXRESULTS ${maxResults}`;
    
    const response = await fetch(
      `${baseUrl}/query?query=${encodeURIComponent(queryStr)}`,
      { headers: getAuthHeaders() }
    );
    const data = await response.json();
    
    const results = data.QueryResponse[entity] || [];
    if (results.length === 0) break;
    
    yield results;
    
    if (results.length < maxResults) break;
    startPosition += maxResults;
  }
}
```

## Common Entity Mappings

### Customer

```yaml
quickbooks_customer:
  id: Customer.Id
  sync_token: Customer.SyncToken  # Required for updates
  display_name: Customer.DisplayName
  given_name: Customer.GivenName
  family_name: Customer.FamilyName
  company_name: Customer.CompanyName
  email: Customer.PrimaryEmailAddr.Address
  phone: Customer.PrimaryPhone.FreeFormNumber
  mobile: Customer.Mobile.FreeFormNumber
  billing_address: Customer.BillAddr
  shipping_address: Customer.ShipAddr
  balance: Customer.Balance
  active: Customer.Active
  created_at: Customer.MetaData.CreateTime
  updated_at: Customer.MetaData.LastUpdatedTime
  notes: Customer.Notes
```

### Invoice

```yaml
quickbooks_invoice:
  id: Invoice.Id
  sync_token: Invoice.SyncToken
  doc_number: Invoice.DocNumber
  txn_date: Invoice.TxnDate
  due_date: Invoice.DueDate
  customer_ref: Invoice.CustomerRef
  line_items: Invoice.Line
  total_amt: Invoice.TotalAmt
  balance: Invoice.Balance
  currency_ref: Invoice.CurrencyRef
  email_status: Invoice.EmailStatus
  billing_email: Invoice.BillEmail.Address
  created_at: Invoice.MetaData.CreateTime
```

### Item (Product/Service)

```yaml
quickbooks_item:
  id: Item.Id
  sync_token: Item.SyncToken
  name: Item.Name
  description: Item.Description
  type: Item.Type  # Inventory, Service, NonInventory
  unit_price: Item.UnitPrice
  income_account_ref: Item.IncomeAccountRef
  expense_account_ref: Item.ExpenseAccountRef
  asset_account_ref: Item.AssetAccountRef
  qty_on_hand: Item.QtyOnHand
  active: Item.Active
```

## Query Language

QuickBooks uses a SQL-like query language:

```typescript
// Query examples
const queries = {
  // Get all active customers
  activeCustomers: "SELECT * FROM Customer WHERE Active = true",
  
  // Get customers by email
  customerByEmail: (email: string) => 
    `SELECT * FROM Customer WHERE PrimaryEmailAddr = '${email}'`,
  
  // Get invoices by date range
  invoicesByDate: (start: string, end: string) =>
    `SELECT * FROM Invoice WHERE TxnDate >= '${start}' AND TxnDate <= '${end}'`,
  
  // Get unpaid invoices
  unpaidInvoices: "SELECT * FROM Invoice WHERE Balance > '0'",
  
  // Count customers
  customerCount: "SELECT COUNT(*) FROM Customer",
};

async function queryQuickBooks<T>(query: string): Promise<T[]> {
  const response = await fetch(
    `${baseUrl}/query?query=${encodeURIComponent(query)}`,
    { headers: getAuthHeaders() }
  );
  const data = await response.json();
  
  // Extract entity type from query
  const entityMatch = query.match(/FROM\s+(\w+)/i);
  const entity = entityMatch ? entityMatch[1] : 'Unknown';
  
  return data.QueryResponse[entity] || [];
}
```

## Creating/Updating Entities

QuickBooks requires SyncToken for updates:

```typescript
// Create customer
async function createCustomer(data: CustomerInput): Promise<Customer> {
  const response = await fetch(`${baseUrl}/customer`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(data),
  });
  
  const result = await response.json();
  return result.Customer;
}

// Update customer (requires SyncToken)
async function updateCustomer(id: string, data: Partial<CustomerInput>): Promise<Customer> {
  // First, get current entity to obtain SyncToken
  const current = await getCustomer(id);
  
  const response = await fetch(`${baseUrl}/customer`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      ...data,
      Id: id,
      SyncToken: current.SyncToken,
      sparse: true,  // Only update provided fields
    }),
  });
  
  const result = await response.json();
  return result.Customer;
}
```

## Error Handling

QuickBooks-specific error handling:

```typescript
interface QuickBooksError {
  Fault: {
    Error: Array<{
      Message: string;
      Detail: string;
      code: string;
      element?: string;
    }>;
    type: string;
  };
}

const QUICKBOOKS_ERROR_CODES = {
  '100': 'Application error',
  '500': 'Invalid request',
  '610': 'Object not found',
  '2000': 'Duplicate name exists',
  '2010': 'Required field missing',
  '3100': 'Business validation error',
  '3200': 'Stale object error (SyncToken mismatch)',
  '4000': 'Element not found',
  '5010': 'Limit exceeded',
  '6000': 'Authorization failed',
};

function handleQuickBooksError(error: QuickBooksError): never {
  const firstError = error.Fault.Error[0];
  throw {
    code: `QUICKBOOKS_${firstError.code}`,
    message: firstError.Message,
    details: {
      detail: firstError.Detail,
      element: firstError.element,
      type: error.Fault.type,
    },
    retryable: firstError.code === '3200',  // Stale object can be retried after refresh
  };
}
```

## Webhook Events

QuickBooks webhook configuration:

```yaml
webhooks:
  verifier_token: YOUR_VERIFIER_TOKEN
  events:
    - name: Customer
      operations: [Create, Update, Delete]
    - name: Invoice
      operations: [Create, Update, Delete, Void]
    - name: Payment
      operations: [Create, Update, Delete, Void]
    - name: Item
      operations: [Create, Update, Delete]
```

**Webhook signature verification:**

```typescript
import crypto from 'crypto';

function verifyQuickBooksWebhook(
  payload: string,
  signature: string,
  verifierToken: string
): boolean {
  const hash = crypto
    .createHmac('sha256', verifierToken)
    .update(payload)
    .digest('base64');
  
  return hash === signature;
}
```
