# Slack Integration Patterns

## Authentication

Slack uses OAuth 2.0 with bot tokens:

```yaml
auth:
  type: oauth2
  token_env: SLACK_BOT_TOKEN
  # Bot tokens don't expire
  # User tokens may require re-authorization
```

**Token types:**
- `xoxb-*` - Bot tokens (recommended)
- `xoxp-*` - User tokens
- `xapp-*` - App-level tokens (for Socket Mode)

## Rate Limiting

Slack has tier-based rate limits:

```typescript
const SLACK_RATE_LIMITS = {
  tier1: { requests: 1, period: 60 },      // Posting messages
  tier2: { requests: 20, period: 60 },     // Most read operations
  tier3: { requests: 50, period: 60 },     // Conversations list
  tier4: { requests: 100, period: 60 },    // Auth test, etc.
  special: { requests: 1, period: 1 },     // Files.upload
};

// Rate limit headers
function parseRateLimitHeaders(response: Response): RateLimitInfo {
  return {
    limit: parseInt(response.headers.get('X-RateLimit-Limit') || '0'),
    remaining: parseInt(response.headers.get('X-RateLimit-Remaining') || '0'),
    reset: parseInt(response.headers.get('X-RateLimit-Reset') || '0'),
    retryAfter: parseInt(response.headers.get('Retry-After') || '0'),
  };
}
```

## Pagination

Slack uses cursor-based pagination:

```typescript
async function* paginateSlack<T>(
  method: string,
  params: Record<string, string> = {}
): AsyncGenerator<T[]> {
  let cursor: string | undefined;
  
  do {
    const queryParams = new URLSearchParams({
      ...params,
      limit: '200',
      ...(cursor && { cursor }),
    });
    
    const response = await fetch(`${baseUrl}/${method}?${queryParams}`, {
      headers: getAuthHeaders(),
    });
    const data = await response.json();
    
    if (!data.ok) {
      throw new Error(data.error);
    }
    
    // Response key varies by method
    const items = data.channels || data.members || data.messages || data.users || [];
    yield items;
    
    cursor = data.response_metadata?.next_cursor;
  } while (cursor);
}
```

## Common Entity Mappings

### User

```yaml
slack_user:
  id: user.id
  team_id: user.team_id
  name: user.name
  real_name: user.real_name
  display_name: user.profile.display_name
  email: user.profile.email
  phone: user.profile.phone
  title: user.profile.title
  status_text: user.profile.status_text
  status_emoji: user.profile.status_emoji
  is_admin: user.is_admin
  is_owner: user.is_owner
  is_bot: user.is_bot
  deleted: user.deleted
  tz: user.tz
  avatar: user.profile.image_192
```

### Channel

```yaml
slack_channel:
  id: channel.id
  name: channel.name
  is_channel: channel.is_channel
  is_private: channel.is_private
  is_archived: channel.is_archived
  created: channel.created
  creator: channel.creator
  topic: channel.topic.value
  purpose: channel.purpose.value
  num_members: channel.num_members
```

### Message

```yaml
slack_message:
  ts: message.ts  # Timestamp (unique ID)
  channel: message.channel
  user: message.user
  text: message.text
  type: message.type
  subtype: message.subtype
  thread_ts: message.thread_ts
  reply_count: message.reply_count
  reactions: message.reactions
  attachments: message.attachments
  blocks: message.blocks
```

## Common Operations

### Send Message

```typescript
async function sendMessage(channel: string, text: string, options?: MessageOptions): Promise<Message> {
  const response = await fetch(`${baseUrl}/chat.postMessage`, {
    method: 'POST',
    headers: {
      ...getAuthHeaders(),
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      channel,
      text,
      ...options,
    }),
  });
  
  const data = await response.json();
  if (!data.ok) {
    throw new Error(data.error);
  }
  
  return data.message;
}

// With blocks for rich formatting
await sendMessage('C1234567890', 'Order Update', {
  blocks: [
    {
      type: 'section',
      text: {
        type: 'mrkdwn',
        text: '*New Order Received*\nOrder #12345',
      },
    },
    {
      type: 'actions',
      elements: [
        {
          type: 'button',
          text: { type: 'plain_text', text: 'View Order' },
          url: 'https://example.com/orders/12345',
        },
      ],
    },
  ],
});
```

### Search Messages

```typescript
async function searchMessages(query: string, options?: SearchOptions): Promise<SearchResult> {
  const params = new URLSearchParams({
    query,
    sort: options?.sort || 'timestamp',
    sort_dir: options?.sortDir || 'desc',
    count: String(options?.count || 20),
  });
  
  const response = await fetch(`${baseUrl}/search.messages?${params}`, {
    headers: getAuthHeaders(),
  });
  
  const data = await response.json();
  if (!data.ok) {
    throw new Error(data.error);
  }
  
  return data.messages;
}
```

## Event Subscriptions

Common events for integration:

```yaml
events:
  # Message events
  - message.channels
  - message.groups
  - message.im
  - message.mpim
  
  # User events
  - user_change
  - team_join
  
  # Channel events
  - channel_created
  - channel_archive
  - member_joined_channel
  - member_left_channel
  
  # App events
  - app_mention
  - app_home_opened
```

**Event handling:**

```typescript
interface SlackEvent {
  type: string;
  event: {
    type: string;
    user?: string;
    channel?: string;
    text?: string;
    ts?: string;
  };
  event_id: string;
  event_time: number;
}

async function handleSlackEvent(event: SlackEvent): Promise<void> {
  switch (event.event.type) {
    case 'message':
      await handleMessage(event.event);
      break;
    case 'app_mention':
      await handleMention(event.event);
      break;
    case 'member_joined_channel':
      await handleMemberJoined(event.event);
      break;
  }
}
```

## Error Handling

Slack-specific error handling:

```typescript
const SLACK_ERROR_CODES = {
  not_authed: 'No authentication token provided',
  invalid_auth: 'Invalid authentication token',
  account_inactive: 'Account has been deactivated',
  token_revoked: 'Token has been revoked',
  no_permission: 'Missing required scope',
  channel_not_found: 'Channel does not exist',
  user_not_found: 'User does not exist',
  is_archived: 'Channel has been archived',
  msg_too_long: 'Message text is too long',
  rate_limited: 'Rate limit exceeded',
  fatal_error: 'Server error',
};

function handleSlackError(response: { ok: false; error: string }): never {
  throw {
    code: `SLACK_${response.error}`,
    message: SLACK_ERROR_CODES[response.error] || response.error,
    retryable: response.error === 'rate_limited' || response.error === 'fatal_error',
  };
}
```

## Webhook Verification

Verify incoming webhooks:

```typescript
import crypto from 'crypto';

function verifySlackRequest(
  body: string,
  timestamp: string,
  signature: string,
  signingSecret: string
): boolean {
  // Check timestamp to prevent replay attacks
  const time = Math.floor(Date.now() / 1000);
  if (Math.abs(time - parseInt(timestamp)) > 300) {
    return false;
  }
  
  const sigBasestring = `v0:${timestamp}:${body}`;
  const mySignature = 'v0=' + crypto
    .createHmac('sha256', signingSecret)
    .update(sigBasestring)
    .digest('hex');
  
  return crypto.timingSafeEqual(
    Buffer.from(mySignature),
    Buffer.from(signature)
  );
}
```
