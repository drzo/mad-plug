# Error Handling

This reference covers patterns for robust error handling across multiple platforms.

## Error Normalization

Normalize platform-specific errors into a common format:

```typescript
interface NormalizedError {
  code: string;
  message: string;
  platform: string;
  statusCode?: number;
  retryable: boolean;
  details?: Record<string, unknown>;
  originalError?: unknown;
}

function normalizeError(error: unknown, platform: string): NormalizedError {
  if (error instanceof ShopifyError) {
    return {
      code: `SHOPIFY_${error.code}`,
      message: error.message,
      platform: 'shopify',
      statusCode: error.statusCode,
      retryable: error.statusCode === 429 || error.statusCode >= 500,
      details: error.errors,
      originalError: error,
    };
  }
  
  if (error instanceof StripeError) {
    return {
      code: `STRIPE_${error.type}`,
      message: error.message,
      platform: 'stripe',
      statusCode: error.statusCode,
      retryable: error.type === 'rate_limit_error' || error.statusCode >= 500,
      details: { param: error.param },
      originalError: error,
    };
  }
  
  // Generic fallback
  return {
    code: 'UNKNOWN_ERROR',
    message: String(error),
    platform,
    retryable: false,
    originalError: error,
  };
}
```

## Retry Strategies

Implement exponential backoff with jitter:

```typescript
interface RetryConfig {
  maxAttempts: number;
  baseDelay: number;
  maxDelay: number;
  jitterFactor: number;
}

const DEFAULT_RETRY_CONFIG: RetryConfig = {
  maxAttempts: 3,
  baseDelay: 1000,
  maxDelay: 30000,
  jitterFactor: 0.2,
};

async function withRetry<T>(
  operation: () => Promise<T>,
  config: Partial<RetryConfig> = {}
): Promise<T> {
  const { maxAttempts, baseDelay, maxDelay, jitterFactor } = {
    ...DEFAULT_RETRY_CONFIG,
    ...config,
  };
  
  let lastError: Error | undefined;
  
  for (let attempt = 1; attempt <= maxAttempts; attempt++) {
    try {
      return await operation();
    } catch (error) {
      lastError = error as Error;
      const normalized = normalizeError(error, 'unknown');
      
      if (!normalized.retryable || attempt === maxAttempts) {
        throw error;
      }
      
      // Calculate delay with exponential backoff and jitter
      const exponentialDelay = baseDelay * Math.pow(2, attempt - 1);
      const jitter = exponentialDelay * jitterFactor * (Math.random() * 2 - 1);
      const delay = Math.min(exponentialDelay + jitter, maxDelay);
      
      console.log(`Retry attempt ${attempt}/${maxAttempts} after ${delay}ms`);
      await sleep(delay);
    }
  }
  
  throw lastError;
}

function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

## Circuit Breaker

Prevent cascading failures:

```typescript
enum CircuitState {
  CLOSED = 'CLOSED',
  OPEN = 'OPEN',
  HALF_OPEN = 'HALF_OPEN',
}

interface CircuitBreakerConfig {
  failureThreshold: number;
  resetTimeout: number;
  halfOpenRequests: number;
}

class CircuitBreaker {
  private state: CircuitState = CircuitState.CLOSED;
  private failures: number = 0;
  private lastFailure: number = 0;
  private halfOpenSuccesses: number = 0;
  
  constructor(private config: CircuitBreakerConfig) {}
  
  async execute<T>(operation: () => Promise<T>): Promise<T> {
    if (this.state === CircuitState.OPEN) {
      if (Date.now() - this.lastFailure > this.config.resetTimeout) {
        this.state = CircuitState.HALF_OPEN;
        this.halfOpenSuccesses = 0;
      } else {
        throw new Error('Circuit breaker is OPEN');
      }
    }
    
    try {
      const result = await operation();
      this.onSuccess();
      return result;
    } catch (error) {
      this.onFailure();
      throw error;
    }
  }
  
  private onSuccess(): void {
    if (this.state === CircuitState.HALF_OPEN) {
      this.halfOpenSuccesses++;
      if (this.halfOpenSuccesses >= this.config.halfOpenRequests) {
        this.state = CircuitState.CLOSED;
        this.failures = 0;
      }
    } else {
      this.failures = 0;
    }
  }
  
  private onFailure(): void {
    this.failures++;
    this.lastFailure = Date.now();
    
    if (this.state === CircuitState.HALF_OPEN) {
      this.state = CircuitState.OPEN;
    } else if (this.failures >= this.config.failureThreshold) {
      this.state = CircuitState.OPEN;
    }
  }
}
```

## Fallback Mechanisms

Provide graceful degradation:

```typescript
async function withFallback<T>(
  primary: () => Promise<T>,
  fallback: () => Promise<T>,
  shouldFallback: (error: unknown) => boolean = () => true
): Promise<T> {
  try {
    return await primary();
  } catch (error) {
    if (shouldFallback(error)) {
      console.warn('Primary failed, using fallback:', error);
      return fallback();
    }
    throw error;
  }
}

// Example: Fall back to cached data
async function getCustomer(id: string): Promise<Customer> {
  return withFallback(
    () => shopifyAdapter.getCustomer(id),
    () => cache.get(`customer:${id}`),
    (error) => normalizeError(error, 'shopify').statusCode >= 500
  );
}
```

## Compensating Transactions

Undo partial operations on failure:

```typescript
interface CompensatableOperation<T> {
  execute: () => Promise<T>;
  compensate: (result: T) => Promise<void>;
}

async function executeWithCompensation<T>(
  operations: CompensatableOperation<T>[]
): Promise<T[]> {
  const results: T[] = [];
  
  try {
    for (const op of operations) {
      const result = await op.execute();
      results.push(result);
    }
    return results;
  } catch (error) {
    // Compensate in reverse order
    for (let i = results.length - 1; i >= 0; i--) {
      try {
        await operations[i].compensate(results[i]);
      } catch (compensateError) {
        console.error('Compensation failed:', compensateError);
        // Log but continue compensating
      }
    }
    throw error;
  }
}

// Example usage
await executeWithCompensation([
  {
    execute: () => stripeAdapter.createCustomer(data),
    compensate: (customer) => stripeAdapter.deleteCustomer(customer.id),
  },
  {
    execute: () => shopifyAdapter.createCustomer(data),
    compensate: (customer) => shopifyAdapter.deleteCustomer(customer.id),
  },
]);
```

## Error Logging and Reporting

Structured error logging:

```typescript
interface ErrorLog {
  timestamp: string;
  platform: string;
  operation: string;
  error: NormalizedError;
  context: Record<string, unknown>;
  traceId: string;
}

function logError(
  error: NormalizedError,
  operation: string,
  context: Record<string, unknown> = {}
): void {
  const log: ErrorLog = {
    timestamp: new Date().toISOString(),
    platform: error.platform,
    operation,
    error,
    context,
    traceId: getTraceId(),
  };
  
  console.error(JSON.stringify(log));
  
  // Send to error tracking service
  if (error.statusCode && error.statusCode >= 500) {
    sendToErrorTracker(log);
  }
}
```
