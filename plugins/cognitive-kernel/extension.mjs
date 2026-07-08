import { joinSession } from "@github/copilot-sdk/extension";
import { execFile, exec } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const scriptsDir = resolve(repoRoot, "scripts");

function runPython(script, args = []) {
    return new Promise((resolvePromise, reject) => {
        const isWindows = process.platform === "win32";
        const python = isWindows ? "python" : "python3";
        execFile(python, [resolve(scriptsDir, script), ...args], {
            cwd: repoRoot,
            timeout: 60000,
        }, (err, stdout, stderr) => {
            if (err) reject(new Error(stderr || err.message));
            else resolvePromise(stdout || stderr);
        });
    });
}

function runShell(script, args = []) {
    return new Promise((resolvePromise, reject) => {
        const isWindows = process.platform === "win32";
        const scriptPath = resolve(scriptsDir, script);
        const cmd = isWindows
            ? `bash "${scriptPath}" ${args.join(" ")}`
            : `"${scriptPath}" ${args.join(" ")}`;
        exec(cmd, { cwd: repoRoot, timeout: 60000 }, (err, stdout, stderr) => {
            if (err) reject(new Error(stderr || err.message));
            else resolvePromise(stdout || stderr);
        });
    });
}

await joinSession({
    tools: [
        {
            name: "cogkernel_build",
            description: "Build a cognitive development kernel (Plan 9 or Inferno-OS based)",
            parameters: {
                type: "object",
                properties: {
                    type: { type: "string", description: "Kernel type: 'plan9' or 'inferno'" },
                    config: { type: "string", description: "Configuration file or options" },
                },
                required: ["type"],
            },
            handler: async (args) => {
                const script = args.type === "plan9" ? "cognitive_plan9kernel.py" : "cognitive_devkernel.py";
                const cmdArgs = args.config ? [args.config] : [];
                try {
                    return await runPython(script, cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "cogkernel_distributed_inference",
            description: "Configure and run distributed inference across compute nodes",
            parameters: {
                type: "object",
                properties: {
                    command: { type: "string", description: "Command: 'setup', 'run', 'status', 'stop'" },
                    nodes: { type: "string", description: "Comma-separated node addresses" },
                    model: { type: "string", description: "Model to distribute" },
                },
                required: ["command"],
            },
            handler: async (args) => {
                const cmdArgs = [args.command];
                if (args.nodes) cmdArgs.push("--nodes", args.nodes);
                if (args.model) cmdArgs.push("--model", args.model);
                try {
                    return await runPython("distributed_inference.py", cmdArgs);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "cogkernel_cluster",
            description: "Configure and monitor compute clusters for cognitive kernels",
            parameters: {
                type: "object",
                properties: {
                    action: { type: "string", description: "Action: 'configure', 'monitor', 'status'" },
                    config: { type: "string", description: "Cluster configuration file or JSON" },
                },
                required: ["action"],
            },
            handler: async (args) => {
                const script = args.action === "monitor" ? "cluster_monitor.py" : "configure_cluster.py";
                const cmdArgs = args.action === "monitor" ? [] : [args.config || ""];
                try {
                    return await runPython(script, cmdArgs.filter(Boolean));
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
        {
            name: "cogkernel_daemon",
            description: "Manage cognitive service daemons (PIE-NN and others)",
            parameters: {
                type: "object",
                properties: {
                    action: { type: "string", description: "Action: 'start', 'stop', 'test', 'status'" },
                    daemon: { type: "string", description: "Daemon name (default: pie_nn)" },
                },
                required: ["action"],
            },
            handler: async (args) => {
                if (args.action === "test") {
                    try {
                        return await runPython("test_daemon.py", [args.daemon || "pie_nn"]);
                    } catch (e) {
                        return `Error: ${e.message}`;
                    }
                }
                if (args.action === "start") {
                    try {
                        return await runShell("run_daemon.sh", [args.daemon || "pie_nn"]);
                    } catch (e) {
                        return `Error: ${e.message}`;
                    }
                }
                try {
                    return await runPython("pie_nn_daemon.py", [args.action]);
                } catch (e) {
                    return `Error: ${e.message}`;
                }
            },
        },
    ],
});
