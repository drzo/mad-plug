import { joinSession } from "@github/copilot-sdk/extension";
import { execFile } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const scriptsDir = resolve(repoRoot, "scripts");
const generatorsDir = resolve(repoRoot, "generators");

function runScript(dir, script, args = []) {
    return new Promise((resolvePromise, reject) => {
        const isWindows = process.platform === "win32";
        const python = isWindows ? "python" : "python3";
        execFile(python, [resolve(dir, script), ...args], {
            cwd: repoRoot,
            timeout: 30000,
        }, (err, stdout, stderr) => {
            if (err) reject(new Error(stderr || err.message));
            else resolvePromise(stdout || stderr);
        });
    });
}

await joinSession({
    tools: [
        {
            name: "dsl_init_language",
            description: "Initialize a new language project with standard directory structure (LANG.md + directories)",
            parameters: {
                type: "object",
                properties: {
                    name: { type: "string", description: "Name for the new language" },
                    output: { type: "string", description: "Output directory" },
                },
                required: ["name"],
            },
            handler: async (args) => {
                const cmdArgs = [args.name];
                if (args.output) cmdArgs.push("--output", args.output);
                try {
                    return await runScript(generatorsDir, "init_language.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "dsl_define_grammar",
            description: "Define a grammar using prime grammar specifications",
            parameters: {
                type: "object",
                properties: {
                    spec: { type: "string", description: "Grammar specification or path to spec file" },
                    output: { type: "string", description: "Output path for grammar definition" },
                },
                required: ["spec"],
            },
            handler: async (args) => {
                const cmdArgs = [args.spec];
                if (args.output) cmdArgs.push("--output", args.output);
                try {
                    return await runScript(scriptsDir, "define_prime_grammar.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "dsl_emit_grammar",
            description: "Emit grammar files from a grammar specification",
            parameters: {
                type: "object",
                properties: {
                    spec_path: { type: "string", description: "Path to the grammar specification" },
                    format: { type: "string", description: "Output format (e.g., 'peg', 'bnf', 'antlr')" },
                },
                required: ["spec_path"],
            },
            handler: async (args) => {
                const cmdArgs = [args.spec_path];
                if (args.format) cmdArgs.push("--format", args.format);
                try {
                    return await runScript(scriptsDir, "emit_grammar.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "dsl_extract_lexicon",
            description: "Extract lexicon/terminology from existing text corpora or documentation",
            parameters: {
                type: "object",
                properties: {
                    source: { type: "string", description: "Path to source text or corpus" },
                    output: { type: "string", description: "Output path for the extracted lexicon" },
                },
                required: ["source"],
            },
            handler: async (args) => {
                const cmdArgs = [args.source];
                if (args.output) cmdArgs.push("--output", args.output);
                try {
                    return await runScript(generatorsDir, "extract_lexicon.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "dsl_validate",
            description: "Validate a language project for completeness and correctness",
            parameters: {
                type: "object",
                properties: {
                    project_path: { type: "string", description: "Path to the language project directory" },
                },
                required: ["project_path"],
            },
            handler: async (args) => {
                try {
                    return await runScript(generatorsDir, "quick_validate.py", [args.project_path]);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
    ],
});
