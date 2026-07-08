# Language Design Patterns

## Table of Contents

1. [Source Material Analysis Patterns](#source-material-analysis-patterns)
2. [Lexicon Extraction Patterns](#lexicon-extraction-patterns)
3. [Grammar Design Patterns](#grammar-design-patterns)
4. [Type System Patterns](#type-system-patterns)
5. [Semantic Patterns](#semantic-patterns)
6. [DSL Family Patterns](#dsl-family-patterns)

## Source Material Analysis Patterns

### Pattern: Corpus-Driven Design

Analyze a corpus of domain documents to extract the natural vocabulary and structure of the domain.

| Step | Action | Output |
|------|--------|--------|
| 1 | Collect representative documents | Corpus |
| 2 | Extract identifiers and phrases | Raw lexicon |
| 3 | Classify into nouns/verbs/adjectives | Categorized lexicon |
| 4 | Build co-occurrence graph | Relationship map |
| 5 | Identify invariants | Constraint set |

### Pattern: Example-Driven Design

Start with concrete examples of what programs in the language should look like, then derive the grammar.

```
Step 1: Write 5-10 example programs by hand
Step 2: Identify common syntactic patterns
Step 3: Generalize patterns into grammar rules
Step 4: Test grammar against examples
Step 5: Iterate until all examples parse
```

### Pattern: Transformation-Driven Design

Start with an existing language and systematically transform it to the target domain.

```
Step 1: Choose a source language (e.g., SQL, Python, Lisp)
Step 2: Identify domain-specific replacements
Step 3: Apply function-creator's domain mapping
Step 4: Validate the transformed language
```

## Lexicon Extraction Patterns

### Pattern: Noun → Type

Domain nouns become types or data constructors in the language.

| Domain Noun | Language Construct |
|-------------|-------------------|
| Customer | `type Customer` |
| Transaction | `type Transaction` |
| Account | `type Account` |

### Pattern: Verb → Operation

Domain verbs become functions, methods, or operators.

| Domain Verb | Language Construct |
|-------------|-------------------|
| Transfer | `transfer(from, to, amount)` |
| Validate | `validate(transaction)` |
| Approve | `approve(request)` |

### Pattern: Adjective → Constraint

Domain adjectives become type constraints, guards, or modifiers.

| Domain Adjective | Language Construct |
|------------------|-------------------|
| Valid | `valid Transaction` (refined type) |
| Pending | `pending : Status` (enum variant) |
| Sufficient | `guard sufficient(balance, amount)` |

### Pattern: Relationship → Composition

Domain relationships become type composition or module structure.

| Domain Relationship | Language Construct |
|--------------------|-------------------|
| "Account has Transactions" | `type Account { transactions: [Transaction] }` |
| "Transaction produces Receipt" | `fn process(t: Transaction) -> Receipt` |
| "Manager approves Request" | `trait Approver { fn approve(r: Request) }` |

## Grammar Design Patterns

### Pattern: Expression-Oriented

Everything is an expression that returns a value. Minimizes the distinction between statements and expressions.

```ebnf
program    = { expression ";" } ;
expression = let_expr | if_expr | fn_expr | binary_expr ;
```

### Pattern: Declaration-Oriented

Programs are sequences of declarations. Good for configuration and schema languages.

```ebnf
program     = { declaration } ;
declaration = type_decl | fn_decl | const_decl ;
```

### Pattern: Pipeline-Oriented

Data flows through a pipeline of transformations. Good for data processing DSLs.

```ebnf
pipeline   = source , { "|>" , transform } ;
source     = identifier | literal ;
transform  = identifier , [ "(" , args , ")" ] ;
```

### Pattern: Rule-Oriented

Programs are sets of rules or patterns. Good for business logic and validation DSLs.

```ebnf
program    = { rule } ;
rule       = pattern , "=>" , action ;
pattern    = condition , { "and" , condition } ;
```

## Type System Patterns

### Pattern: Structural Typing

Types are defined by their structure, not their name. Good for data interchange.

### Pattern: Nominal Typing

Types are defined by their name. Good for domain modeling where identity matters.

### Pattern: Refinement Types

Types with predicates that constrain values. Good for validation-heavy domains.

```
type PositiveInt = { x: Int | x > 0 }
type ValidEmail = { s: String | matches(s, email_regex) }
```

### Pattern: Effect Types

Types that track computational effects. Good for safety-critical domains.

```
fn read_file(path: Path) -> IO[String]
fn transfer(from: Account, to: Account, amount: Money) -> Transaction[Receipt]
```

## Semantic Patterns

### Pattern: Eager Evaluation

Expressions are evaluated immediately. Simple mental model, good for scripting DSLs.

### Pattern: Lazy Evaluation

Expressions are evaluated only when needed. Good for infinite data structures and query DSLs.

### Pattern: Staged Evaluation

Expressions are evaluated in stages (compile-time, link-time, run-time). Good for code generation DSLs.

## DSL Family Patterns

Common DSL archetypes derived from source material analysis:

| Archetype | Domain | Key Features |
|-----------|--------|-------------|
| **Query DSL** | Data retrieval | SELECT/FROM/WHERE, joins, aggregations |
| **Config DSL** | System configuration | Key-value, nesting, inheritance, validation |
| **Workflow DSL** | Business processes | States, transitions, guards, actions |
| **Schema DSL** | Data modeling | Types, relationships, constraints, migrations |
| **Rule DSL** | Business logic | Conditions, actions, priorities, conflict resolution |
| **Template DSL** | Text generation | Interpolation, loops, conditionals, filters |
| **Test DSL** | Quality assurance | Given/When/Then, assertions, fixtures, mocks |
| **Build DSL** | Software builds | Targets, dependencies, recipes, variables |
