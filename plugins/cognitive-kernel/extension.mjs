import { joinSession } from "@github/copilot-sdk/extension";
import { spawn } from "node:child_process";
import { resolve, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { runPythonScript, resolveBash } from "../_shared/procRunner.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(__dirname, "..", "..");
const scriptsDir = resolve(repoRoot, "scripts");

function runPython(script, args = []) {
    return runPythonScript(repoRoot, resolve(scriptsDir, script), args, 60000);
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
                    action: { type: "string", description: "Action: 'init', 'validate', 'status', 'monitor'" },
                    config: { type: "string", description: "Project directory (required for 'init'/'validate')" },
                },
                required: ["action"],
            },
            handler: async (args) => {
                if (args.action === "monitor") {
                    try {
                        return await runPython("cluster_monitor.py", []);
                    } catch (e) {
                        return `Error: ${e.message}`;
                    }
                }
                // configure_cluster.py expects: <subcommand> [project_path]
                // where the subcommand is init/validate/status.
                if ((args.action === "init" || args.action === "validate") && !args.config) {
                    return `Error: action "${args.action}" requires a "config" project directory path.`;
                }
                const cmdArgs = [args.action];
                if (args.config) cmdArgs.push(args.config);
                try {
                    return await runPython("configure_cluster.py", cmdArgs);
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
                    action: { type: "string", description: "Action: 'start', 'test', 'status'" },
                    daemon: { type: "string", description: "Daemon name (default: pie_nn)" },
                    socket: { type: "string", description: "UNIX socket path the daemon listens on (default: /tmp/tc_daemon.sock)" },
                },
                required: ["action"],
            },
            handler: async (args) => {
                const socketPath = args.socket || "/tmp/tc_daemon.sock";
                if (args.action === "test" || args.action === "status") {
                    // test_daemon.py exercises get_status/list_modules/diagnose/etc. against
                    // the running daemon's JSON-RPC socket, so it doubles as a status check.
                    try {
                        return await runPython("test_daemon.py", [socketPath]);
                    } catch (e) {
                        return `Error: ${e.message}`;
                    }
                }
                if (args.action === "start") {
                    // run_daemon.sh runs the daemon in the foreground ("Press Ctrl+C to
                    // stop"), so it must be launched detached rather than awaited —
                    // otherwise this call would block until the tool-call timeout.
                    try {
                        const bash = resolveBash();
                        const scriptPath = resolve(scriptsDir, "run_daemon.sh");
                        const child = spawn(bash, [scriptPath, socketPath], {
                            cwd: repoRoot,
                            detached: true,
                            stdio: "ignore",
                        });
                        child.unref();
                        return `Started daemon on socket ${socketPath} (pid ${child.pid}). Use action "status" to verify.`;
                    } catch (e) {
                        return `Error: ${e.message}`;
                    }
                }
                return `Error: unsupported action "${args.action}". Use 'start', 'test', or 'status'. There is no supported 'stop' action yet — terminate the daemon process directly.`;
            },
        },
    ],
});
