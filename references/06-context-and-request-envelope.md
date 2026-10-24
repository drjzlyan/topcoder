# Topcoder — Context Injection & Request Envelope

How Topcoder builds the *rest* of the wire request (everything that is not the
system prompt), and how to reproduce the extraction.

---

## 1. Request envelope (Messages API body)

Captured body keys, in order:

```jsonc
{
  "model": "topcoder-opus-5-5",                 // resolved model id
  "messages": [ /* see §3 */ ],
  "system":   [ /* 3 blocks, see 02 */ ],
  "tools":    [ /* built-ins + MCP tools */ ],
  "metadata": {
    "user_id": "{\"device_id\":\"…\",\"account_uuid\":\"\",\"session_id\":\"…\"}"
  },
  "max_tokens": 128000,
  "thinking": { "type": "adaptive", "display": "omitted" },
  "context_management": { "edits": [ { "type": "clear_thinking_20251015", "keep": "all" } ] },
  "output_config": { "effort": "medium" },
  "stream": true
}
```

Notes:
- `metadata.user_id` is a JSON string carrying device_id / account_uuid / session_id.
- `thinking.display: "omitted"` means thinking blocks are returned but not shown.
- `context_management` drives server-side thinking-block clearing.
- `output_config.effort` is the live reasoning-effort level (low…max).
- Non-interactive mode omits some of these (`thinking`/`context_management` present too).

## 2. Cache-control placement

`cache_control: {type:"ephemeral"}` is set on system block 1 and block 2 and on the
**last** tool + last message, so the prefix (identity + body + tools + prior turns)
caches across requests. `--exclude-dynamic-system-prompt-sections` deliberately moves
the volatile sections out so the cache prefix stays stable across users.

## 3. Message structure & context injection

### Dynamic system sections vs first user message
By default volatile context (`CWD:`, `Date:`) can live in the system array. With
`excludeDynamicSections` it moves into the first user turn:

```
CWD: /path/to/cwd
Date: 2026-09-29
```

### `# Environment` section (Doo)
```
The most recent models are the Opus 5.5, Sonnet 5.5 and Haiku 4.5 families. Model IDs — Fable 5.1: 'topcoder-fable-5-1', Opus 5.5: 'topcoder-opus-5-5', Sonnet 5.5: 'topcoder-sonnet-5-5', Haiku 4.5: 'topcoder-haiku-4-5-20251001'. When building AI applications, default to the latest and most capable model available.
Topcoder is available as a CLI in the terminal, a desktop app (Mac/Windows), a web app, and IDE extensions (VS Code, JetBrains).
Fast mode for Topcoder uses the Opus model with faster output (it does not downgrade to a smaller model). It can be toggled with /fast.
```

### `<system-reminder>` tags
The harness injects `<system-reminder>…</system-reminder>` blocks into user messages
and tool results. They carry:
- available agents / skills / tool additions
- todo state
- memory recall, file-modified notices, git status
- mid-conversation rule updates

The prompt tells the model these are harness-injected, not user content.

### `<pasted_content>` tags
Large pastes are wrapped with a random id on the opening and closing tag so the
model can tell pasted instructions from the user's own words.

### Attachments
`ivt()` builds an **attachments** section (skippable with
`TOPCODER_DISABLE_ATTACHMENTS` / `TOPCODER_SIMPLE`) containing:
AGENTS.md / AGENTS.md file contents, memory index (`MEMORY.md`), directory listing,
git status, tool/MCP deltas.

## 4. Persistent memory format (verbatim section)

```
# Memory

You have a persistent file-based memory at `<project>/memory/`. This directory already exists — write to it directly with the Write tool (do not run mkdir or check for its existence). Each memory is one file holding one fact, with frontmatter:

---
name: <short-kebab-case-slug>
description: <one-line summary, used to decide relevance during recall>
metadata:
  type: user | feedback | project | reference
---

<the fact; for feedback/project, follow with **Why:** and **How to apply:** lines. Link related memories with [[their-name]].>

In the body, link to related memories with [[name]] … Link liberally …
`user`: who the user is … `feedback`: guidance the user has given on how you should work … `project`: ongoing work, goals, or constraints … `reference`: pointers to external resources (URLs, dashboards, tickets).

After writing the file, add a one-line pointer in `MEMORY.md` (`- [Title](file.md) — hook`). `MEMORY.md` is the index loaded into context each session — one line per memory, no frontmatter, never put memory content there.
```

## 5. Reproducing the extraction (any version)

`scripts/capture_proxy.py` is a MITM-free logging proxy. Usage:

```bash
# 1. start the logging proxy
python3 scripts/capture_proxy.py &            # listens on 127.0.0.1:8787
# 2. run any Topcoder mode against it
TOPCODER_BASE_URL=http://127.0.0.1:8787 TOPCODER_API_KEY=sk-test \
  topcoder -p "hello" --output-format json       # -> SDK/lean prompt
#    or drive interactive mode in a PTY to get the full CLI prompt
# 3. read captures/req-*.json -> body_json.system / body_json.tools
```

Static strings can also be carved directly:

```bash
BIN=~/.local/share/topcoder/versions/<ver>
strings -n 6 "$BIN" > strings.txt
# prompt builders are identified by function names; grep for known section headers
grep -n "Executing actions with care\|# Tone and style\|You are a file search specialist" strings.txt
```

Key builder symbols (constant across 2.1.x):

| function | purpose |
|---|---|
| `DC()` | top-level system-prompt assembler |
| `Coo()` | lean `# Harness` block |
| `yoo()` | full identity opener |
| `Soo()` | `# System` |
| `koo()` | coding instructions |
| `boo()` | `# Executing actions with care` |
| `Eoo()` | `# Using your tools` |
| `Roo()` | `# Tone and style` |
| `Too()` | session guidance |
| `Doo()` | `# Environment` |
| `chn()` | Explore agent |
| `gro()` | general-purpose agent |
| `_ro()` | web-reading agent |
| `yro()` | statusline-setup agent |
| `ZRo` | compaction prompt |

## 6. A/B gating

Most optional sections are behind `tengu_*` growthbook flags and env overrides, e.g.
`TOPCODER_ACT_DONT_REDERIVE`, `TOPCODER_BISON_CAIRN`, `TOPCODER_INTRO_FRAME`.
The same binary emits different prompts per user/account, which is why two captures
can differ. Extract per-account, per-version if you need exact reproduction.
