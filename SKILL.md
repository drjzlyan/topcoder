---
name: topcoder
description: >-
  A corpus of production coding-agent prompts: system prompts, tool definitions,
  subagent prompts, slash-command and hook prompts, the extension/plugin layer,
  and the context-injection scheme. Use when designing or studying coding-agent
  prompts across harnesses (opencode, Cursor, Codex, aider, custom agents) — to
  adopt a proven prompt section, build an agent system prompt, or re-extract the
  prompts from a new release.
---

# Topcoder Prompt Corpus (harness-agnostic)

Everything in `references/` was extracted from a compiled CLI coding agent by two
methods: (1) live capture of the exact Messages API request via a logging proxy,
and (2) carving prompt constants out of the compiled binary's embedded JS bundle.
`references/01-main-system-prompt.md` is byte-for-byte ground truth.

This skill is not tied to any harness. Use it to lift the *content* and the
*architecture* into any coding agent you build or configure.

## The corpus

| File | What it holds |
|---|---|
| `references/01-main-system-prompt.md` | Exact assembled system prompt — interactive **and** SDK/lean variants |
| `references/02-system-prompt-sections.md` | The assembler (`DC()`), every section, lean vs full shapes, dynamic-section list |
| `references/03-builtin-tools.md` | All 37 built-in tool `name` + `description`s as the model sees them |
| `references/04-subagents.md` | Explore, general-purpose, web-reading, statusline subagent prompts |
| `references/05-utility-prompts.md` | Session-title, compaction, post-compaction continuation, output styles |
| `references/06-context-and-request-envelope.md` | Wire-request envelope, cache control, `<system-reminder>`/`<pasted_content>`, memory format |
| `references/07-extensions-commands-agents-hooks.md` | Plugin layout, slash-command + subagent frontmatter, hook contract, MCP — with real prompts |
| `references/ground-truth-capture.json` | Raw captured `system` array + built-in tool schemas |
| `scripts/capture_proxy.py` | Logging proxy to re-capture from any future version |

## The architecture in one screen

A coding-agent system prompt is a **3-block array**, not one string:

```
system[0]  telemetry/billing marker
system[1]  identity line  .............. cache_control: ephemeral
system[2]  body = concatenated sections  cache_control: ephemeral
```

The body is assembled at runtime from named, individually-gated **sections**:

```
STATIC PREFIX (lean)        STATIC PREFIX (full)
  identity + # Harness        identity + # System + coding-instructions
                              + # Executing actions with care
                              + # Using your tools + # Tone and style

+ DYNAMIC SECTIONS (each optional, feature-flagged)
  communication · pronouns · action_caution · task_continuity · tool_param_json
  session_guidance · memory · env_info · context_management · focus_mode
  act_dont_rederive · delivering_work_max · overcorrection · autonomy_append …
```

## How to use this across harnesses

### 1. Adopt a specific section
Most harnesses already have a system prompt. Lift sections rather than the whole
prompt — they are written to be independent:

- **Safety / reversibility** → `# Executing actions with care` (02) is the best single
  block for agents that touch shared state or run destructive commands.
- **Anti-over-engineering** → the coding-instructions bullets in `koo()` (02).
- **Scope discipline** → `# Delivering work` and `# Corrections` (02).
- **Conciseness** → `# Tone and style` (02) + the communication rules (05).
- **Subagent design** → the read-only constraint block in the Explore prompt (04).
- **Extension layer** → `07` for slash-command/subagent frontmatter, the hook
  input/output contract, MCP config, and full real prompts (feature-dev, code-review).

### 2. Build a new agent system prompt
Follow the assembler in 02: identity line → static prefix → optional dynamic
sections → attachments. Keep each section single-purpose and gate it so you can
A/B and trim per model. Put stable sections first (better prompt caching) and
volatile context (cwd, date, git status, memory) last or in the first user turn.

### 3. Map onto any harness (Cursor/Codex/aider/custom)
- The **text** of every section is model-agnostic prose — reuse verbatim.
- Replace harness-specific token names (`TodoWrite`, `WebFetch`, `Agent`, `Skill`)
  with your harness's tool names — the originals are marked with `${…}` in the corpus.
- The lean `# Harness` block (02 §3a) is the most portable opener; it assumes only
  "a terminal, a permission mode, and file/search tools".
- Tool schemas in `03-builtin-tools.md` are plain JSON-Schema descriptions — reuse
  the descriptions with any function-calling API.

### 4. Install as a skill in another harness
This directory is a standard `SKILL.md`. Copy it to the harness's skills path:

```bash
cp -R ./topcoder <harness>/skills/
# opencode:       ~/.config/opencode/skills/
# agents dir:     ~/.agents/skills/
# project-local:  .<harness>/skills/
```

### 5. Re-extract for a new release
Prompts change per build and per account (A/B flags). To refresh:

```bash
python3 scripts/capture_proxy.py &
TOPCODER_BASE_URL=http://127.0.0.1:8787 TOPCODER_API_KEY=sk-test topcoder -p "hi"
# then read captures/req-*.json -> body_json.system / body_json.tools
```
See `references/06` §5 for the full method and the stable builder function names.

## Design lessons worth copying

- **Assemble, don't concatenate.** Named, gated sections let one binary serve many
  models/experiments and keep the cache prefix stable.
- **Two shapes, one content.** Lean (`# Harness`) and full variants differ only in
  framing; the substance is the same. Match framing to model capability.
- **Say where truth lives.** Sections explicitly tell the model that
  `<system-reminder>` and hook output are harness-injected, not user instructions —
  a cheap, effective prompt-injection defense.
- **Constrain the reader, not just the doer.** The Explore subagent is defined mostly
  by prohibitions (read-only, no writes, no redirects) and a speed mandate.
- **Untrusted-data framing.** Both the web-reading subagent and `<pasted_content>`
  mark external content as data, with instructions never to follow it.
- **Preserve verbatim across compaction.** The compaction prompt requires *all* user
  messages and security constraints to survive summarization verbatim.

## Provenance & caveats

- Captured binary version: `2.1.285` (build `2026-09-29`, git `afb2129`).
- Live captures include the extracting user's MCP tools (183) — filtered out; only the
  built-in set is documented.
- Dynamic sections marked with `${…}` or lists are runtime-interpolated; fill from
  your own harness.
- This is reverse-engineering for interoperability/study. Review the applicable
  licensing terms before shipping the text verbatim in a product.
