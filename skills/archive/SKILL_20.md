---
name: language-creator
description: Guide for designing and creating effective domain-specific languages (DSLs) and optimal programming languages from source material. Use when designing a new language, transforming an existing language, or creating language tooling from a corpus of examples.
---

# Language Creator

This skill provides guidance for creating effective programming languages, especially DSLs, by analyzing source material.

## About Languages

Languages are formal systems for expressing computation. This skill transforms the `skill-creator` paradigm into a `language-creator` paradigm, applying the principles of skill design to the design of programming languages.

### What Languages Provide

1.  **Domain-Specific Abstractions** - High-level constructs tailored to a problem domain.
2.  **Formal Syntax & Semantics** - Unambiguous rules for interpretation and execution.
3.  **Tooling & Ecosystems** - Compilers, interpreters, debuggers, and libraries.
4.  **Reusable Paradigms** - Encapsulated patterns of computation (functional, OO, etc.).

## Core Principles

### Concise is Key

The language should be expressive and minimal. Every keyword and syntactic construct must justify its existence.

**Default assumption: The user is a smart developer.** Only add features that provide significant expressive power or safety. Challenge each feature: "Is this truly necessary?" and "Does this feature justify its complexity?"

Prefer clear, orthogonal concepts over numerous special-case features.

### Set Appropriate Degrees of Freedom

Match the language's level of abstraction and constraint to the target domain's needs:

*   **High freedom (General Purpose Language)**: Use when the language must solve a wide variety of problems.
*   **Medium freedom (Domain-Specific Language)**: Use when a clear problem domain exists, but flexibility is still required.
*   **Low freedom (Configuration Language)**: Use when the language is primarily for declaring state or configuration, with minimal logic.

## Anatomy of a Language (as a Skill)

Every language definition consists of a required LANG.md file and optional bundled resources:

```
language-name/
├── LANG.md (required)
│   ├── YAML frontmatter metadata (required)
│   │   ├── name: (required)
│   │   └── description: (required)
│   └── Markdown specification (required)
└── Language Resources (optional)
    ├── generators/       - Code generators, compilers, interpreters
    ├── specifications/   - Formal grammar (EBNF), type system rules
    └── syntax_templates/ - Code snippets, examples, standard library
```

## Language Creation Process

Language creation involves these steps:

1.  **Analyze Source Material** - Understand the domain through concrete examples.
2.  **Design Language Architecture** - Plan reusable language constructs and tooling.
3.  **Scaffold the Language** - Initialize the language project.
4.  **Implement Language Specification** - Write the grammar, semantics, and tooling.
5.  **Validate the Language Design** - Test the language against the source material.
6.  **Deliver the Language** - Package the language and its toolchain.
7.  **Iterate on the Design** - Refine the language based on usage and feedback.

### Step 1: Analyzing the Source Material

Gather a corpus of source material (documents, code, data) that the language aims to represent or manipulate. Ask questions like:

*   "What are the core entities and relationships in this domain?"
*   "What are the common operations and transformations?"
*   "What are the invariants and constraints?"

### Step 2: Designing the Language Architecture

For each pattern in the source material, identify the required language constructs:

| Resource Type        | When to Use                                    | Example                                       |
| -------------------- | ---------------------------------------------- | --------------------------------------------- |
| `generators/`        | Repetitive code generation or interpretation   | `parser.py` to generate an AST from text      |
| `syntax_templates/`  | Boilerplate code or standard library functions | A standard `main` function or `List` library  |
| `specifications/`    | Formal rules needed for implementation         | EBNF grammar, type inference rules            |

### Step 3: Scaffolding the Language

Use the `init_language.py` script to generate a new language project structure.

```bash
python /home/ubuntu/skills/language-creator/generators/init_language.py <language-name>
```

### Step 4: Implement the Language Specification

This is the core implementation phase. Write the parser, type checker, interpreter/compiler, and any other tooling. Use the `language-nn` framework to structure this process.

### Step 5: Validate the Language Design

Run the validation script to test the language against the source corpus:

```bash
python /home/ubuntu/skills/language-creator/generators/quick_validate.py <language-name>
```

### Step 6: Delivering the Language

Package the language using the `message` tool, sending the `LANG.md` file as the primary artifact.

### Step 7: Iterate

Refine the language based on feedback from users and its performance on new source material.
