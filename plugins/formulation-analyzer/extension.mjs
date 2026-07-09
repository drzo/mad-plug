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
            name: "formulation_analyze",
            description: "Analyze a skincare formulation for compatibility, safety, and optimization opportunities",
            parameters: {
                type: "object",
                properties: {
                    file: { type: "string", description: "Path to the formulation file (.form or JSON)" },
                },
                required: ["file"],
            },
            handler: async (args) => {
                try {
                    return await runScript("analyze_formulation.py", [args.file]);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "formulation_optimize",
            description: "Optimize a formulation using neural hypergraph embeddings for maximum efficacy",
            parameters: {
                type: "object",
                properties: {
                    file: { type: "string", description: "Path to the formulation file" },
                    target: { type: "string", description: "Optimization target (e.g., 'stability', 'absorption', 'efficacy')" },
                },
                required: ["file"],
            },
            handler: async (args) => {
                const cmdArgs = [args.file];
                if (args.target) cmdArgs.push("--target", args.target);
                try {
                    return await runScript("skinform_optim.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "formulation_lookup_ingredient",
            description: "Look up ingredient properties, safety data, and compatibility information",
            parameters: {
                type: "object",
                properties: {
                    ingredient: { type: "string", description: "Ingredient name (e.g., 'niacinamide', 'retinol')" },
                },
                required: ["ingredient"],
            },
            handler: async (args) => {
                try {
                    return await runScript("lookup_ingredient.py", [args.ingredient]);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "formulation_generate_topology",
            description: "Generate a neural network topology specification",
            parameters: {
                type: "object",
                properties: {
                    type: { type: "string", description: "Topology type (e.g., 'feedforward', 'recurrent', 'transformer')" },
                    layers: { type: "string", description: "Number of layers or layer spec" },
                    output: { type: "string", description: "Output path for the topology file" },
                },
                required: ["type"],
            },
            handler: async (args) => {
                const cmdArgs = [args.type];
                if (args.layers) cmdArgs.push("--layers", args.layers);
                if (args.output) cmdArgs.push("--output", args.output);
                try {
                    return await runScript("generate_topology.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "formulation_brain_model",
            description: "Generate and optionally visualize brain-inspired computational models",
            parameters: {
                type: "object",
                properties: {
                    model: { type: "string", description: "Model type or specification" },
                    visualize: { type: "boolean", description: "Whether to generate visualization" },
                    output: { type: "string", description: "Output path" },
                },
                required: ["model"],
            },
            handler: async (args) => {
                const cmdArgs = [args.model];
                if (args.output) cmdArgs.push("--output", args.output);
                try {
                    let result = await runScript("generate_brain_model.py", cmdArgs);
                    if (args.visualize) {
                        result += "\n" + await runScript("visualize_brain.py", [args.model]);
                    }
                    return result;
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "formulation_continued_fractions",
            description: "Compute and analyze continued fraction representations for numerical analysis",
            parameters: {
                type: "object",
                properties: {
                    value: { type: "string", description: "Number or expression to analyze" },
                    depth: { type: "string", description: "Maximum depth of continued fraction expansion" },
                },
                required: ["value"],
            },
            handler: async (args) => {
                const cmdArgs = [args.value];
                if (args.depth) cmdArgs.push("--depth", args.depth);
                try {
                    return await runScript("continued_fractions.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
    ],
});
