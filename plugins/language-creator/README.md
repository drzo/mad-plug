# language-creator

Design and create domain-specific languages end-to-end: initialize projects, define grammars, emit parser files, extract terminology, and validate completeness.

**Version:** 0.1.0 | **Category:** Language Design & DSLs | **Tags:** `dsl` `grammar` `parser` `language`

---

## Description

`language-creator` (also registered in the marketplace as `dsl-factory`) provides a complete DSL development pipeline. Start by initializing a language project with the standard directory layout (`LANG.md` + subdirectories), define its grammar using prime grammar specifications, emit that grammar in PEG, BNF, or ANTLR format, extract a terminology lexicon from existing text corpora, and finally validate the project for structural completeness.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `dsl_init_language` | Initialize a new language project structure | `name` |
| `dsl_define_grammar` | Define a grammar from prime grammar specifications | `spec` |
| `dsl_emit_grammar` | Emit grammar files in PEG/BNF/ANTLR format | `spec_path` |
| `dsl_extract_lexicon` | Extract terminology from text corpora | `source` |
| `dsl_validate` | Validate a language project for completeness | `project_path` |

---

## Usage Examples

### Initialize a new DSL project
```
dsl_init_language(name="config-lang", output="languages/config-lang")
```
Creates `languages/config-lang/` with `LANG.md`, grammar/, lexicon/, and tests/ directories.

### Define the grammar
```
dsl_define_grammar(spec="key=value pairs, nested blocks with {}, comment lines starting with #", output="languages/config-lang/grammar/spec.yaml")
```
Produces a structured prime grammar specification YAML.

### Emit a PEG parser file
```
dsl_emit_grammar(spec_path="languages/config-lang/grammar/spec.yaml", format="peg")
```
Writes a PEG grammar file ready for use with a PEG parser generator.

### Extract lexicon from existing config files
```
dsl_extract_lexicon(source="examples/configs/", output="languages/config-lang/lexicon/terms.yaml")
```
Analyzes the corpus and builds a terminology dictionary.

### Validate the completed project
```
dsl_validate(project_path="languages/config-lang")
```
Reports any missing required files or structural issues.

---

## Dependencies

None

---

## Version

0.1.0

---

## Category & Tags

Category: `language-design`

Tags: `dsl` `grammar` `parser` `language`

---

## Scripts

Python scripts:
- `generators/init_language.py` — language project initialization
- `scripts/define_prime_grammar.py` — prime grammar definition
- `scripts/emit_grammar.py` — grammar file emission
- `generators/extract_lexicon.py` — lexicon extraction from corpora
- `generators/quick_validate.py` — project validation
