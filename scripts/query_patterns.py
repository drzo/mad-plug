#!/usr/bin/env python3
"""
gh253 Pattern Query Tool
Usage: python query_patterns.py <command> [args]

Commands:
  get <id>              Get pattern by ID (1-253)
  search <term>         Search patterns by name/content
  broader <id>          Get broader (parent) patterns
  narrower <id>         Get narrower (child) patterns
  roots                 List root patterns (no broader)
  hubs                  List high-connectivity hub patterns
  path <from> <to>      Find path between patterns
"""

import sys
import re
from pathlib import Path
from collections import deque

# Patterns live at <repo-root>/patterns/cat{1,2,3}-{enterprises,organisations,repositories}/
# as gh<NNN>-<slug>.md files, with per-pattern gh<NNN>/broader.md and
# gh<NNN>/narrower.md relationship files alongside them.
BASE = Path(__file__).resolve().parent.parent / "patterns"
CATEGORIES = ["cat1-enterprises", "cat2-organisations", "cat3-repositories"]


def find_pattern_file(pattern_id: int) -> Path:
    """Find pattern file by ID"""
    pid = f"gh{pattern_id:03d}"
    for cat in CATEGORIES:
        cat_path = BASE / cat
        if not cat_path.exists():
            continue
        matches = list(cat_path.glob(f"{pid}-*.md"))
        if matches:
            return matches[0]
    return None

def get_pattern(pattern_id: int) -> dict:
    """Get pattern content"""
    path = find_pattern_file(pattern_id)
    if not path:
        return None
    
    content = path.read_text(encoding="utf-8")
    
    # Frontmatter looks like: description: "100 - CONTRIBUTOR PATH"
    name_match = re.search(r'description:\s*["\']?(\d+\s*-\s*)?(.+?)["\']?\s*$', content, re.MULTILINE)
    if name_match:
        name = name_match.group(2).strip()
    else:
        # Fall back to the first markdown heading.
        heading_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        name = heading_match.group(1).strip() if heading_match else f"Pattern {pattern_id}"
    
    return {"id": pattern_id, "name": name, "content": content, "path": str(path)}

def get_refs(pattern_id: int, ref_type: str) -> list:
    """Get broader or narrower references"""
    path = find_pattern_file(pattern_id)
    if not path:
        return []
    
    ref_file = path.parent / f"gh{pattern_id:03d}" / f"{ref_type}.md"
    if not ref_file.exists():
        return []
    
    content = ref_file.read_text(encoding="utf-8")
    matches = re.findall(r'gh(\d{3})', content, re.IGNORECASE)
    refs = []
    for m in matches:
        rid = int(m)
        if rid != pattern_id and rid not in refs:
            refs.append(rid)
    return refs

def search_patterns(term: str) -> list:
    """Search patterns by term"""
    results = []
    term_lower = term.lower()
    
    for cat in CATEGORIES:
        cat_path = BASE / cat
        if not cat_path.exists():
            continue
        for pattern_file in cat_path.glob("gh*.md"):
            if pattern_file.is_dir():
                continue
            content = pattern_file.read_text(encoding="utf-8")
            if term_lower in content.lower():
                match = re.match(r'gh(\d{3})', pattern_file.name)
                if match:
                    pid = int(match.group(1))
                    pattern = get_pattern(pid)
                    if pattern:
                        results.append(pattern)
    
    return results

def find_path(start: int, end: int) -> list:
    """Find shortest path between patterns (via narrower)"""
    if start == end:
        return [start]
    
    queue = deque([(start, [start])])
    visited = {start}
    
    while queue:
        current, path = queue.popleft()
        for child in get_refs(current, "narrower"):
            if child == end:
                return path + [child]
            if child not in visited:
                visited.add(child)
                queue.append((child, path + [child]))
    
    return []

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    
    cmd = sys.argv[1]
    
    if cmd == "get" and len(sys.argv) > 2:
        pid = int(sys.argv[2])
        pattern = get_pattern(pid)
        if pattern:
            print(f"[{pattern['id']}] {pattern['name']}")
            print(f"Path: {pattern['path']}")
            print("-" * 50)
            print(pattern['content'][:1000])
        else:
            print(f"Pattern {pid} not found")
    
    elif cmd == "search" and len(sys.argv) > 2:
        term = " ".join(sys.argv[2:])
        results = search_patterns(term)
        print(f"Found {len(results)} patterns matching '{term}':")
        for p in results[:20]:
            print(f"  [{p['id']:3d}] {p['name']}")
    
    elif cmd == "broader" and len(sys.argv) > 2:
        pid = int(sys.argv[2])
        refs = get_refs(pid, "broader")
        print(f"Broader patterns for {pid}:")
        for ref in refs:
            p = get_pattern(ref)
            print(f"  [{ref:3d}] {p['name'] if p else 'Unknown'}")
    
    elif cmd == "narrower" and len(sys.argv) > 2:
        pid = int(sys.argv[2])
        refs = get_refs(pid, "narrower")
        print(f"Narrower patterns for {pid}:")
        for ref in refs:
            p = get_pattern(ref)
            print(f"  [{ref:3d}] {p['name'] if p else 'Unknown'}")
    
    elif cmd == "roots":
        print("Root patterns (no broader context):")
        for pid in [1, 18, 24, 95]:
            p = get_pattern(pid)
            if p:
                print(f"  [{pid:3d}] {p['name']}")
    
    elif cmd == "hubs":
        print("Hub patterns (highest connectivity):")
        hubs = [(30, 24), (107, 21), (100, 20)]
        for pid, degree in hubs:
            p = get_pattern(pid)
            if p:
                print(f"  [{pid:3d}] {p['name']} (degree: {degree})")
    
    elif cmd == "path" and len(sys.argv) > 3:
        start = int(sys.argv[2])
        end = int(sys.argv[3])
        path = find_path(start, end)
        if path:
            print(f"Path from {start} to {end}:")
            print(" → ".join(str(p) for p in path))
        else:
            print(f"No path found from {start} to {end}")
    
    else:
        print(__doc__)

if __name__ == "__main__":
    main()
