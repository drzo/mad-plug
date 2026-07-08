import { joinSession } from "@github/copilot-sdk/extension";
import { execFile } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const scriptsDir = resolve(repoRoot, "scripts");

function runScript(script, args = []) {
    return new Promise((resolve, reject) => {
        const isWindows = process.platform === "win32";
        const python = isWindows ? "python" : "python3";
        execFile(python, [resolve(scriptsDir, script), ...args], {
            cwd: repoRoot,
            timeout: 30000,
        }, (err, stdout, stderr) => {
            if (err) reject(new Error(stderr || err.message));
            else resolve(stdout || stderr);
        });
    });
}

await joinSession({
    tools: [
        {
            name: "skill_decompose",
            description: "Decompose a skill into its abstract template and domain-specific bindings. Outputs template_manifest.yaml and domain_bindings.yaml.",
            parameters: {
                type: "object",
                properties: {
                    skill_path: { type: "string", description: "Path to the skill directory (must contain SKILL.md)" },
                    output: { type: "string", description: "Output directory for the template manifest" },
                },
                required: ["skill_path"],
            },
            handler: async (args) => {
                const cmdArgs = [args.skill_path];
                if (args.output) cmdArgs.push("--output", args.output);
                try {
                    return await runScript("decompose_skill.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "skill_transform",
            description: "Transform a skill from one domain to another using structural analogy",
            parameters: {
                type: "object",
                properties: {
                    template_path: { type: "string", description: "Path to the template manifest YAML" },
                    target_domain: { type: "string", description: "Target domain for the transformation" },
                    output: { type: "string", description: "Output path for the transformed skill" },
                },
                required: ["template_path", "target_domain"],
            },
            handler: async (args) => {
                const cmdArgs = [args.template_path, args.target_domain];
                if (args.output) cmdArgs.push("--output", args.output);
                try {
                    return await runScript("transform_skill.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "skill_chain_transforms",
            description: "Chain multiple transformations for multi-hop domain transfer",
            parameters: {
                type: "object",
                properties: {
                    skill_path: { type: "string", description: "Path to the source skill" },
                    domains: { type: "string", description: "Comma-separated list of domains to chain through" },
                },
                required: ["skill_path", "domains"],
            },
            handler: async (args) => {
                try {
                    return await runScript("chain_transforms.py", [args.skill_path, args.domains]);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "skill_apply_grt",
            description: "Apply the General Relevance Transform to map skill patterns to new contexts",
            parameters: {
                type: "object",
                properties: {
                    source: { type: "string", description: "Source skill or pattern" },
                    target_context: { type: "string", description: "Target context for the GRT mapping" },
                },
                required: ["source", "target_context"],
            },
            handler: async (args) => {
                try {
                    return await runScript("apply_grt.py", [args.source, args.target_context]);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "skill_share_template",
            description: "Share a skill template as a reusable scaffold",
            parameters: {
                type: "object",
                properties: {
                    template_path: { type: "string", description: "Path to the template to share" },
                    name: { type: "string", description: "Name for the shared template" },
                },
                required: ["template_path"],
            },
            handler: async (args) => {
                const cmdArgs = [args.template_path];
                if (args.name) cmdArgs.push("--name", args.name);
                try {
                    return await runScript("share_template.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
    ],
});
