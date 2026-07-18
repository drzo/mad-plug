import { joinSession } from "@github/copilot-sdk/extension";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { runPythonScript } from "../_shared/procRunner.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const scriptsDir = resolve(repoRoot, "scripts");

function runScript(script, args = []) {
    return runPythonScript(repoRoot, resolve(scriptsDir, script), args, 60000);
}

await joinSession({
    tools: [
        {
            name: "alexander_score",
            description: "Score one plugin or the whole marketplace against Alexander metrics (structural conformance, the 15 structure-preserving properties, and gh253 topology connectivity). Returns wholeness scores W(plugin) / W(total) with per-metric breakdown.",
            parameters: {
                type: "object",
                properties: {
                    plugin: { type: "string", description: "Plugin name to score; omit to scan the whole marketplace" },
                    format: { type: "string", description: "Output format for full scans: 'summary' (default) or 'json'" },
                },
                required: [],
            },
            handler: async (args) => {
                try {
                    if (args.plugin) {
                        return await runScript("alexander_metrics.py", ["score", args.plugin]);
                    }
                    const cmdArgs = ["scan"];
                    if (args.format === "json") cmdArgs.push("--json");
                    return await runScript("alexander_metrics.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "ksm_cycle_run",
            description: "Run one KSM outer-loop cycle (12-step nested iteration) over the marketplace. Modes: 'report' (rank weakest centres), 'plan' (emit ordered remediation actions per KSM step), 'apply' (execute safe automated remediations: registry sync, shim creation, metadata normalization).",
            parameters: {
                type: "object",
                properties: {
                    mode: { type: "string", description: "Cycle mode: report, plan, or apply" },
                    limit: { type: "string", description: "Max number of critical centres to work in the inner loop (default 5)" },
                },
                required: ["mode"],
            },
            handler: async (args) => {
                const cmdArgs = [args.mode];
                if (args.limit) cmdArgs.push(args.limit);
                try {
                    return await runScript("ksm_optimizer.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "optimization_report",
            description: "Report the weakest-centre ranking (latent centres for the next KSM cycle) and current marketplace wholeness trajectory.",
            parameters: {
                type: "object",
                properties: {
                    count: { type: "string", description: "Number of weakest centres to list (default 10)" },
                },
                required: [],
            },
            handler: async (args) => {
                const cmdArgs = ["weakest"];
                if (args.count) cmdArgs.push(args.count);
                try {
                    return await runScript("alexander_metrics.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
    ],
});
