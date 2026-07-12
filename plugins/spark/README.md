# spark

Comprehensive guidance for building modern web applications with opinionated defaults for tech stack, design system, and code standards.

**Version:** 0.1.0 | **Category:** Code Generation & Scaffolding | **Tags:** `web` `react` `vite` `typescript` `scaffold` `stack`

---

## Description

`spark` provides structured, opinionated guidance for bootstrapping modern web applications. It curates a pre-vetted technology stack (Vite, React 19+, TypeScript, Tailwind CSS v4+, shadcn/ui, TanStack Router & Query) and matches it to four complexity tiers. The plugin also exposes reference material for design systems, typography pairings, OKLCH color palettes, component patterns, and performance checklists.

---

## Tools

| Tool | Description | Required Parameters |
|---|---|---|
| `spark_get_stack` | Get the full stack specification for a complexity tier | `stack` |
| `spark_list_stacks` | List all available stack variations with brief descriptions | — |
| `spark_get_reference` | Retrieve a reference document (design system, colors, etc.) | `reference` |

### `spark_get_stack` stack tiers

| Value | Use Case |
|---|---|
| `default-webapp` | General-purpose tools, utilities, MVPs, prototypes |
| `content-showcase` | Marketing sites, portfolios, blogs, documentation |
| `data-dashboard` | Analytics dashboards, admin panels, BI tools |
| `complex-application` | SaaS platforms, enterprise tools, multi-view apps |

### `spark_get_reference` documents

| Value | Description |
|---|---|
| `design-system` | Design philosophy, spatial composition, micro-interactions |
| `typography-pairings` | Distinctive font combinations with personality guidance |
| `color-palettes` | Pre-curated OKLCH palettes with WCAG validation |
| `component-patterns` | Common shadcn compositions and usage patterns |
| `performance-checklist` | Web Vitals optimization, React Compiler setup |
| `prd-template` | Simplified planning framework for new apps |
| `radix-migration-guide` | Base UI migration path for Radix concerns |

---

## Usage Examples

### Get the default web app stack
```
spark_get_stack(stack="default-webapp")
```
Returns the full technology specification, package list, configuration templates, and design guidance for a general-purpose web application.

### Get the data dashboard stack
```
spark_get_stack(stack="data-dashboard")
```
Returns the dashboard-optimized stack with Recharts and date-fns additions, plus data-density design guidance.

### List all available stacks
```
spark_list_stacks()
```
Returns a summary of all four complexity tiers with one-line descriptions.

### Get the design system reference
```
spark_get_reference(reference="design-system")
```
Returns the comprehensive design philosophy document covering spatial composition, backgrounds, and micro-interactions.

---

## Dependencies

None

---

## Version

0.1.0

---

## Category & Tags

Category: `code-generation`

Tags: `web` `react` `vite` `typescript` `scaffold` `stack`

---

## What it does

Spark helps you quickly bootstrap high-quality web applications by providing:

- Pre-vetted technology stack choices with multiple complexity-based variations
- An opinionated design philosophy and system
- Step-by-step setup workflows
- Design and performance optimization guidance

## Skills

### `spark-app-template`

Activated when a user wants to create a new web application, dashboard, or interactive interface. Provides guidance on:

- **Tech stack** — Vite, React 19+, TypeScript, Tailwind CSS v4+, shadcn/ui, TanStack Router & Query
- **Design system** — Typography pairings, OKLCH color palettes, spatial composition, micro-interactions
- **Stack variations** — Pre-configured stacks tailored to app complexity (default web app, content showcase, data dashboard, complex application)
- **Performance** — Core Web Vitals targets, React Compiler setup, optimization checklists
- **Component patterns** — Common shadcn compositions and usage patterns

## Stack variations

| Stack | Use case |
| --- | --- |
| **Default Web App** | General-purpose tools, utilities, simple CRUD, MVPs, prototypes |
| **Content Showcase** | Marketing sites, portfolios, blogs, documentation |
| **Data Dashboard** | Analytics dashboards, admin panels, BI tools, monitoring |
| **Complex Application** | SaaS platforms, enterprise tools, multi-view apps |
