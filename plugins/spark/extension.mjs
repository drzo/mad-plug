import { joinSession } from "@github/copilot-sdk/extension";
import { readFileSync, readdirSync } from "node:fs";
import { resolve, dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const skillDir = resolve(__dirname, "skills", "spark-app-template");
const stacksDir = join(skillDir, "stacks");
const refsDir = join(skillDir, "references");

const STACK_FILES = {
    "default-webapp": "default-webapp.md",
    "content-showcase": "content-showcase.md",
    "data-dashboard": "data-dashboard.md",
    "complex-application": "complex-application.md",
};

const REFERENCE_FILES = {
    "design-system": "design-system.md",
    "typography-pairings": "typography-pairings.md",
    "color-palettes": "color-palettes.md",
    "component-patterns": "component-patterns.md",
    "performance-checklist": "performance-checklist.md",
    "prd-template": "prd-template.md",
    "radix-migration-guide": "radix-migration-guide.md",
};

function readFile(path) {
    try {
        return readFileSync(path, "utf-8");
    } catch (e) {
        return `Error reading file: ${e.message}`;
    }
}

await joinSession({
    tools: [
        {
            name: "spark_get_stack",
            description: "Get the full stack specification for a web app complexity tier. Tiers: default-webapp, content-showcase, data-dashboard, complex-application",
            parameters: {
                type: "object",
                properties: {
                    stack: {
                        type: "string",
                        description: "Stack tier: 'default-webapp', 'content-showcase', 'data-dashboard', or 'complex-application'",
                    },
                },
                required: ["stack"],
            },
            handler: async (args) => {
                const filename = STACK_FILES[args.stack];
                if (!filename) {
                    const available = Object.keys(STACK_FILES).join(", ");
                    return `Unknown stack '${args.stack}'. Available: ${available}`;
                }
                return readFile(join(stacksDir, filename));
            },
        },
        {
            name: "spark_list_stacks",
            description: "List all available Spark stack variations with brief descriptions",
            parameters: {
                type: "object",
                properties: {},
                required: [],
            },
            handler: async () => {
                const lines = [
                    "# Available Spark Stacks\n",
                    "| Stack | Use Case |",
                    "|---|---|",
                    "| `default-webapp` | General-purpose tools, utilities, MVPs, prototypes |",
                    "| `content-showcase` | Marketing sites, portfolios, blogs, documentation |",
                    "| `data-dashboard` | Analytics dashboards, admin panels, BI tools |",
                    "| `complex-application` | SaaS platforms, enterprise tools, multi-view apps |",
                    "",
                    "Use `spark_get_stack(stack=\"<name>\")` to retrieve the full specification for any tier.",
                ];
                return lines.join("\n");
            },
        },
        {
            name: "spark_get_reference",
            description: "Retrieve a Spark reference document. Available: design-system, typography-pairings, color-palettes, component-patterns, performance-checklist, prd-template, radix-migration-guide",
            parameters: {
                type: "object",
                properties: {
                    reference: {
                        type: "string",
                        description: "Reference name: 'design-system', 'typography-pairings', 'color-palettes', 'component-patterns', 'performance-checklist', 'prd-template', 'radix-migration-guide'",
                    },
                },
                required: ["reference"],
            },
            handler: async (args) => {
                const filename = REFERENCE_FILES[args.reference];
                if (!filename) {
                    const available = Object.keys(REFERENCE_FILES).join(", ");
                    return `Unknown reference '${args.reference}'. Available: ${available}`;
                }
                return readFile(join(refsDir, filename));
            },
        },
    ],
});
