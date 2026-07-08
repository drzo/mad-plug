import { joinSession } from "@github/copilot-sdk/extension";
import { exec } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const scriptsDir = resolve(repoRoot, "scripts");

function runShell(script, args = []) {
    return new Promise((resolvePromise, reject) => {
        const isWindows = process.platform === "win32";
        const scriptPath = resolve(scriptsDir, script);
        const cmd = isWindows
            ? `bash "${scriptPath}" ${args.join(" ")}`
            : `"${scriptPath}" ${args.join(" ")}`;
        exec(cmd, { cwd: repoRoot, timeout: 30000 }, (err, stdout, stderr) => {
            if (err) reject(new Error(stderr || err.message));
            else resolvePromise(stdout || stderr);
        });
    });
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
