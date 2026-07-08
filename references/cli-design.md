# CLI Design Patterns

This reference covers patterns for building consistent, user-friendly CLI interfaces.

## Command Naming Conventions

Use `entity:action` format for consistency:

```
customer:create    # Create a customer
customer:get       # Get a single customer
customer:list      # List customers
customer:update    # Update a customer
customer:delete    # Delete a customer
customer:sync      # Sync customer between platforms

order:create
order:get
order:list
order:sync

invoice:create
invoice:send
invoice:void
```

**Naming rules:**
- Use lowercase with colons as separators
- Entity first, action second
- Use common verbs: create, get, list, update, delete, sync, send, void
- Avoid abbreviations unless universally understood

## Argument Parsing

Support multiple input styles:

```bash
# Long flags (preferred for clarity)
weaver customer:create --email "user@example.com" --name "John Doe"

# Short flags (for common options)
weaver customer:list -l 50 -f table

# Positional arguments (for primary identifiers)
weaver customer:get CUST_123

# Stdin for bulk operations
cat customers.json | weaver customer:import --format json

# Interactive prompts for missing required args
weaver customer:create
# > Email: user@example.com
# > Name: John Doe
```

**Implementation:**

```typescript
interface ArgDefinition {
  name: string;
  short?: string;
  type: 'string' | 'number' | 'boolean' | 'array';
  required?: boolean;
  default?: unknown;
  choices?: string[];
  description: string;
}

const COMMON_ARGS: ArgDefinition[] = [
  { name: 'format', short: 'f', type: 'string', default: 'json', choices: ['json', 'table', 'csv', 'raw'] },
  { name: 'limit', short: 'l', type: 'number', default: 50 },
  { name: 'cursor', short: 'c', type: 'string' },
  { name: 'platform', short: 'p', type: 'string' },
  { name: 'quiet', short: 'q', type: 'boolean', default: false },
  { name: 'verbose', short: 'v', type: 'boolean', default: false },
];
```

## Output Formatting

Support multiple output formats:

```typescript
type OutputFormat = 'json' | 'table' | 'csv' | 'raw';

function formatOutput(data: unknown, format: OutputFormat): string {
  switch (format) {
    case 'json':
      return JSON.stringify(data, null, 2);
    
    case 'table':
      return formatTable(data);
    
    case 'csv':
      return formatCsv(data);
    
    case 'raw':
      return String(data);
  }
}

function formatTable(data: unknown): string {
  if (!Array.isArray(data) || data.length === 0) {
    return 'No results';
  }
  
  const headers = Object.keys(data[0]);
  const rows = data.map(item => headers.map(h => String(item[h] ?? '')));
  
  // Calculate column widths
  const widths = headers.map((h, i) => 
    Math.max(h.length, ...rows.map(r => r[i].length))
  );
  
  // Build table
  const headerLine = headers.map((h, i) => h.padEnd(widths[i])).join(' │ ');
  const separator = widths.map(w => '─'.repeat(w)).join('─┼─');
  const dataLines = rows.map(r => 
    r.map((c, i) => c.padEnd(widths[i])).join(' │ ')
  ).join('\n');
  
  return `${headerLine}\n${separator}\n${dataLines}`;
}

function formatCsv(data: unknown): string {
  if (!Array.isArray(data) || data.length === 0) {
    return '';
  }
  
  const headers = Object.keys(data[0]);
  const rows = data.map(item => 
    headers.map(h => {
      const value = String(item[h] ?? '');
      return value.includes(',') ? `"${value}"` : value;
    }).join(',')
  );
  
  return [headers.join(','), ...rows].join('\n');
}
```

## Interactive Prompts

Prompt for missing required arguments:

```typescript
import * as readline from 'readline';

async function prompt(question: string, options?: {
  default?: string;
  choices?: string[];
  password?: boolean;
}): Promise<string> {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout,
  });
  
  let displayQuestion = question;
  if (options?.default) {
    displayQuestion += ` [${options.default}]`;
  }
  if (options?.choices) {
    displayQuestion += ` (${options.choices.join('/')})`;
  }
  displayQuestion += ': ';
  
  return new Promise((resolve) => {
    rl.question(displayQuestion, (answer) => {
      rl.close();
      resolve(answer || options?.default || '');
    });
  });
}

async function promptForMissingArgs(
  args: Record<string, unknown>,
  definitions: ArgDefinition[]
): Promise<Record<string, unknown>> {
  const result = { ...args };
  
  for (const def of definitions) {
    if (def.required && !result[def.name]) {
      result[def.name] = await prompt(def.description, {
        choices: def.choices,
      });
    }
  }
  
  return result;
}
```

## Configuration Management

Support multiple configuration sources:

```typescript
interface Config {
  platforms: Record<string, PlatformConfig>;
  primaryPlatform: string;
  defaults: {
    format: OutputFormat;
    limit: number;
  };
}

function loadConfig(): Config {
  // Priority: CLI args > env vars > config file > defaults
  const defaults: Config = {
    platforms: {},
    primaryPlatform: 'shopify',
    defaults: { format: 'json', limit: 50 },
  };
  
  // Load from config file
  const configPaths = [
    './weaver.yaml',
    './config/weaver.yaml',
    `${process.env.HOME}/.weaver/config.yaml`,
  ];
  
  for (const path of configPaths) {
    if (fs.existsSync(path)) {
      const fileConfig = yaml.parse(fs.readFileSync(path, 'utf-8'));
      Object.assign(defaults, fileConfig);
      break;
    }
  }
  
  // Override with env vars
  if (process.env.WEAVER_PRIMARY_PLATFORM) {
    defaults.primaryPlatform = process.env.WEAVER_PRIMARY_PLATFORM;
  }
  
  return defaults;
}
```

## Progress and Status

Show progress for long operations:

```typescript
class ProgressIndicator {
  private interval?: NodeJS.Timeout;
  private frames = ['⠋', '⠙', '⠹', '⠸', '⠼', '⠴', '⠦', '⠧', '⠇', '⠏'];
  private frameIndex = 0;
  
  start(message: string): void {
    process.stdout.write(`${this.frames[0]} ${message}`);
    this.interval = setInterval(() => {
      this.frameIndex = (this.frameIndex + 1) % this.frames.length;
      process.stdout.write(`\r${this.frames[this.frameIndex]} ${message}`);
    }, 80);
  }
  
  stop(success: boolean, message?: string): void {
    if (this.interval) {
      clearInterval(this.interval);
    }
    const icon = success ? '✓' : '✗';
    process.stdout.write(`\r${icon} ${message || ''}\n`);
  }
}

// Usage
const progress = new ProgressIndicator();
progress.start('Creating customer...');
try {
  await client.customer_create({ email, name });
  progress.stop(true, 'Customer created');
} catch (error) {
  progress.stop(false, `Failed: ${error.message}`);
}
```

## Help and Documentation

Generate help from command definitions:

```typescript
function generateHelp(commands: Record<string, CommandDefinition>): string {
  let help = `
weaver - Unified multiplatform CLI

Usage:
  weaver <command> [options]

Commands:
`;
  
  for (const [name, def] of Object.entries(commands)) {
    help += `  ${name.padEnd(20)} ${def.description}\n`;
  }
  
  help += `
Global Options:
  --config <dir>       Configuration directory (default: ./config)
  --format <format>    Output format: json, table, csv, raw (default: json)
  --platform <name>    Target platform
  --quiet              Suppress non-essential output
  --verbose            Show detailed output
  --help               Show help for a command

Examples:
  weaver customer:create --email "user@example.com" --name "John Doe"
  weaver customer:list --format table --limit 10
  weaver order:sync --order-id ORD_123 --direction shopify_to_qb
`;
  
  return help;
}

function generateCommandHelp(name: string, def: CommandDefinition): string {
  let help = `
weaver ${name}

${def.description}

Usage:
  weaver ${name} [options]

Options:
`;
  
  for (const arg of def.args) {
    const required = arg.required ? '(required)' : '';
    const defaultVal = arg.default ? `(default: ${arg.default})` : '';
    help += `  --${arg.name.padEnd(15)} ${arg.description} ${required} ${defaultVal}\n`;
  }
  
  return help;
}
```
