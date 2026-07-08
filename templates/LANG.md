---
name: PIE-NN
description: A differentiable programming language whose constructs are derived from Proto-Indo-European roots and structured according to neural network architecture patterns.
---

# PIE-NN Language Specification

## 1. Overview

PIE-NN is a differentiable, homoiconic programming language designed for creating cognitive architectures. Its syntax and semantics are derived from Proto-Indo-European (PIE) roots, providing a deep etymological grounding for its constructs. The language's architecture is modeled after the `language-nn` framework, treating language features as composable, trainable neural network modules.

This fusion allows for the creation of self-modifying programs whose structures evolve through feedback, guided by the semantic weight of ancient linguistic concepts.

## 2. Core Principles

- **Etymological Grounding**: Every core construct is mapped to a PIE root, inheriting its semantic field. For example, `*deik-` (to show) becomes the root for all declaration and assertion operations.
- **Differentiable Structure**: The language is composed of `lang.Construct` modules that support forward (`compile`) and backward (`redesign`) passes, allowing the language itself to be optimized.
- **Homoiconicity**: PIE-NN code is represented as a data structure (an Abstract Syntax Tree based on its own constructs) that can be manipulated by the language itself.
- **Temporal Execution**: The language is designed to run within a `time-crystal-daemon`, where operations are scheduled and executed on a hierarchical temporal oscillator, mirroring cognitive rhythms.

## 3. Language Architecture (language-nn mapping)

PIE-NN adopts the `language-nn` framework, mapping its concepts to PIE-derived constructs.

| `language-nn` Concept | PIE-NN Construct | PIE Root & Meaning |
|---|---|---|
| `lang.Construct` | `gno-` | `*gno-` (to know) - A fundamental, knowable unit of the language. |
| `lang.Pipeline` | `ser-` | `*ser-` (to line up) - A sequential series of operations. |
| `lang.Fork` | `skei-` | `*skei-` (to cut, split) - A parallel branching of execution paths. |
| `lang.Merge` | `sem-` | `*sem-` (one, as one) - A joining of parallel execution paths. |
| `lang.Criterion` | `krei-` | `*krei-` (to sieve, discriminate) - A loss function to evaluate design effectiveness. |
| `lang.TypeMap` | `meit-` | `*meit-` (to change, exchange) - A mapping between type systems. |
| `lang.Constraint` | `dher-` | `*dher-` (to hold firmly, support) - A constraint on syntax or values. |

## 4. Core Constructs and Grammar

The grammar is based on a small set of core PIE roots that define the primary operations.

### 4.1. Declarations (`*deik-` - to show)

- **`deik <name> is <type>`**: Declares a variable of a given type.
- **`deik <name> is gno-(...)`**: Declares a new language construct.

### 4.2. Operations (`*werg-` - to do)

- **`werg <operation> on <target>`**: Executes an operation.

### 4.3. State (`*stā-` - to stand)

- **`stā <name> at <value>`**: Sets the state of a variable.

### 4.4. Flow Control (`*kʷo-` - relative stem)

- **`kʷo <condition> then <block>`**: Conditional execution.

## 5. Example Program

This example defines a simple cognitive agent that perceives input and generates a response, structured as a `ser-` (pipeline).

```pie-nn
// Define a perception module
deik Perception is gno-(
  // Input: raw data, Output: structured percept
  deik input is RawData
  deik output is Percept

  werg Parse on input into output
)

// Define a response module
deik Response is gno-(
  deik input is Percept
  deik output is Action

  werg Decide on input into output
)

// Define the main agent pipeline
deik Agent is ser-(
  add Perception
  add Response
)

// Execute the agent
werg Agent on RawInputStream
```
