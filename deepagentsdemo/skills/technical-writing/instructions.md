# Technical Writing Skill — Agent Instructions & Guidelines

When authoring technical documentation, system explanations, or developer guides, strictly adhere to the following authoring principles.

---

## 1. The Diátaxis Taxonomy

Before writing a single paragraph, classify the document into one of the four Diátaxis quadrants and adhere to its specific rules:

| Document Type | Primary Goal | Structure / Tone | Avoid |
|---|---|---|---|
| **Tutorial** | Teach a beginner by doing | Hands-on, step-by-step, predictable path | Explaining underlying architecture or theoretical tangents |
| **How-To Guide** | Help an expert solve a specific problem | Practical recipe, goal-oriented, prerequisites listed | Beginner hand-holding or foundational concept explanations |
| **Reference** | Provide accurate technical specifications | Precise, structured, complete, tabular | Opinions, workflows, or storytelling |
| **Explanation** | Provide conceptual understanding and context | Discursive, architectural, comparative, tradeoff-focused | Step-by-step instructional commands |

---

## 2. Information Architecture & Readability

1. **The Inverted Pyramid**:
   - Lead with the outcome or core conclusion in the opening 2–3 sentences (BLUF: Bottom Line Up Front).
   - Follow with essential context, then deeper technical details and edge cases.
2. **Visual Hierarchy & Scannability**:
   - Use descriptive, action-oriented headers (`## Setting Up the Local Development Environment` rather than `## Setup`).
   - Use bulleted lists for items of equal priority; use numbered lists only for sequential procedural steps.
   - Use tables for multi-attribute comparisons, parameters, and error code catalogs.
3. **GitHub / Markdown Callouts**:
   - Use callout blocks strategically to highlight critical caveats or best practices:
     - `> [!NOTE]`: Contextual background or extra information.
     - `> [!TIP]`: Performance optimizations or helpful shortcuts.
     - `> [!IMPORTANT]`: Crucial prerequisites or constraints.
     - `> [!WARNING]`: Actions that might cause downtime, build failures, or breaking changes.
     - `> [!CAUTION]`: Dangerous operations that risk data loss or security exposure.

---

## 3. Tone, Style & Language Precision

1. **Active Voice & Imperative Mood**:
   - Prefer active voice over passive voice:
     - *Good*: "The orchestrator routes the message to the worker node."
     - *Poor*: "The message is routed to the worker node by the orchestrator."
   - In instructions, use direct imperative verbs: "Run the build script," "Configure your API key."
2. **Audience-Aware Vocabulary**:
   - Tailor technical depth to the intended reader.
   - Eliminate filler words and empty marketing buzzwords ("revolutionary", "blazing fast", "game-changing", "seamless").
3. **Unambiguous Pronouns**:
   - Avoid ambiguous uses of "this", "it", or "that" when referring to complex technical concepts. Explicitly state the noun (e.g., "This configuration parameter...").

---

## 4. Code Presentation Standards

1. **Always Specify Syntax Highlighting**:
   - Always tag code fences with the exact language (`python`, `bash`, `json`, `yaml`, `typescript`, `sql`).
2. **Self-Contained & Functional Snippets**:
   - Never write code examples that rely on undeclared variables or mystery imports without context.
   - Include realistic comments explaining non-obvious design rationales.
3. **Show Inputs, Outputs, and Exceptions**:
   - Accompany code samples with expected terminal outputs or response JSON to give the reader instant validation.

---

## 5. Architectural Modeling with Mermaid Diagrams

Whenever explaining systems with multiple moving parts, render them using **Mermaid.js**:
- Use `graph TD` or `graph LR` for component topology and data flow.
- Use `sequenceDiagram` for asynchronous handoffs, API request/response cycles, and agent tool execution loops.
- Use `stateDiagram-v2` for state machine transitions.

---

## 6. Output Checklist for the Deep Agent

Before delivering technical documentation to the user:
- [ ] Is the document clearly classified under the Diátaxis taxonomy?
- [ ] Does it lead with the Bottom Line Up Front (BLUF)?
- [ ] Are code snippets syntactically tagged and functionally complete?
- [ ] Are complex architectures accompanied by clear Mermaid diagrams?
- [ ] Are actionable steps formatted as numbered lists with imperative verbs?
- [ ] Are callouts used strategically without excessive nesting?
