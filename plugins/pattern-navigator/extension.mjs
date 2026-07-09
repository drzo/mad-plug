import { joinSession } from "@github/copilot-sdk/extension";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { runPythonScript } from "../_shared/procRunner.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const scriptsDir = resolve(repoRoot, "scripts");

function runScript(script, args = []) {
    return runPythonScript(repoRoot, resolve(scriptsDir, script), args, 30000);
}

await joinSession({
    tools: [
        {
            name: "pattern_query",
            description: "Query the APL253 pattern topology by ID, search term, or relationship. Commands: get <id>, search <term>, broader <id>, narrower <id>, roots, hubs, path <from> <to>",
            parameters: {
                type: "object",
                properties: {
                    command: { type: "string", description: "Command to execute: get, search, broader, narrower, roots, hubs, path" },
                    args: { type: "string", description: "Arguments for the command (e.g., pattern ID or search term)" },
                },
                required: ["command"],
            },
            handler: async (args) => {
                const cmdArgs = [args.command];
                if (args.args) cmdArgs.push(...args.args.split(/\s+/));
                try {
                    return await runScript("query_patterns.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "pattern_transform",
            description: "Transform patterns across domain boundaries — map APL patterns to GitHub/software domains",
            parameters: {
                type: "object",
                properties: {
                    pattern_id: { type: "string", description: "Pattern ID to transform" },
                    target_domain: { type: "string", description: "Target domain (e.g., 'github', 'software')" },
                },
                required: ["pattern_id"],
            },
            handler: async (args) => {
                const cmdArgs = [args.pattern_id];
                if (args.target_domain) cmdArgs.push(args.target_domain);
                try {
                    return await runScript("transform_patterns.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "pattern_relationships",
            description: "Build and explore relationships between patterns to discover connected design decisions",
            parameters: {
                type: "object",
                properties: {
                    pattern_id: { type: "string", description: "Pattern ID to explore relationships for" },
                    depth: { type: "string", description: "Depth of relationship traversal (default: 1)" },
                },
                required: ["pattern_id"],
            },
            handler: async (args) => {
                const cmdArgs = [args.pattern_id];
                if (args.depth) cmdArgs.push("--depth", args.depth);
                try {
                    return await runScript("build_relationships.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
    ],
});
