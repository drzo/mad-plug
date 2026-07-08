# Authentication Strategies

This reference covers patterns for handling authentication across multiple platforms.

## Authentication Types

| Type | Platforms | Characteristics |
|------|-----------|-----------------|
| OAuth 2.0 | Shopify, QuickBooks, Slack | Token refresh required, user consent |
| API Key | Stripe, SendGrid | Simple, no refresh, rotate periodically |
| Bearer Token | GitHub, many REST APIs | Similar to API key, often from OAuth |
| Basic Auth | Legacy systems | Username/password, avoid if possible |

## Unified Auth Manager

Centralize authentication handling:

```typescript
interface AuthProvider {
  type: 'oauth2' | 'api_key' | 'token' | 'basic';
  getHeaders(): Promise<Record<string, string>>;
  refresh?(): Promise<void>;
  isExpired?(): boolean;
}

class AuthManager {
  private providers: Map<string, AuthProvider> = new Map();
  
  register(platform: string, provider: AuthProvider): void {
    this.providers.set(platform, provider);
  }
  
  async getHeaders(platform: string): Promise<Record<string, string>> {
    const provider = this.providers.get(platform);
    if (!provider) throw new Error(`No auth provider for ${platform}`);
    
    if (provider.isExpired?.() && provider.refresh) {
      await provider.refresh();
    }
    
    return provider.getHeaders();
  }
}
```

## OAuth 2.0 Token Refresh

Handle token expiration gracefully:

```typescript
class OAuth2Provider implements AuthProvider {
  type = 'oauth2' as const;
  private accessToken: string;
  private refreshToken: string;
  private expiresAt: number;
  private tokenUrl: string;
  private clientId: string;
  private clientSecret: string;
  
  constructor(config: OAuth2Config) {
    this.accessToken = config.accessToken;
    this.refreshToken = config.refreshToken;
    this.expiresAt = config.expiresAt;
    this.tokenUrl = config.tokenUrl;
    this.clientId = config.clientId;
    this.clientSecret = config.clientSecret;
  }
  
  isExpired(): boolean {
    // Refresh 5 minutes before expiration
    return Date.now() > this.expiresAt - 300000;
  }
  
  async refresh(): Promise<void> {
    const response = await fetch(this.tokenUrl, {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: new URLSearchParams({
        grant_type: 'refresh_token',
        refresh_token: this.refreshToken,
        client_id: this.clientId,
        client_secret: this.clientSecret,
      }),
    });
    
    const data = await response.json();
    this.accessToken = data.access_token;
    this.expiresAt = Date.now() + data.expires_in * 1000;
    if (data.refresh_token) {
      this.refreshToken = data.refresh_token;
    }
  }
  
  async getHeaders(): Promise<Record<string, string>> {
    return { Authorization: `Bearer ${this.accessToken}` };
  }
}
```

## API Key Management

Secure API key handling:

```typescript
class ApiKeyProvider implements AuthProvider {
  type = 'api_key' as const;
  private keyEnvVar: string;
  private headerFormat: string;
  
  constructor(config: { keyEnvVar: string; headerFormat?: string }) {
    this.keyEnvVar = config.keyEnvVar;
    this.headerFormat = config.headerFormat || 'Bearer {key}';
  }
  
  async getHeaders(): Promise<Record<string, string>> {
    const key = process.env[this.keyEnvVar];
    if (!key) throw new Error(`Missing env var: ${this.keyEnvVar}`);
    
    const value = this.headerFormat.replace('{key}', key);
    return { Authorization: value };
  }
}
```

## Multi-Tenant Authentication

Handle multiple accounts per platform:

```typescript
interface TenantCredentials {
  tenantId: string;
  platform: string;
  credentials: AuthConfig;
}

class MultiTenantAuthManager {
  private credentials: Map<string, AuthProvider> = new Map();
  
  private getKey(tenantId: string, platform: string): string {
    return `${tenantId}:${platform}`;
  }
  
  register(tenant: TenantCredentials): void {
    const key = this.getKey(tenant.tenantId, tenant.platform);
    const provider = createProvider(tenant.credentials);
    this.credentials.set(key, provider);
  }
  
  async getHeaders(tenantId: string, platform: string): Promise<Record<string, string>> {
    const key = this.getKey(tenantId, platform);
    const provider = this.credentials.get(key);
    if (!provider) throw new Error(`No credentials for tenant ${tenantId} on ${platform}`);
    return provider.getHeaders();
  }
}
```

## Credential Storage

Best practices for storing credentials:

```yaml
# .env (development only)
SHOPIFY_ACCESS_TOKEN=shpat_xxx
STRIPE_SECRET_KEY=sk_test_xxx
QUICKBOOKS_ACCESS_TOKEN=xxx
QUICKBOOKS_REFRESH_TOKEN=xxx

# Production: Use secret managers
# - AWS Secrets Manager
# - HashiCorp Vault
# - Azure Key Vault
# - Google Secret Manager
```

**Secret manager integration:**

```typescript
import { SecretsManager } from '@aws-sdk/client-secrets-manager';

class SecretManagerCredentialStore {
  private client: SecretsManager;
  private cache: Map<string, { value: string; expiresAt: number }> = new Map();
  
  constructor() {
    this.client = new SecretsManager({});
  }
  
  async getSecret(secretId: string): Promise<string> {
    const cached = this.cache.get(secretId);
    if (cached && cached.expiresAt > Date.now()) {
      return cached.value;
    }
    
    const response = await this.client.getSecretValue({ SecretId: secretId });
    const value = response.SecretString!;
    
    // Cache for 5 minutes
    this.cache.set(secretId, { value, expiresAt: Date.now() + 300000 });
    return value;
  }
}
```

## Platform-Specific Auth Notes

**Shopify:** Uses OAuth 2.0 with offline access tokens that don't expire but can be revoked.

**Stripe:** API keys don't expire. Use restricted keys in production with minimal permissions.

**QuickBooks:** OAuth 2.0 with 1-hour access tokens and 100-day refresh tokens. Must refresh before expiration.

**Slack:** Bot tokens don't expire. User tokens may require re-authorization.
