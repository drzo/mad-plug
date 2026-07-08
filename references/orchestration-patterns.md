# Orchestration Patterns

This reference covers patterns for coordinating API calls across multiple platforms.

## Sequential Orchestration

Execute steps in order, passing context between them. Use when operations depend on previous results.

```yaml
orchestration:
  type: sequential
  steps:
    - action: fetch
      platform: shopify
      entity: order
    - action: transform
      mapping: order_to_invoice
    - action: create
      platform: quickbooks
      entity: invoice
    - action: update
      platform: shopify
      entity: order
      field: note
```

**Implementation pattern:**

```typescript
async function executeSequential(steps: Step[], context: Context): Promise<Result[]> {
  const results: Result[] = [];
  
  for (const step of steps) {
    const adapter = getAdapter(step.platform);
    const result = await adapter.execute(step.action, context);
    results.push({ step: step.action, result });
    Object.assign(context, result); // Pass data to next step
  }
  
  return results;
}
```

## Parallel Orchestration

Execute operations simultaneously across platforms. Use when operations are independent.

```yaml
orchestration:
  type: parallel
  platforms: [shopify, stripe, quickbooks]
  rollback: true
```

**Implementation pattern:**

```typescript
async function executeParallel(platforms: string[], operation: Operation): Promise<Results> {
  const tasks = platforms.map(p => getAdapter(p).execute(operation));
  const results = await Promise.allSettled(tasks);
  
  return platforms.reduce((acc, platform, i) => {
    const result = results[i];
    acc[platform] = result.status === 'fulfilled' ? result.value : { error: result.reason };
    return acc;
  }, {});
}
```

## Saga Pattern

Distributed transactions with compensation. Use when you need atomicity across platforms.

```yaml
orchestration:
  type: saga
  steps:
    - action: create
      platform: stripe
      entity: customer
      compensate:
        action: delete
        platform: stripe
        entity: customer
    - action: create
      platform: shopify
      entity: customer
      compensate:
        action: delete
        platform: shopify
        entity: customer
    - action: create
      platform: quickbooks
      entity: customer
      compensate:
        action: delete
        platform: quickbooks
        entity: customer
```

**Implementation pattern:**

```typescript
async function executeSaga(steps: SagaStep[]): Promise<SagaResult> {
  const completed: SagaStep[] = [];
  
  try {
    for (const step of steps) {
      const result = await executeStep(step);
      completed.push({ ...step, result });
    }
    return { success: true, results: completed };
  } catch (error) {
    // Compensate in reverse order
    for (const step of completed.reverse()) {
      if (step.compensate) {
        await executeStep(step.compensate);
      }
    }
    return { success: false, error, compensated: completed };
  }
}
```

## Event-Driven Orchestration

React to platform webhooks. Use for real-time synchronization.

```yaml
orchestration:
  type: event_driven
  triggers:
    - platform: shopify
      event: orders/create
      actions:
        - action: transform
          mapping: order_to_invoice
        - action: create
          platform: quickbooks
          entity: invoice
    - platform: stripe
      event: invoice.paid
      actions:
        - action: update
          platform: shopify
          entity: order
          field: financial_status
```

**Implementation pattern:**

```typescript
class EventOrchestrator {
  private handlers: Map<string, EventHandler[]> = new Map();
  
  register(platform: string, event: string, handler: EventHandler): void {
    const key = `${platform}:${event}`;
    const handlers = this.handlers.get(key) || [];
    handlers.push(handler);
    this.handlers.set(key, handlers);
  }
  
  async handle(platform: string, event: string, payload: unknown): Promise<void> {
    const key = `${platform}:${event}`;
    const handlers = this.handlers.get(key) || [];
    
    for (const handler of handlers) {
      await handler(payload);
    }
  }
}
```

## Choosing the Right Pattern

| Pattern | Use When | Trade-offs |
|---------|----------|------------|
| Sequential | Steps depend on each other | Slower, but predictable |
| Parallel | Operations are independent | Faster, but harder to handle partial failures |
| Saga | Need atomicity across platforms | Complex, but ensures consistency |
| Event-driven | Real-time sync needed | Eventual consistency, requires webhook setup |

## Error Handling in Orchestration

Always implement error boundaries:

```typescript
async function withErrorBoundary<T>(
  operation: () => Promise<T>,
  context: { platform: string; action: string }
): Promise<Result<T>> {
  try {
    const data = await operation();
    return { success: true, data };
  } catch (error) {
    return {
      success: false,
      error: normalizeError(error, context),
    };
  }
}
```
