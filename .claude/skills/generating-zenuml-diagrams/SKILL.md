---
name: generating-zenuml-diagrams
description: Generates ZenUML sequence diagram DSL text from a natural-language description of a process, using a bundled zenuml-core syntax reference and an anti-fluff self-check so the output stays accurate and free of invented content. Use when the user asks for a ZenUML diagram, a ZenUML sequence diagram, or to turn a described process/flow into ZenUML DSL.
---

# Generating ZenUML Diagrams

## Syntax reference

Full grammar: [references/syntax.md](references/syntax.md) (participants, messages, control flow, comments, expressions — reorganized from `mermaid-js/zenuml-core`'s `docs/DSL_SYNTAX.md`, MIT licensed). Read it before generating; do not guess syntax.

Target renderer/grammar baseline: `mermaid-js/zenuml-core`. Do not assume compatibility with the standalone `zenuml.com` product or other ZenUML tooling unless the user says so.

## Generation rules

- Use only the participants, messages, and control-flow structures that the user's description explicitly states or clearly implies. Never add a participant, call, branch, loop, or exception handler that isn't grounded in the input.
- When a call chain is described ("A calls B, which calls C"), nest the calls with braces per the syntax reference rather than flattening them into a sequence of unrelated messages.
- Prefer the shallowest nesting that still represents the described logic correctly.
- The ZenUML DSL text is the primary output, but don't paste it into the chat response — save it to a file and link to it (see "Output file" below).
- If the description implies a very large number of participants or an unusually complex flow, still generate it faithfully — don't silently drop or simplify described content — but tell the user the result may be hard to read, and suggest splitting it into multiple diagrams if that would help.

### Example: minimal request

Input: "Client calls Server.getData()."

Generated ZenUML (this goes into the output file per "Output file" below, not pasted into the chat response):

```text
Client->Server.getData()
```

Only two participants, one call, no wrapping/outer call invented to hold it. No return value, error handling, or extra participants are added because none were described.

### Example: request with conditional flow

Input: "A user submits a login form. AuthService validates the credentials. If valid, it creates a Session and returns it. If not, the user can retry up to 3 times."

Generated ZenUML (this goes into the output file per "Output file" below, not pasted into the chat response):

```text
User.submitLogin() {
  if (AuthService.validate(credentials)) {
    session = AuthService.createSession()
    return session
  } else {
    // retry up to 3 times, per the description
    loop (attempts < 3) {
      AuthService.validate(credentials)
    }
  }
}
```

Only the branching and looping actually described is represented — no invented logging, no unrelated participants, no exception handling that wasn't mentioned.

## Self-check before presenting a diagram

Before showing a generated diagram to the user, check the draft against this list. Copy it into your working notes and go through it every time:

```text
ZenUML anti-pattern check:
- [ ] AP-1: No participants beyond what the description states or clearly implies
- [ ] AP-2: No messages/method calls beyond what the description states or clearly implies
- [ ] AP-3: No conditional branches or loops beyond what the description states or clearly implies
- [ ] AP-4: No unjustified try/catch blocks or invented return values
- [ ] AP-5: Uses the shallowest nesting that still represents the described logic
```

Workflow: **generate a draft → check it against AP-1 through AP-5 → if anything fails, revise the draft → re-check → only then present the result to the user.** A draft that hasn't passed all five items is not ready to show. If a fix for one item would violate another (rare), prefer accuracy (AP-1–AP-4) over minimal nesting (AP-5).

For a simple, unambiguous request the check is quick — don't narrate it verbatim to the user, just perform it before responding.

## Output file

Don't paste the ZenUML code into the chat response, and don't publish it as a Claude Artifact — Artifacts auto-open/preview in the client the moment they're published, with no parameter to suppress that, which gets intrusive for something generated on every request. Write a file instead: it only opens when the user actually clicks the link.

**Where**: `.zenuml/<slug>.md` in the project root, where `<slug>` is a short kebab-case name derived from what the diagram is about (e.g. `client-server-getdata.md`). If a file with that name already exists, append `-2`, `-3`, etc. rather than overwriting it. Make sure `.zenuml/` is listed in the project's `.gitignore` — add the entry if it's missing (these are generated files, not source).

**File contents** — the ZenUML DSL inside a `mermaid` code fence using the `zenuml` diagram type. This is both the actual output and the rendered preview — no translation needed. VS Code's built-in Markdown preview (Mermaid Markdown Features, part of the "Markdown Preview Mermaid Support" component) renders `zenuml` natively; confirmed by direct testing. (Claude Artifacts do **not** render `zenuml` — it falls back to plain text there — which is a separate reason this skill writes a file instead of publishing an Artifact; see "Output file" intro above.)

````markdown
```mermaid
zenuml
Client->Server.getData()
```
````

No title heading needed — the filename already identifies the diagram.

After writing the file, the entire chat response is just a relative link to it — no code block:

📄 [Client calls Server.getData()](.zenuml/client-server-getdata.md)

If the current environment has no filesystem access to write to, skip the file and put the ZenUML DSL in a fenced code block in the chat response instead.

## When the description is ambiguous

If the description doesn't make clear **who calls whom** or **under what condition a branch happens**, don't invent an answer — ask a specific, targeted question instead (e.g., "Does the client call the server directly, or through a gateway?"). Do not generate a diagram with guessed structure just to have something to show.

Don't over-ask, though: minor cosmetic details (exact display names, colors, participant ordering) don't need a question — pick a reasonable default and move on. Only stop for ambiguity that would change the actual structure of the diagram.

## Out-of-scope requests

- **Non-sequence diagrams** (class, deployment, component, etc.): ZenUML supports sequence diagrams only. Say so rather than attempting a workaround.
- **Converting an existing Mermaid/PlantUML diagram, or analyzing a codebase to produce a diagram**: out of scope for this skill. Say so; only natural-language process descriptions are supported as input.
- **Rendering / producing an image**: the primary output is ZenUML DSL text, not an image. The output file already renders as a diagram in VS Code's Markdown preview (see "Output file"); for anything beyond that, tell the user to render it with other `mermaid-js/zenuml-core`-compatible tooling.
