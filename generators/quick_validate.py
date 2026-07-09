#!/usr/bin/env python3
"""
Validate a language project structure and specification.

Usage:
    python quick_validate.py <language-name>

Checks:
    1. LANG.md exists and has valid frontmatter
    2. Required directories exist
    3. Grammar file exists and is non-empty
    4. Parser script exists and is syntactically valid
    5. At least one example program exists
    6. Example programs parse without errors
"""

import os
import sys
import re
import ast
import subprocess


def validate_language(name: str) -> bool:
    # Accept either a direct path to the project (relative or absolute) or a
    # bare language name, in which case fall back to the conventional
    # ~/skills/<name> location.
    if os.path.exists(name) or os.sep in name or "/" in name or os.path.isabs(name):
        base = name
    else:
        base = os.path.join(os.path.expanduser("~/skills"), name)
    errors = []
    warnings = []

    # 1. Check LANG.md
    lang_md = f"{base}/LANG.md"
    if not os.path.exists(lang_md):
        errors.append(f"Missing LANG.md at {lang_md}")
    else:
        with open(lang_md) as f:
            content = f.read()
        if not content.startswith("---"):
            errors.append("LANG.md missing YAML frontmatter (must start with ---)")
        if "name:" not in content:
            errors.append("LANG.md frontmatter missing 'name' field")
        if "description:" not in content:
            errors.append("LANG.md frontmatter missing 'description' field")
        if "[TODO" in content:
            warnings.append("LANG.md still contains [TODO] placeholders")
        lines = content.strip().split("\n")
        if len(lines) < 10:
            warnings.append(f"LANG.md is very short ({len(lines)} lines)")

    # 2. Check directories
    for subdir in ["generators", "specifications", "syntax_templates"]:
        path = f"{base}/{subdir}"
        if not os.path.isdir(path):
            warnings.append(f"Missing directory: {subdir}/")

    # 3. Check grammar
    grammar_path = f"{base}/specifications/grammar.ebnf"
    if os.path.exists(grammar_path):
        with open(grammar_path) as f:
            grammar = f.read().strip()
        if not grammar:
            errors.append("grammar.ebnf is empty")
    else:
        warnings.append("No grammar.ebnf found in specifications/")

    # 4. Check parser
    parser_path = f"{base}/generators/parser.py"
    if os.path.exists(parser_path):
        with open(parser_path) as f:
            parser_src = f.read()
        try:
            ast.parse(parser_src)
        except SyntaxError as e:
            errors.append(f"parser.py has syntax error: {e}")
    else:
        warnings.append("No parser.py found in generators/")

    # 5. Check examples
    templates_dir = f"{base}/syntax_templates"
    if os.path.isdir(templates_dir):
        examples = [f for f in os.listdir(templates_dir) if not f.startswith(".")]
        if not examples:
            warnings.append("No example programs in syntax_templates/")
    else:
        warnings.append("syntax_templates/ directory missing")

    # 6. Try parsing examples
    if os.path.exists(parser_path) and os.path.isdir(templates_dir):
        for ex in os.listdir(templates_dir):
            ex_path = f"{templates_dir}/{ex}"
            if os.path.isfile(ex_path):
                try:
                    result = subprocess.run(
                        [sys.executable, parser_path, ex_path],
                        capture_output=True, text=True, timeout=10
                    )
                    if result.returncode != 0:
                        warnings.append(f"Parser failed on {ex}: {result.stderr.strip()}")
                except subprocess.TimeoutExpired:
                    warnings.append(f"Parser timed out on {ex}")
                except Exception as e:
                    warnings.append(f"Could not test parser on {ex}: {e}")

    # Report
    print(f"\n{'='*60}")
    print(f"  Language Validation: {name}")
    print(f"{'='*60}\n")

    if errors:
        print(f"❌ ERRORS ({len(errors)}):")
        for e in errors:
            print(f"   • {e}")
        print()

    if warnings:
        print(f"⚠️  WARNINGS ({len(warnings)}):")
        for w in warnings:
            print(f"   • {w}")
        print()

    if not errors and not warnings:
        print("✅ All checks passed!\n")
    elif not errors:
        print("✅ No errors (warnings are informational)\n")
    else:
        print("❌ Fix errors before delivery\n")

    return len(errors) == 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python quick_validate.py <language-name>")
        sys.exit(1)
    ok = validate_language(sys.argv[1])
    sys.exit(0 if ok else 1)
