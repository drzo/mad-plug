#!/usr/bin/env python3
"""
Alexander Metrics — marketplace wholeness scanner for mad-plug.

Treats every plugin as an Alexandrian "centre" and quantifies its degree of
life along three metric groups:

  1. structural   — conformance to AGENTS.md quality expectations
  2. fifteen      — Christopher Alexander's 15 structure-preserving properties
                    mapped to measurable marketplace analogues
  3. topology     — connectivity of the plugin's tags/category to the gh253
                    pattern graph (hub patterns and entry points)

Aggregates into a wholeness score W(plugin) in [0, 1] and a marketplace
wholeness W(total).

Usage:
  python3 scripts/alexander_metrics.py scan [--json]        Scan all plugins
  python3 scripts/alexander_metrics.py score <plugin>       Score one plugin
  python3 scripts/alexander_metrics.py weakest [n]          N weakest centres

See references/alexander-metrics.md for the full metric model.
"""

import json
import re
import sys
from pathlib import Path
from statistics import median

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGINS_DIR = REPO_ROOT / "plugins"
PATTERNS_DIR = REPO_ROOT / "patterns"
EXTENSIONS_DIR = REPO_ROOT / ".github" / "extensions"
MARKETPLACE_JSON = REPO_ROOT / "marketplace.json"
MARKETPLACE_INDEX = REPO_ROOT / "marketplace-index.json"

SEMVER_RE = re.compile(r"^\d+\.\d+\.\d+$")
KEBAB_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
SNAKE_RE = re.compile(r"^[a-z0-9]+(_[a-z0-9]+)*$")

REQUIRED_FILES = ["extension.mjs", "plugin.md", "plugin.json", "README.md"]
REQUIRED_PLUGIN_JSON_FIELDS = ["name", "version", "description", "category", "entrypoint"]
README_SECTIONS = ["description", "usage examples", "tools", "version", "dependencies", "category"]

# Metric group weights for the wholeness aggregate.
WEIGHTS = {"structural": 0.50, "fifteen": 0.35, "topology": 0.15}

FIFTEEN_PROPERTIES = [
    "levels-of-scale",
    "strong-centers",
    "boundaries",
    "alternating-repetition",
    "positive-space",
    "good-shape",
    "local-symmetries",
    "deep-interlock",
    "contrast",
    "gradients",
    "roughness",
    "echoes",
    "the-void",
    "simplicity-inner-calm",
    "not-separateness",
]


def load_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def read_text(path):
    try:
        return path.read_text(encoding="utf-8")
    except OSError:
        return ""


def list_plugin_dirs():
    if not PLUGINS_DIR.exists():
        return []
    return sorted(
        p for p in PLUGINS_DIR.iterdir()
        if p.is_dir() and not p.name.startswith("_") and not p.name.startswith(".")
    )


def registered_tool_names(extension_src):
    """Extract tool names registered in an extension.mjs source."""
    return re.findall(r'name:\s*["\']([a-z0-9_]+)["\']', extension_src)


def valid_categories():
    index = load_json(MARKETPLACE_INDEX) or {}
    return [c.get("id") for c in index.get("categories", [])]


# ---------------------------------------------------------------------------
# Group 1 — structural conformance (AGENTS.md quality expectations)
# ---------------------------------------------------------------------------

def structural_checks(plugin_dir, meta, extension_src, readme_src, context):
    name = plugin_dir.name
    checks = {}

    for f in REQUIRED_FILES:
        checks[f"file:{f}"] = (plugin_dir / f).is_file()
    checks["file:shim"] = (EXTENSIONS_DIR / name / "extension.mjs").is_file()

    checks["json:parses"] = meta is not None
    meta = meta or {}
    for field in REQUIRED_PLUGIN_JSON_FIELDS:
        checks[f"json:field:{field}"] = bool(meta.get(field))
    checks["json:name-matches-dir"] = meta.get("name") == name
    checks["json:semver"] = bool(SEMVER_RE.match(str(meta.get("version", ""))))
    desc = str(meta.get("description", ""))
    checks["json:description-length"] = 0 < len(desc) <= 160
    checks["json:category-valid"] = meta.get("category") in context["categories"]
    checks["json:dependencies-declared"] = isinstance(meta.get("dependencies"), list)

    declared_tools = set(meta.get("tools") or [])
    registered = set(registered_tool_names(extension_src))
    checks["json:tools-match-extension"] = bool(registered) and declared_tools == registered

    readme_lower = readme_src.lower()
    for section in README_SECTIONS:
        checks[f"readme:section:{section}"] = section in readme_lower

    checks["ext:join-session"] = "joinSession" in extension_src
    checks["ext:handlers-try-catch"] = (
        "runScript" not in extension_src and "runPython" not in extension_src
    ) or ("try {" in extension_src and "catch" in extension_src)
    checks["ext:tool-names-snake-case"] = bool(registered) and all(
        SNAKE_RE.match(t) for t in registered
    )

    checks["registry:marketplace-json"] = name in context["marketplace_names"]
    checks["registry:marketplace-index"] = name in context["index_plugin_names"]
    entry = context["marketplace_entries"].get(name, {})
    checks["registry:category-consistent"] = (
        entry.get("category") == meta.get("category") if entry else False
    )

    return checks


# ---------------------------------------------------------------------------
# Group 2 — the fifteen properties as marketplace metrics
# ---------------------------------------------------------------------------

def fifteen_property_scores(plugin_dir, meta, extension_src, structural, context):
    name = plugin_dir.name
    meta = meta or {}
    scores = {}

    # 1. Levels of Scale — artifacts exist at multiple granularities.
    granularities = [
        (plugin_dir / "plugin.md").is_file(),
        (plugin_dir / "README.md").is_file(),
        (plugin_dir / "skills").is_dir(),
        bool(meta.get("tools")),
    ]
    scores["levels-of-scale"] = sum(granularities) / len(granularities)

    # 2. Strong Centers — tool count relative to category median.
    tool_count = len(meta.get("tools") or [])
    cat_median = context["category_tool_median"].get(meta.get("category"), 1) or 1
    scores["strong-centers"] = min(1.0, tool_count / cat_median) if tool_count else 0.0

    # 3. Boundaries — dependency interface explicitly declared.
    scores["boundaries"] = 1.0 if isinstance(meta.get("dependencies"), list) else 0.0

    # 4. Alternating Repetition — structure consistent with category siblings.
    sibling_conf = context["category_structural_avg"].get(meta.get("category"))
    own_conf = sum(structural.values()) / len(structural)
    if sibling_conf:
        scores["alternating-repetition"] = max(0.0, 1.0 - abs(own_conf - sibling_conf))
    else:
        scores["alternating-repetition"] = own_conf

    # 5. Positive Space — no dead intra-plugin references in the README.
    readme = read_text(plugin_dir / "README.md")
    refs = re.findall(r"`((?:skills|scripts|references)/[\w./-]+)`", readme)
    if refs:
        alive = sum(
            1 for r in refs if (plugin_dir / r).exists() or (REPO_ROOT / r).exists()
        )
        scores["positive-space"] = alive / len(refs)
    else:
        scores["positive-space"] = 1.0

    # 6. Good Shape — description is a well-formed single sentence.
    desc = str(meta.get("description", ""))
    scores["good-shape"] = 1.0 if desc and len(desc) <= 160 and desc.count(". ") <= 1 else 0.5 if desc else 0.0

    # 7. Local Symmetries — naming conventions consistent at every level.
    registered = registered_tool_names(extension_src)
    naming = [bool(KEBAB_RE.match(name))] + [bool(SNAKE_RE.match(t)) for t in registered]
    scores["local-symmetries"] = sum(naming) / len(naming)

    # 8. Deep Interlock — participates in the dependency graph.
    deps = meta.get("dependencies") or []
    depended_upon = name in context["dependency_targets"]
    scores["deep-interlock"] = 1.0 if deps or depended_upon else 0.5

    # 9. Contrast — tag distinctiveness relative to category siblings.
    tags = set(meta.get("tags") or [])
    sibling_tags = context["category_tags"].get(meta.get("category"), set()) - tags
    if tags:
        unique = tags - sibling_tags
        scores["contrast"] = 0.5 + 0.5 * (len(unique) / len(tags))
    else:
        scores["contrast"] = 0.0

    # 10. Gradients — versioning follows the marketplace maturity gradient.
    version = str(meta.get("version", ""))
    scores["gradients"] = 1.0 if SEMVER_RE.match(version) else 0.0

    # 11. Roughness — optional enrichment tolerated, nothing forced.
    scores["roughness"] = 1.0  # optional dirs never penalized; presence is a bonus signal only

    # 12. Echoes — process execution reuses plugins/_shared, never copies it.
    spawns = re.search(r"child_process|execFile|spawn\(", extension_src)
    uses_shared = "_shared/procRunner.mjs" in extension_src
    scores["echoes"] = 1.0 if uses_shared or not spawns else 0.0

    # 13. The Void — no global mutable state across tool invocations.
    top_level_mutable = re.findall(r"^(?:let|var)\s+\w+", extension_src, re.MULTILINE)
    scores["the-void"] = 1.0 if not top_level_mutable else 0.0

    # 14. Simplicity and Inner Calm — the extension carries no excess weight.
    line_count = extension_src.count("\n") + 1 if extension_src else 0
    scores["simplicity-inner-calm"] = 1.0 if 0 < line_count <= 400 else 0.5 if line_count else 0.0

    # 15. Not-Separateness — woven into both registries and the pattern topology.
    parts = [
        structural.get("registry:marketplace-json", False),
        structural.get("registry:marketplace-index", False),
        bool(tags & context["index_tags"]),
    ]
    scores["not-separateness"] = sum(parts) / len(parts)

    return scores


# ---------------------------------------------------------------------------
# Group 3 — topology connectivity to the gh253 pattern graph
# ---------------------------------------------------------------------------

def pattern_slugs():
    slugs = []
    for cat in ("cat1-enterprises", "cat2-organisations", "cat3-repositories"):
        cat_dir = PATTERNS_DIR / cat
        if not cat_dir.exists():
            continue
        for f in cat_dir.glob("gh*-*.md"):
            slugs.append(f.stem.split("-", 1)[1])
    return slugs


def topology_scores(meta, context):
    meta = meta or {}
    tags = [t for t in (meta.get("tags") or [])]
    slugs = context["pattern_slugs"]
    if not slugs:
        return {"tag-pattern-connectivity": 0.0, "category-anchoring": 0.0}

    # How many tags surface somewhere in the 253-pattern slug space.
    if tags:
        hits = sum(1 for t in tags if any(t.replace("-", " ") in s.replace("-", " ") or t in s for s in slugs))
        tag_conn = hits / len(tags)
    else:
        tag_conn = 0.0

    # Category anchoring — plugin sits in a recognized category (which maps
    # onto the enterprise/organisation/repository scales of gh253).
    anchored = 1.0 if meta.get("category") in context["categories"] else 0.0
    return {"tag-pattern-connectivity": tag_conn, "category-anchoring": anchored}


# ---------------------------------------------------------------------------
# Aggregation
# ---------------------------------------------------------------------------

def build_context():
    marketplace = load_json(MARKETPLACE_JSON) or {}
    index = load_json(MARKETPLACE_INDEX) or {}

    entries = {p.get("name"): p for p in marketplace.get("plugins", [])}
    index_names = set()
    category_of = {}
    for cat in index.get("categories", []):
        for pname in cat.get("plugins", []):
            index_names.add(pname)
            category_of[pname] = cat.get("id")

    metas = {}
    structural_conf = {}
    tool_counts = {}
    cat_tags = {}
    dep_targets = set()
    for pdir in list_plugin_dirs():
        meta = load_json(pdir / "plugin.json") or {}
        metas[pdir.name] = meta
        tool_counts.setdefault(meta.get("category"), []).append(len(meta.get("tools") or []))
        cat_tags.setdefault(meta.get("category"), set()).update(meta.get("tags") or [])
        for d in meta.get("dependencies") or []:
            dep_targets.add(d)

    context = {
        "categories": [c.get("id") for c in index.get("categories", [])],
        "marketplace_names": set(entries),
        "marketplace_entries": entries,
        "index_plugin_names": index_names,
        "index_tags": set(index.get("tags", [])),
        "category_tool_median": {
            c: median([n for n in counts if n > 0] or [1]) for c, counts in tool_counts.items()
        },
        "category_tags": cat_tags,
        "dependency_targets": dep_targets,
        "pattern_slugs": pattern_slugs(),
        "category_structural_avg": {},
        "metas": metas,
    }

    # First pass for structural conformance averages per category.
    for pdir in list_plugin_dirs():
        meta = metas[pdir.name]
        ext = read_text(pdir / (meta.get("entrypoint") or "extension.mjs"))
        readme = read_text(pdir / "README.md")
        checks = structural_checks(pdir, meta or None, ext, readme, context)
        structural_conf.setdefault(meta.get("category"), []).append(
            sum(checks.values()) / len(checks)
        )
    context["category_structural_avg"] = {
        c: sum(v) / len(v) for c, v in structural_conf.items() if v
    }
    return context


def score_plugin(pdir, context):
    meta = load_json(pdir / "plugin.json")
    ext = read_text(pdir / ((meta or {}).get("entrypoint") or "extension.mjs"))
    readme = read_text(pdir / "README.md")

    structural = structural_checks(pdir, meta, ext, readme, context)
    fifteen = fifteen_property_scores(pdir, meta, ext, structural, context)
    topology = topology_scores(meta, context)

    s_score = sum(structural.values()) / len(structural)
    f_score = sum(fifteen.values()) / len(fifteen)
    t_score = sum(topology.values()) / len(topology)
    wholeness = (
        WEIGHTS["structural"] * s_score
        + WEIGHTS["fifteen"] * f_score
        + WEIGHTS["topology"] * t_score
    )

    failing = sorted(k for k, v in structural.items() if not v)
    weak_properties = sorted(
        (k for k, v in fifteen.items() if v < 0.75), key=lambda k: fifteen[k]
    )

    return {
        "plugin": pdir.name,
        "wholeness": round(wholeness, 4),
        "groups": {
            "structural": round(s_score, 4),
            "fifteen": round(f_score, 4),
            "topology": round(t_score, 4),
        },
        "structural_checks": structural,
        "fifteen_properties": {k: round(v, 4) for k, v in fifteen.items()},
        "topology": {k: round(v, 4) for k, v in topology.items()},
        "failing_checks": failing,
        "weak_properties": weak_properties,
    }


def scan_marketplace():
    context = build_context()
    reports = [score_plugin(p, context) for p in list_plugin_dirs()]
    total = sum(r["wholeness"] for r in reports) / len(reports) if reports else 0.0
    return {
        "marketplace_wholeness": round(total, 4),
        "plugin_count": len(reports),
        "weights": WEIGHTS,
        "plugins": sorted(reports, key=lambda r: r["wholeness"]),
    }


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def print_summary(report):
    print(f"Marketplace wholeness W(total) = {report['marketplace_wholeness']:.4f} "
          f"across {report['plugin_count']} plugins\n")
    print(f"{'plugin':<32} {'W':>7} {'struct':>7} {'15prop':>7} {'topo':>7}  weakest")
    for r in report["plugins"]:
        weakest = r["weak_properties"][0] if r["weak_properties"] else "-"
        print(f"{r['plugin']:<32} {r['wholeness']:>7.3f} "
              f"{r['groups']['structural']:>7.3f} {r['groups']['fifteen']:>7.3f} "
              f"{r['groups']['topology']:>7.3f}  {weakest}")


def main(argv):
    if len(argv) < 2:
        print(__doc__)
        return 1
    cmd = argv[1]

    if cmd == "scan":
        report = scan_marketplace()
        if "--json" in argv:
            print(json.dumps(report, indent=2))
        else:
            print_summary(report)
        return 0

    if cmd == "score" and len(argv) >= 3:
        pdir = PLUGINS_DIR / argv[2]
        if not pdir.is_dir():
            print(f"Unknown plugin: {argv[2]}")
            return 1
        context = build_context()
        print(json.dumps(score_plugin(pdir, context), indent=2))
        return 0

    if cmd == "weakest":
        n = int(argv[2]) if len(argv) >= 3 and argv[2].isdigit() else 10
        report = scan_marketplace()
        print(f"{n} weakest centres (latent centres for the next KSM cycle):\n")
        for r in report["plugins"][:n]:
            print(f"  {r['plugin']:<32} W={r['wholeness']:.3f}  "
                  f"failing={len(r['failing_checks'])} checks, "
                  f"weak properties: {', '.join(r['weak_properties'][:3]) or '-'}")
        return 0

    print(__doc__)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
