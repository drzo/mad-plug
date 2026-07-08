# Domain-to-Language Mapping Patterns

## Table of Contents

1. [The Mapping Functor](#the-mapping-functor)
2. [Financial Domain → Language](#financial-domain--language)
3. [Data Processing Domain → Language](#data-processing-domain--language)
4. [Legal/Compliance Domain → Language](#legalcompliance-domain--language)
5. [Infrastructure Domain → Language](#infrastructure-domain--language)
6. [Scientific Domain → Language](#scientific-domain--language)
7. [Writing Your Own Mappings](#writing-your-own-mappings)

## The Mapping Functor

A domain-to-language mapping is a functor `F: Domain → Language` that maps:

```
F(entity) = type
F(operation) = function
F(constraint) = type_constraint
F(relationship) = composition
F(invariant) = axiom
F(pattern) = idiom
```

The functor preserves domain relationships as language relationships.

## Financial Domain → Language

Source: Banking, trading, accounting

| Domain Concept | Language Construct | Example Syntax |
|---------------|-------------------|----------------|
| Account | `type Account` | `account checking : Account` |
| Transaction | `type Transaction` | `tx = transfer(from, to, 100.00)` |
| Balance | `refined type` | `type Balance = { n: Decimal \| n >= 0 }` |
| Transfer | `function` | `fn transfer(from: Account, to: Account, amount: Money)` |
| Reconcile | `assertion` | `assert balance(a) == sum(credits(a)) - sum(debits(a))` |
| Audit Trail | `effect type` | `fn transfer(...) -> Audited[Receipt]` |

### Example DSL: FinLang

```
account savings : Account(currency=ZAR)
account checking : Account(currency=ZAR)

rule "minimum balance" {
  when balance(savings) < 1000.00
  then alert("Low balance", savings)
}

transaction payroll {
  debit checking 50000.00
  credit savings 50000.00
  memo "Monthly salary"
}
```

## Data Processing Domain → Language

Source: ETL pipelines, data transformation

| Domain Concept | Language Construct | Example Syntax |
|---------------|-------------------|----------------|
| Source | `source` declaration | `source csv("data.csv")` |
| Transform | `pipe operator` | `data \|> filter(age > 18) \|> sort(name)` |
| Schema | `type` declaration | `type Person { name: String, age: Int }` |
| Validation | `guard` | `guard valid_email(email)` |
| Sink | `sink` declaration | `sink postgres("table_name")` |

### Example DSL: FlowLang

```
source customers = csv("customers.csv", schema=Customer)

pipeline clean_customers {
  customers
  |> filter(age >= 18)
  |> map(name -> uppercase(name))
  |> deduplicate(by=email)
  |> validate(schema=CleanCustomer)
  |> sink(postgres("clean_customers"))
}
```

## Legal/Compliance Domain → Language

Source: Regulations, contracts, compliance rules

| Domain Concept | Language Construct | Example Syntax |
|---------------|-------------------|----------------|
| Party | `type Party` | `party plaintiff : Person` |
| Obligation | `must` keyword | `plaintiff must file_within(30.days)` |
| Right | `may` keyword | `defendant may appeal(judgment)` |
| Condition | `when` clause | `when filed(complaint) then serve(defendant)` |
| Deadline | `temporal type` | `deadline : Date = filing_date + 30.days` |
| Evidence | `fact` declaration | `fact exhibit_a : Document(certified=true)` |

### Example DSL: LexLang

```
case fraud_investigation {
  party complainant : Person
  party respondent : Company

  fact statement : BankStatement(period=2024-01..2024-12)
  fact evidence_a : EmailChain(from=respondent)

  rule "burden of proof" {
    complainant must prove(
      on_balance_of_probabilities,
      that: respondent.misrepresented(statement)
    )
  }

  remedy {
    if proven then order(respondent, pay(damages))
  }
}
```

## Infrastructure Domain → Language

Source: Cloud infrastructure, deployment

| Domain Concept | Language Construct | Example Syntax |
|---------------|-------------------|----------------|
| Resource | `resource` declaration | `resource web_server : EC2(t3.micro)` |
| Dependency | `depends_on` | `db depends_on vpc` |
| Configuration | `config` block | `config { region = "us-east-1" }` |
| Scaling | `scale` rule | `scale web_server when cpu > 80%` |
| Network | `network` declaration | `network vpc : VPC(cidr="10.0.0.0/16")` |

## Scientific Domain → Language

Source: Mathematical models, simulations

| Domain Concept | Language Construct | Example Syntax |
|---------------|-------------------|----------------|
| Variable | `var` declaration | `var x : Real = 0.0` |
| Equation | `equation` block | `equation: dx/dt = -k * x` |
| Constraint | `subject_to` | `subject_to x >= 0` |
| Unit | `unit type` | `type Velocity = Meters / Seconds` |
| Simulation | `simulate` block | `simulate(t=0..100, dt=0.01)` |

## Writing Your Own Mappings

### Step 1: Identify Domain Vocabulary

Run the lexicon extractor on your source material:

```bash
python /home/ubuntu/skills/language-creator/generators/extract_lexicon.py <source-dir>
```

### Step 2: Classify into Language Roles

| Domain Category | Language Role | Mapping Rule |
|----------------|--------------|--------------|
| Nouns (entities) | Types | Each noun → a type declaration |
| Verbs (operations) | Functions | Each verb → a function signature |
| Adjectives (qualities) | Constraints | Each adjective → a type refinement |
| Relationships | Composition | Each relationship → type composition |
| Invariants | Axioms | Each invariant → a compile-time check |
| Patterns | Idioms | Each pattern → a syntactic sugar |

### Step 3: Choose a Grammar Archetype

Based on the domain's natural structure, select from:

| If the domain is about... | Use archetype... |
|--------------------------|-----------------|
| Querying data | Query DSL (SELECT/FROM/WHERE) |
| Configuring systems | Config DSL (key-value, nesting) |
| Defining workflows | Workflow DSL (states, transitions) |
| Modeling data | Schema DSL (types, relationships) |
| Expressing rules | Rule DSL (conditions, actions) |
| Generating text | Template DSL (interpolation, loops) |

### Step 4: Validate the Mapping

Check that the mapping preserves domain relationships:

- If A contains B in the domain, `type A` should contain `type B`
- If A produces B in the domain, `fn a() -> B` should exist
- If A constrains B in the domain, `type B` should have a constraint from A
