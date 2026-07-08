---
name: dsl-factory
description: >
  Design and create domain-specific languages with grammar definitions, parsers,
  lexicon extraction, and validation. Full pipeline from language specification
  to working parser and example programs.
tools:
  - generators/init_language.py
  - generators/extract_lexicon.py
  - generators/quick_validate.py
  - scripts/define_prime_grammar.py
  - scripts/emit_grammar.py
---

# Language Creator Plugin

Provides a complete pipeline for designing, implementing, and validating
domain-specific languages (DSLs).

## Capabilities

- **Initialize** a new language project with standard directory structure
- **Define grammars** using prime grammar specifications
- **Emit** grammar files from specifications
- **Extract lexicons** from existing text corpora or documentation
- **Validate** language projects for completeness and correctness

## Usage

Invoke when the user asks about:
- Creating a new DSL ("design a language for X")
- Grammar authoring ("define a grammar that handles Y")
- Lexicon work ("extract terminology from this document")
- Language validation ("check if my language project is complete")

## Pipeline

```
init_language.py → LANG.md + directories
define_prime_grammar.py → grammar specification
emit_grammar.py → grammar files
extract_lexicon.py → lexicon from corpus
quick_validate.py → project validation
```
