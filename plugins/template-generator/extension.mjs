import { joinSession } from "@github/copilot-sdk/extension";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { runShellScript } from "../_shared/procRunner.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const scriptsDir = resolve(repoRoot, "scripts");

function runShell(script, args = []) {
    return runShellScript(repoRoot, resolve(scriptsDir, script), args, 30000);
}

await joinSession({
    tools: [
        {
            name: "template_new_skill",
            description: "Scaffold a new skill with proper frontmatter, directory structure, and placeholder content",
            parameters: {
                type: "object",
                properties: {
                    name: { type: "string", description: "Name for the new skill" },
                    description: { type: "string", description: "Short description of the skill" },
                    output: { type: "string", description: "Output directory (optional)" },
                },
                required: ["name"],
            },
            handler: async (args) => {
                const cmdArgs = [args.name];
                if (args.description) cmdArgs.push(args.description);
                if (args.output) cmdArgs.push(args.output);
                try {
                    return await runShell("new-skill.sh", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "template_new_extension",
            description: "Scaffold a new extension with the standard extension layout",
            parameters: {
                type: "object",
                properties: {
                    name: { type: "string", description: "Name for the new extension" },
                    description: { type: "string", description: "Short description of the extension" },
                },
                required: ["name"],
            },
            handler: async (args) => {
                const cmdArgs = [args.name];
                if (args.description) cmdArgs.push(args.description);
                try {
                    return await runShell("new-extension.sh", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
    ],
});
