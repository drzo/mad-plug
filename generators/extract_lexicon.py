#!/usr/bin/env python3
"""
Extract a domain lexicon from source material for DSL design.

Usage:
    python extract_lexicon.py <source-file-or-dir> [--output lexicon.yaml]

Analyzes source material (text, code, data) to extract:
  - Domain nouns (entities, objects, concepts)
  - Domain verbs (actions, operations, processes)
  - Domain relationships (contains, produces, validates)
  - Domain constraints (invariants, rules, bounds)
  - Frequency and co-occurrence data

Output: A YAML lexicon file suitable for language design.
"""

import os
import sys
import re
import json
from collections import Counter, defaultdict
from pathlib import Path


def read_sources(path: str) -> list[str]:
    """Read all text files from a file or directory."""
    texts = []
    p = Path(path)
    if p.is_file():
        texts.append(p.read_text(errors="replace"))
    elif p.is_dir():
        for f in p.rglob("*"):
            if f.is_file() and f.suffix in (".txt", ".md", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".csv", ".sql", ".html", ".xml", ".lua", ".rb", ".go", ".rs", ".java", ".c", ".cpp", ".h"):
                try:
                    texts.append(f.read_text(errors="replace"))
                except Exception:
                    pass
    return texts


def extract_identifiers(text: str) -> list[str]:
    """Extract identifiers (camelCase, snake_case, PascalCase)."""
    # Match programming identifiers
    idents = re.findall(r'\b[A-Za-z_][A-Za-z0-9_]*\b', text)
    # Split camelCase and PascalCase
    expanded = []
    for ident in idents:
        parts = re.sub(r'([a-z])([A-Z])', r'\1_\2', ident).lower().split('_')
        expanded.extend(p for p in parts if len(p) > 2)
    return expanded


def extract_phrases(text: str) -> list[str]:
    """Extract noun phrases (simple heuristic)."""
    # Simple: sequences of capitalized words
    phrases = re.findall(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+\b', text)
    return [p.lower() for p in phrases]


def classify_words(words: list[str]) -> dict:
    """Classify words into rough categories based on common patterns."""
    nouns = []
    verbs = []
    adjectives = []

    verb_suffixes = ('ate', 'ify', 'ize', 'ise', 'ect', 'ute', 'ess', 'ode')
    verb_prefixes = ('get', 'set', 'add', 'del', 'run', 'put', 'pop', 'has')
    adj_suffixes = ('able', 'ible', 'ful', 'less', 'ous', 'ive', 'ent', 'ant')

    for w in words:
        wl = w.lower()
        if wl.endswith(verb_suffixes) or wl.startswith(verb_prefixes):
            verbs.append(wl)
        elif wl.endswith(adj_suffixes):
            adjectives.append(wl)
        else:
            nouns.append(wl)

    return {
        "nouns": Counter(nouns).most_common(50),
        "verbs": Counter(verbs).most_common(30),
        "adjectives": Counter(adjectives).most_common(20),
    }


def build_cooccurrence(texts: list[str], top_words: set) -> dict:
    """Build co-occurrence matrix for top words."""
    cooccur = defaultdict(Counter)
    for text in texts:
        sentences = re.split(r'[.;!?\n]', text.lower())
        for sent in sentences:
            words_in_sent = set(re.findall(r'\b\w+\b', sent)) & top_words
            for w1 in words_in_sent:
                for w2 in words_in_sent:
                    if w1 < w2:
                        cooccur[w1][w2] += 1
                        cooccur[w2][w1] += 1
    # Return top co-occurrences
    result = {}
    for word, neighbors in cooccur.items():
        result[word] = [n for n, _ in neighbors.most_common(5)]
    return result


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract domain lexicon from source material")
    parser.add_argument("source", help="Source file or directory")
    parser.add_argument("--output", "-o", default="lexicon.yaml", help="Output YAML file")
    args = parser.parse_args()

    texts = read_sources(args.source)
    if not texts:
        print(f"❌ No readable files found at: {args.source}")
        sys.exit(1)

    print(f"📖 Read {len(texts)} source files")

    # Extract all identifiers
    all_words = []
    for t in texts:
        all_words.extend(extract_identifiers(t))

    # Classify
    classified = classify_words(all_words)

    # Build co-occurrence for top terms
    top_words = set()
    for category in classified.values():
        top_words.update(w for w, _ in category[:20])
    cooccur = build_cooccurrence(texts, top_words)

    # Output as YAML
    lines = [
        "# Domain Lexicon",
        f"# Extracted from: {args.source}",
        f"# Total tokens analyzed: {len(all_words)}",
        "",
        "nouns:",
    ]
    for word, count in classified["nouns"]:
        related = cooccur.get(word, [])
        rel_str = f"  # co-occurs with: {', '.join(related)}" if related else ""
        lines.append(f"  - term: {word}  # freq: {count}{rel_str}")

    lines.append("")
    lines.append("verbs:")
    for word, count in classified["verbs"]:
        lines.append(f"  - term: {word}  # freq: {count}")

    lines.append("")
    lines.append("adjectives:")
    for word, count in classified["adjectives"]:
        lines.append(f"  - term: {word}  # freq: {count}")

    lines.append("")
    lines.append("# Suggested language keywords (top nouns + verbs):")
    lines.append("suggested_keywords:")
    for word, count in (classified["nouns"][:10] + classified["verbs"][:5]):
        lines.append(f"  - {word}")

    output = "\n".join(lines) + "\n"
    with open(args.output, "w") as f:
        f.write(output)

    print(f"✅ Lexicon written to: {args.output}")
    print(f"   Nouns: {len(classified['nouns'])}")
    print(f"   Verbs: {len(classified['verbs'])}")
    print(f"   Adjectives: {len(classified['adjectives'])}")


if __name__ == "__main__":
    main()
