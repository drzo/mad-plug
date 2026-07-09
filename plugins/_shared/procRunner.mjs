// Shared process-resolution helpers for plugin extensions.
//
// Extension host processes are long-lived and may have been spawned before
// Python/Git were installed or before PATH was updated. Relying on a bare
// "python"/"bash" command can therefore resolve to a stale PATH entry (e.g.
// the Windows Store "python.exe" alias stub, which prints an install prompt
// and exits non-zero instead of running anything). These helpers search a
// set of well-known install locations in addition to PATH so tools keep
// working regardless of when the extension process itself was started.
import { execFile, exec } from "node:child_process";
import { existsSync, readdirSync } from "node:fs";
import { join } from "node:path";

let cachedPython;
let cachedBash;

function candidateDirs(...envVars) {
    return envVars.map((v) => process.env[v]).filter(Boolean);
}

export function resolvePython() {
    if (cachedPython) return cachedPython;

    const candidates = [];

    // Highest-priority: explicit override.
    if (process.env.COPILOT_PYTHON && existsSync(process.env.COPILOT_PYTHON)) {
        cachedPython = process.env.COPILOT_PYTHON;
        return cachedPython;
    }

    // Common per-user install locations on Windows.
    for (const base of candidateDirs("LOCALAPPDATA")) {
        const pyDir = join(base, "Programs", "Python");
        if (existsSync(pyDir)) {
            try {
                const versions = readdirSync(pyDir)
                    .filter((n) => /^Python3\d\d?$/.test(n))
                    .sort()
                    .reverse();
                for (const v of versions) {
                    candidates.push(join(pyDir, v, "python.exe"));
                }
            } catch {
                // ignore unreadable dir
            }
        }
    }

    // System-wide install locations.
    candidates.push(
        "C:\\Python312\\python.exe",
        "C:\\Python311\\python.exe",
        "C:\\Python310\\python.exe",
        "C:\\Program Files\\Python312\\python.exe",
        "C:\\Program Files\\Python311\\python.exe"
    );

    for (const c of candidates) {
        if (existsSync(c)) {
            cachedPython = c;
            return cachedPython;
        }
    }

    // Fall back to PATH lookup (non-Windows, or environments where PATH is correct).
    cachedPython = process.platform === "win32" ? "python" : "python3";
    return cachedPython;
}

export function resolveBash() {
    if (cachedBash) return cachedBash;

    const candidates = [
        "C:\\Program Files\\Git\\bin\\bash.exe",
        "C:\\Program Files (x86)\\Git\\bin\\bash.exe",
    ];
    for (const base of candidateDirs("LOCALAPPDATA", "ProgramFiles", "ProgramFiles(x86)")) {
        candidates.push(join(base, "Git", "bin", "bash.exe"));
    }

    for (const c of candidates) {
        if (existsSync(c)) {
            cachedBash = c;
            return cachedBash;
        }
    }

    cachedBash = "bash";
    return cachedBash;
}

export function runPythonScript(repoRoot, scriptPath, args = [], timeout = 30000) {
    return new Promise((resolvePromise, reject) => {
        const python = resolvePython();
        // Many scripts print unicode symbols (emoji, checkmarks). On Windows the
        // console defaults to a legacy codepage (cp1252) which can't encode them
        // and crashes with UnicodeEncodeError. Force UTF-8 I/O for the child.
        const env = { ...process.env, PYTHONIOENCODING: "utf-8", PYTHONUTF8: "1" };
        execFile(python, [scriptPath, ...args], { cwd: repoRoot, timeout, env }, (err, stdout, stderr) => {
            // Scripts often print their real diagnostics to stdout and only use a
            // non-zero exit code as the failure signal (e.g. validators reporting
            // "N errors found"). Surface stdout too so that output isn't discarded.
            if (err) reject(new Error(stderr || stdout || err.message));
            else resolvePromise(stdout || stderr);
        });
    });
}

export function runShellScript(repoRoot, scriptPath, args = [], timeout = 30000) {
    return new Promise((resolvePromise, reject) => {
        const isWindows = process.platform === "win32";
        const cmd = isWindows
            ? `"${resolveBash()}" "${scriptPath}" ${args.join(" ")}`
            : `"${scriptPath}" ${args.join(" ")}`;
        exec(cmd, { cwd: repoRoot, timeout }, (err, stdout, stderr) => {
            if (err) reject(new Error(stderr || stdout || err.message));
            else resolvePromise(stdout || stderr);
        });
    });
}
