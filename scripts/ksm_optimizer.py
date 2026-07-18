#!/usr/bin/env python3
"""
KSM Optimizer — runs the Knowledge Sharing Mechanism 12-step nested iteration
cycles over the mad-plug marketplace, guided by Alexander metrics.

The engine implements the dual-loop process documented in
plugins/unicorn-dynamics/skills/SKILL.md:

  Outer Loop (Solution Cycle — steps 1-3, 10-12) operates on the whole
  marketplace; the Inner Loop (Iteration Cycle — steps 4-9) strengthens one
  chosen critical centre (plugin) per iteration.

Modes:
  report   Score the marketplace and rank the weakest (latent) centres.
  plan     Emit ordered remediation actions per KSM step, per centre.
  apply    Execute safe automated remediations (registry sync, shim
           creation, metadata normalization); content-quality items are
           left as recommendations.

Usage:
  python3 scripts/ksm_optimizer.py report [n]
  python3 scripts/ksm_optimizer.py plan [n]
  python3 scripts/ksm_optimizer.py apply [n]
  python3 scripts/ksm_optimizer.py cycle <mode> [--history <file>]

`n` limits the number of centres worked in the inner loop (default 5).
`cycle` runs one full outer loop and appends the wholeness trajectory to the
history file so convergence is visible across cycles.

See references/ksm-optimization.md for the step-to-phase mapping.
"""

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import alexander_metrics as am

REPO_ROOT = am.REPO_ROOT
PLUGINS_DIR = am.PLUGINS_DIR
EXTENSIONS_DIR = am.EXTENSIONS_DIR

# Which structural checks the apply mode may remediate automatically.
# Everything else becomes a recommendation for a human/agent to strengthen.
SAFE_REMEDIATIONS = {
    "file:shim": "create-shim",
    "registry:marketplace-index": "index-sync",
    "json:dependencies-declared": "declare-dependencies",
    "registry:category-consistent": "registry-category-sync",
}

# Structure-preserving transformation applied by each remediation, per the
# fifteen-property mapping in references/alexander-metrics.md.
TRANSFORMATION_OF = {
    "file:shim": "not-separateness",
    "registry:marketplace-index": "not-separateness",
    "registry:marketplace-json": "not-separateness",
    "registry:category-consistent": "not-separateness",
    "json:dependencies-declared": "boundaries",
    "json:tools-match-extension": "local-symmetries",
    "ext:handlers-try-catch": "good-shape",
    "ext:join-session": "strong-centers",
}


def now_iso():
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


# ---------------------------------------------------------------------------
# Outer loop steps 1-3: analyze, differentiate, choose critical centres
# ---------------------------------------------------------------------------

def analyze_wholeness():
    """Step 1 — Analyze Problem in Space and Time: full metrics snapshot."""
    return am.scan_marketplace()


def differentiate_centres(report):
    """Step 2 — Differentiate Tasks into Centres: group deficiencies."""
    centres = []
    for r in report["plugins"]:
        deficiencies = list(r["failing_checks"])
        if not deficiencies and not r["weak_properties"]:
            continue
        centres.append({
            "plugin": r["plugin"],
            "wholeness": r["wholeness"],
            "deficiencies": deficiencies,
            "weak_properties": r["weak_properties"],
            # Leverage: latent centres are weak but repairable — more failing
            # checks means more strengthening potential per iteration.
            "leverage": len(deficiencies) + 0.25 * len(r["weak_properties"]),
        })
    return centres


def choose_critical_centres(centres, limit):
    """Step 3 — Choose Critical Centre(s): weakest first, leverage breaks ties."""
    return sorted(centres, key=lambda c: (c["wholeness"], -c["leverage"]))[:limit]


# ---------------------------------------------------------------------------
# Inner loop steps 4-9: constraints, sub-tasks, strengthen, assess
# ---------------------------------------------------------------------------

def inner_loop_plan(centre, context):
    """Steps 4-8 — build the iteration plan for one centre."""
    name = centre["plugin"]
    meta = context["metas"].get(name, {})

    constraints = {  # Step 4 — Identify Constraints and Relationships
        "category": meta.get("category"),
        "dependencies": meta.get("dependencies") or [],
        "registered_in_marketplace": name in context["marketplace_names"],
        "registered_in_index": name in context["index_plugin_names"],
    }

    actions = []  # Step 5 — Differentiate Sub-Tasks to Centres
    for check in centre["deficiencies"]:
        actions.append({
            "check": check,
            "transformation": TRANSFORMATION_OF.get(check, "positive-space"),
            "automated": check in SAFE_REMEDIATIONS,
            "remediation": SAFE_REMEDIATIONS.get(check, "recommend-manual-strengthening"),
        })
    for prop in centre["weak_properties"]:
        actions.append({
            "check": f"property:{prop}",
            "transformation": prop,
            "automated": False,
            "remediation": "recommend-manual-strengthening",
        })

    return {
        "plugin": name,
        "step4_constraints": constraints,
        "step5_subtasks": actions,
    }


def apply_remediation(action, plugin_name):
    """Step 6 — Strengthen Centres: execute one safe remediation."""
    kind = action["remediation"]
    pdir = PLUGINS_DIR / plugin_name

    if kind == "create-shim":
        shim_dir = EXTENSIONS_DIR / plugin_name
        shim = shim_dir / "extension.mjs"
        if shim.exists():
            return "shim already present"
        shim_dir.mkdir(parents=True, exist_ok=True)
        shim.write_text(
            f'// Re-exports from plugins/{plugin_name} for auto-discovery\n'
            f'import "../../../plugins/{plugin_name}/extension.mjs";\n',
            encoding="utf-8",
        )
        return f"created {shim.relative_to(REPO_ROOT)}"

    if kind == "declare-dependencies":
        meta_path = pdir / "plugin.json"
        meta = am.load_json(meta_path)
        if meta is None:
            return "plugin.json unreadable — skipped"
        if isinstance(meta.get("dependencies"), list):
            return "dependencies already declared"
        meta["dependencies"] = []
        meta_path.write_text(json.dumps(meta, indent=2) + "\n", encoding="utf-8")
        return "declared empty dependencies list"

    if kind == "index-sync":
        index = am.load_json(am.MARKETPLACE_INDEX)
        meta = am.load_json(pdir / "plugin.json") or {}
        category = meta.get("category")
        if index is None or not category:
            return "cannot sync index — missing index or category"
        for cat in index.get("categories", []):
            if cat.get("id") == category:
                if plugin_name not in cat["plugins"]:
                    cat["plugins"].append(plugin_name)
                    cat["plugins"].sort()
                    am.MARKETPLACE_INDEX.write_text(
                        json.dumps(index, indent=2) + "\n", encoding="utf-8")
                    return f"added {plugin_name} to index category {category}"
                return "already indexed"
        return f"category {category} not found in index"

    if kind == "registry-category-sync":
        marketplace = am.load_json(am.MARKETPLACE_JSON)
        meta = am.load_json(pdir / "plugin.json") or {}
        if marketplace is None or not meta.get("category"):
            return "cannot sync registry — missing data"
        for entry in marketplace.get("plugins", []):
            if entry.get("name") == plugin_name:
                if entry.get("category") != meta["category"]:
                    entry["category"] = meta["category"]
                    am.MARKETPLACE_JSON.write_text(
                        json.dumps(marketplace, indent=2) + "\n", encoding="utf-8")
                    return "synced registry category from plugin.json"
                return "registry category already consistent"
        return "plugin missing from marketplace.json — add entry manually"

    return "no automated remediation — recommendation only"


def assess_iteration(plugin_name, before_wholeness):
    """Steps 7-9 — Compare / Simplify / Assess Iteration Vision: re-score."""
    context = am.build_context()
    result = am.score_plugin(PLUGINS_DIR / plugin_name, context)
    return {
        "plugin": plugin_name,
        "wholeness_before": before_wholeness,
        "wholeness_after": result["wholeness"],
        "improved": result["wholeness"] >= before_wholeness,
        "remaining_failing_checks": result["failing_checks"],
    }


# ---------------------------------------------------------------------------
# Outer loop steps 10-12: integrate, evaluate, assess solution vision
# ---------------------------------------------------------------------------

def run_cycle(mode="report", limit=5, history_path=None):
    snapshot = analyze_wholeness()                       # step 1
    centres = differentiate_centres(snapshot)            # step 2
    critical = choose_critical_centres(centres, limit)   # step 3
    context = am.build_context()

    cycle = {
        "timestamp": now_iso(),
        "mode": mode,
        "step1_marketplace_wholeness": snapshot["marketplace_wholeness"],
        "step2_centres_with_deficiencies": len(centres),
        "step3_critical_centres": [c["plugin"] for c in critical],
        "inner_loops": [],
    }

    for centre in critical:                              # steps 4-9 per centre
        plan = inner_loop_plan(centre, context)
        if mode == "apply":
            plan["step6_applied"] = []
            for action in plan["step5_subtasks"]:
                if action["automated"]:
                    outcome = apply_remediation(action, centre["plugin"])
                    plan["step6_applied"].append(
                        {"check": action["check"], "outcome": outcome})
            plan["step7_9_assessment"] = assess_iteration(
                centre["plugin"], centre["wholeness"])
        cycle["inner_loops"].append(plan)

    if mode == "apply":                                  # steps 10-12
        final = analyze_wholeness()
        cycle["step10_wholeness_after"] = final["marketplace_wholeness"]
        cycle["step11_improved"] = (
            final["marketplace_wholeness"] >= cycle["step1_marketplace_wholeness"])
        cycle["step12_feedback"] = (
            "wholeness increased — continue to next cycle"
            if final["marketplace_wholeness"] > cycle["step1_marketplace_wholeness"]
            else "wholeness stable — remaining deficiencies need manual strengthening")

    if history_path:
        history_file = Path(history_path)
        history = []
        if history_file.exists():
            try:
                history = json.loads(history_file.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                history = []
        history.append({
            "timestamp": cycle["timestamp"],
            "mode": mode,
            "wholeness_before": cycle["step1_marketplace_wholeness"],
            "wholeness_after": cycle.get("step10_wholeness_after",
                                         cycle["step1_marketplace_wholeness"]),
        })
        history_file.write_text(json.dumps(history, indent=2) + "\n", encoding="utf-8")

    return cycle


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_report(cycle):
    print(f"KSM cycle [{cycle['mode']}] @ {cycle['timestamp']}")
    print(f"  Step 1  marketplace wholeness: {cycle['step1_marketplace_wholeness']:.4f}")
    print(f"  Step 2  centres with deficiencies: {cycle['step2_centres_with_deficiencies']}")
    print(f"  Step 3  critical centres: {', '.join(cycle['step3_critical_centres']) or 'none'}")
    for loop in cycle["inner_loops"]:
        print(f"\n  Inner loop — {loop['plugin']}")
        print(f"    Step 4  constraints: category={loop['step4_constraints']['category']}, "
              f"deps={loop['step4_constraints']['dependencies']}")
        for a in loop["step5_subtasks"]:
            marker = "AUTO" if a["automated"] else "recommend"
            print(f"    Step 5  [{marker:>9}] {a['check']} "
                  f"(transformation: {a['transformation']})")
        for applied in loop.get("step6_applied", []):
            print(f"    Step 6  applied {applied['check']}: {applied['outcome']}")
        if "step7_9_assessment" in loop:
            a = loop["step7_9_assessment"]
            print(f"    Steps 7-9  W {a['wholeness_before']:.4f} -> "
                  f"{a['wholeness_after']:.4f} "
                  f"({'improved' if a['improved'] else 'regressed'})")
    if "step10_wholeness_after" in cycle:
        print(f"\n  Steps 10-12  W(total) {cycle['step1_marketplace_wholeness']:.4f} -> "
              f"{cycle['step10_wholeness_after']:.4f}: {cycle['step12_feedback']}")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]

    history = None
    if "--history" in argv:
        history = argv[argv.index("--history") + 1]

    if cmd in ("report", "plan", "apply"):
        positional = [a for a in argv[2:] if not a.startswith("--") and a != history]
        limit = int(positional[0]) if positional and positional[0].isdigit() else 5
        cycle = run_cycle(mode=cmd, limit=limit, history_path=history)
        if "--json" in argv:
            print(json.dumps(cycle, indent=2))
        else:
            print_report(cycle)
        return 0

    if cmd == "cycle" and len(argv) >= 3 and argv[2] in ("report", "plan", "apply"):
        cycle = run_cycle(mode=argv[2], limit=5, history_path=history)
        print_report(cycle)
        return 0

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
