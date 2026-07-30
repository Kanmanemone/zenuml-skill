# ZenUML DSL Syntax Reference

> Adapted from `mermaid-js/zenuml-core`'s [`docs/DSL_SYNTAX.md`](https://github.com/mermaid-js/zenuml-core/blob/master/docs/DSL_SYNTAX.md) (MIT License). Reorganized and condensed for use as a Claude Skill reference; original credit and license belong to the `mermaid-js/zenuml-core` project.

This is the 1st-party grammar baseline for this skill. Generate diagrams that conform to this grammar (`mermaid-js/zenuml-core`), not to the standalone `zenuml.com` product or other renderers, unless the user says otherwise.

## Contents

- [Participants](#participants)
- [Messages](#messages)
- [Return values & assignment](#return-values--assignment)
- [Control flow](#control-flow)
- [Organization](#organization)
- [Comments & styling](#comments--styling)
- [Expressions & literals](#expressions--literals)
- [Starter annotation](#starter-annotation)

## Participants

Participants can be declared implicitly (just by using them in a message) or explicitly for more control:

```text
@Type <<Stereotype>> [emoji] ParticipantName Width as "Display Label" #COLOR
```

- Type annotations: `@Actor`, `@Boundary`, `@Control`, `@Entity`, `@Database`, `@Collections`, `@Queue`
- `as "Label"` sets a display alias distinct from the identifier
- `#FF5733` sets a hex color
- Emoji via shortcode (`[rocket]`) or a literal Unicode character
- Valid participant names follow Java/C identifier rules

Example:

```text
@Actor Alice #FF5733 as "End User"
@Database DB
```

## Messages

**Synchronous** (dot notation, shows an activation bar):

```text
A.methodName()
A -> B.methodName(arg1, arg2)
result = A.compute()
String result = A.compute()
```

Nested calls show nested activation boxes:

```text
A.process() {
  B.validate()
  C.persist()
}
```

Self-messages (no explicit target) must be wrapped in a nested block.

**Asynchronous** (colon syntax, open arrowhead, no activation bar):

```text
A -> B: message text
A --> B: response text   // reply arrow
```

**Object creation**:

```text
instance = new AClass(args)
```

## Return values & assignment

```text
return
return someValue
result = A.compute()
```

`return` exits the current activation. The assignment target on a call (`result = A.compute()`) is optional — omit it if the caller doesn't need the value.

## Control flow

Combined fragments render as boxes around grouped logic:

- **Conditional**: `if (condition) { ... } else if (condition) { ... } else { ... }`
- **Loops**: `while (condition) { ... }`, `for (...) { ... }`, `foreach (...) { ... }`, or bare `loop { ... }` — all rendered identically
- **Optional** (single-path alternative): `opt (condition) { ... }`
- **Parallel**: `par { statement1 statement2 }`
- **Critical section**: `critical (mutex) { ... }`
- **Error handling**: `try { ... } catch (ExceptionType e) { ... } finally { ... }` — multiple `catch` clauses are supported

Only use `try/catch`, `par`, or `critical` when the source description actually implies error handling, concurrency, or mutual exclusion — do not add them as decoration (see the skill's anti-pattern checklist).

## Organization

- **Sections**: `section(Label) { ... }` or an anonymous `{ ... }` block to group related statements. `Label` must be a single token: a bare identifier (`section(Checkout)`) or, for a multi-word human-readable label, a quoted string (`section("Checkout Flow")`). Never place multiple unquoted words directly inside the parentheses (e.g. `section(Checkout Flow)`) — the parser splits on whitespace and misparses each word as a separate statement. Even quoted correctly, `Label` is **not rendered anywhere** — verified against `zenuml-core`'s `src/parser/FrameBuilder.ts`, where `enterSection`/`enterAlt`/`enterOpt` all discard everything but the frame type (`{ type, left, right, children }`, no `label`/`title` field). The section box always shows a generic "Section" tab, regardless of what `Label` is. Don't rely on `Label` for a human-readable caption — use a `// comment` on the line above the section instead (comments do render as a diagram note).
- **Groups**: `group "Name" { participant1 participant2 }` visually clusters participant lifelines
- **Cross-diagram reference**: `ref(DiagramName)` links to another diagram instead of inlining it
- **Dividers**: `== Phase Label ==` draws a horizontal separator between logical sections

## Comments & styling

- Line comments: `// comment text` — attaches to the following statement and renders as a diagram note
- Unicode identifiers and emoji (shortcode `[rocket]` or literal character) are supported in names and labels
- Participant color/width/alias covered under [Participants](#participants)

## Expressions & literals

Conditions and arguments support:

- Comparisons: `==`, `!=`, `>=`, `<`, etc.
- Boolean operators: `&&`, `||`, `!`
- Arithmetic operators
- Literals: numbers, strings (`"$99.99"`), duration-like literals (`500ms`)
- Function calls as expressions

## Starter annotation

```text
@Starter(ParticipantName)
```

Designates which participant initiates the sequence, when it isn't obvious from message order alone.
