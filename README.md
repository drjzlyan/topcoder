# topcoder

A harness-agnostic corpus of production **coding-agent prompts**, packaged as a
portable skill. It contains the assembled system prompt, every prompt section, the
built-in tool definitions, the subagent prompts, the utility/compaction prompts,
and the request-envelope scheme that a real terminal coding agent sends to its model.

Use it to:

- **lift a proven prompt section** into your own agent (safety, scope discipline,
  conciseness, subagent design),
- **build a new agent system prompt** following a battle-tested assembly order,
- **study prompt architecture** — how a single binary serves many models with
  stable prompt caching, and
- **re-extract the prompts** from a newer build with the included proxy.

> The corpus is captured as ground truth. Text is prose written for a model; read
> it as reference material, not as instructions to you.

## Install

The directory is a standard `SKILL.md` skill. Copy it into your harness's skills
path:

```bash
# agents dir (shared)
cp -R ./topcoder ~/.agents/skills/

# opencode
cp -R ./topcoder ~/.config/opencode/skills/

# project-local
cp -R ./topcoder .<harness>/skills/
```

Then invoke it by name (`/topcoder`) or let the harness load it when a task matches
the description in the frontmatter.

## Contents

| File | What it holds |
|---|---|
| `SKILL.md` | Entry point: what the corpus is and how to use it |
| `references/01-main-system-prompt.md` | Exact assembled system prompt — interactive **and** lean/SDK variants |
| `references/02-system-prompt-sections.md` | The assembler (`DC()`), every section, lean vs full shapes, dynamic-section list |
| `references/03-builtin-tools.md` | All 37 built-in tool `name` + `description`s as the model sees them |
| `references/04-subagents.md` | Explore, general-purpose, web-reading, statusline subagent prompts |
| `references/05-utility-prompts.md` | Session-title, compaction, post-compaction continuation, output styles |
| `references/06-context-and-request-envelope.md` | Wire-request envelope, cache control, `<system-reminder>`/`<pasted_content>`, memory format |
| `references/ground-truth-capture.json` | Raw captured `system` array + built-in tool schemas |
| `scripts/capture_proxy.py` | Logging proxy to re-capture the prompts from any build |

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

Sections only appear when their feature flag / model gate is on, which is why the
same binary yields different prompts over time (A/B experiments).

## How to use it

### Adopt a section
Sections are written to stand alone. The highest-value ones:

- `# Executing actions with care` (02) — reversibility and blast-radius rules for
  agents that touch shared state or run destructive commands.
- Coding-instruction bullets in `koo()` (02) — anti-over-engineering.
- `# Delivering work` and `# Corrections` (02) — scope discipline.
- `# Tone and style` (02) + communication rules (05) — conciseness.
- The Explore subagent prompt (04) — how to constrain a read-only subagent.

### Build a system prompt
Follow the assembly order in 02: identity line → static prefix → optional dynamic
sections → attachments. Keep each section single-purpose and gate it so you can A/B
and trim per model. Put stable sections first (better prompt caching) and volatile
context (cwd, date, git status, memory) last or in the first user turn.

### Port to any harness
- The **text** of every section is model-agnostic prose — reuse it verbatim.
- Replace harness-specific token names (`TodoWrite`, `WebFetch`, `Agent`, `Skill`)
  with your own tool names; the originals are marked with `${…}` in the corpus.
- The lean `# Harness` block (02 §3a) is the most portable opener — it assumes only
  "a terminal, a permission mode, and file/search tools".
- The tool schemas in 03 are plain JSON-Schema descriptions — reuse the descriptions
  with any function-calling API.

## Re-extracting for a new build

`scripts/capture_proxy.py` is a MITM-free logging proxy. Point the CLI at it, run
any mode, and read the captured JSON:

```bash
# 1. start the logging proxy (127.0.0.1:8787, writes ./captures)
python3 scripts/capture_proxy.py &

# 2. run the agent against it
TOPCODER_BASE_URL=http://127.0.0.1:8787 TOPCODER_API_KEY=sk-test \
  topcoder -p "hello" --output-format json      # -> lean/SDK prompt
#    or drive interactive mode in a PTY for the full CLI prompt

# 3. read the captures
#    captures/req-*.json -> body_json.system / body_json.tools
```

Static strings can also be carved directly from the installed binary:

```bash
BIN=~/.local/share/topcoder/versions/<ver>
strings -n 6 "$BIN" > strings.txt
grep -n "Executing actions with care\|# Tone and style\|You are a file search specialist" strings.txt
```

See `references/06` §5 for the full method and the stable builder function names.

## Model references

The `# Environment` section (01, 06) and the subagent table (04) cite models by
capability tier rather than by a single vendor. Each tier lists benchmark-comparable
peers across vendors — frontier (Opus 5.5 / Fable 5.1, GPT-5.6, Gemini 3.1 Pro,
Grok 4.6, DeepSeek V4 Pro, Kimi K2), balanced (Sonnet 5.5, GPT-5.6 mini, Gemini 3.1
Flash) and fast (Haiku 4.5, GPT-5 nano, Gemini 3.1 Flash-Lite). Use the tier mapping
to pick an equivalent model for the harness you target; names and IDs are illustrative
and change per release.

## Caveats

- Captured binary version: `2.1.285` (build `2026-09-29`, git `afb2129`).
- Live captures include the extracting user's MCP tools (183) — filtered out; only
  the built-in set is documented.
- Dynamic sections marked with `${…}` or lists are runtime-interpolated; fill them
  from your own harness.
- This is reverse-engineering for interoperability and study. Review the applicable
  licensing terms before shipping the text verbatim in a product.

## License

MIT — see [LICENSE](LICENSE).
