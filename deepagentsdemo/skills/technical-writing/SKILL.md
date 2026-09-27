---
name: technical-writing
description: Technical writing and documentation skill for authoring clear, structured, professional engineering documentation, API references, READMEs, architectural decision records (ADRs), tutorials, and code guides.
version: 1.0.0
tags:
  - technical-writing
  - documentation
  - readme
  - adr
  - api-docs
  - diataxis
  - guides
---

# Technical Writing Skill

## Purpose & Scope
This skill equips the **Deep Agent** with professional technical communication, documentation design, and developer-relations authoring capabilities.

Software engineering is only as effective as the documentation that accompanies it. This skill guides the agent to write clear, structured, concise, and audience-appropriate technical content—ranging from user-facing READMEs and interactive tutorials to rigorous Architectural Decision Records (ADRs), API references, and system design documents.

---

## Core Capabilities

1. **The Diátaxis Framework**:
   - Classifying and structuring documentation across the four core documentation quadrants:
     - **Tutorials**: Learning-oriented, step-by-step journeys for newcomers.
     - **How-To Guides**: Problem-oriented recipes showing how to accomplish specific real-world tasks.
     - **Reference**: Information-oriented technical descriptions, schemas, and API contracts.
     - **Explanation**: Understanding-oriented discussions of architecture, context, and tradeoffs.

2. **Architectural Decision Records (ADRs)**:
   - Formatting historical architectural decisions using the MADR / Nygard format: Context, Considered Options, Decision Outcome, Tradeoffs, and Consequences.

3. **High-Impact READMEs & Developer Portals**:
   - Creating captivating, scannable project entry points featuring value propositions, badges, quickstart scripts, architectural diagrams, configuration options, and license info.

4. **API & Interface Specifications**:
   - Writing precise API references: authentication, base URLs, typed request parameters, headers, response schemas, status code tables, and realistic error responses.

5. **Code Walkthroughs & Explanations**:
   - Using the **Context -> Mechanism -> Code Walkthrough -> Edge Cases** pedagogy when explaining code to human developers.
   - Using clear visual formatting (fenced blocks, syntax highlighting, callout alerts).

6. **Visual Systems & Architecture Modeling**:
   - Using **Mermaid.js** diagrams (`graph TD`, `sequenceDiagram`, `stateDiagram`) to visualize lifecycles, message sequences, and component topologies directly within Markdown.

---

## When to Use This Skill (Triggers)

Activate this skill when the user query involves:
- Writing or improving a project `README.md` or landing page documentation.
- Documenting an architecture, writing an RFC, or authoring an Architectural Decision Record (ADR).
- Creating an API reference, OpenAPI documentation, or endpoint usage guides.
- Writing developer tutorials, getting-started guides, or troubleshooting runbooks.
- Explaining complex algorithms, codebase structures, or systems design to technical and non-technical stakeholders.

---

## Associated References
- Detailed directives: [`instructions.md`](./instructions.md)
- Production templates & examples: [`examples.md`](./examples.md)
