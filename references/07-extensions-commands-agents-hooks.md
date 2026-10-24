# Extensions — Plugins, Commands, Subagents, Hooks & MCP

The core system prompt (01–06) is only part of the surface. A modern coding agent
also exposes an **extension layer**: slash commands, subagents, event hooks, skills,
and MCP servers, each with its own prompt/schema shape. This reference captures those
shapes and the concrete prompts shipped in the agent's official plugin set.

> Source: the bundled plugin marketplace (`plugins/*`, `.topcoder-plugin/marketplace.json`)
> plus `examples/hooks`. Text is reproduced for reference, rebranded to the harness.

---

## 1. Plugin layout & manifest

A plugin is a directory with **automatic component discovery**:

```
plugin-name/
├── .topcoder-plugin/
│   └── plugin.json          # Required manifest
├── commands/                # Slash commands (*.md)
├── agents/                  # Subagent definitions (*.md)
├── skills/                  # Skills (<name>/SKILL.md)
├── hooks/
│   └── hooks.json           # Event handler config
├── .mcp.json                # MCP server definitions
└── scripts/                 # Helper scripts
```

Rules:

- `plugin.json` lives in `.topcoder-plugin/`; component dirs sit at the **plugin root**.
- Only create the directories the plugin uses.
- kebab-case for every file and directory name.

Minimal manifest:

```json
{ "name": "plugin-name" }
```

Fuller manifest:

```json
{
  "name": "plugin-name",
  "version": "1.0.0",
  "description": "Brief explanation of purpose",
  "author": { "name": "Author", "email": "author@example.com" },
  "commands": "./custom-commands",
  "agents": ["./agents", "./specialized-agents"],
  "hooks": "./config/hooks.json",
  "mcpServers": "./.mcp.json"
}
```

Custom component paths **supplement** the defaults (they don't replace them), must be
relative and start with `./`. Use the `${TOPCODER_PLUGIN_ROOT}` env var — never hardcode
absolute paths — for hook commands, MCP args, script refs, and resource files.

## 2. Slash commands

A slash command is a Markdown file whose body becomes the agent's instructions when
the user types `/name`.

**Commands are instructions *for the agent*, not messages to the user.** Write
directives ("Review this code for SQLi, XSS, auth bypass; give line numbers and
severity"), not narration ("This command will review your code…").

Locations & namespacing:

| Scope | Location | Label in `/help` |
|---|---|---|
| Project | `.topcoder/commands/` | `(project)` |
| Personal | `~/.topcoder/commands/` | `(user)` |
| Plugin | `plugin-name/commands/` | `(plugin-name)` |

Subdirectories namespace: `commands/ci/build.md` → `/build (project:ci)`.

### Frontmatter fields

| Field | Purpose | Type / values |
|---|---|---|
| `description` | Shown in `/help` (≤60 chars) | string |
| `allowed-tools` | Tool allowlist for the command | `Read, Grep, Bash(git:*)` |
| `model` | Model for the command | `sonnet` / `opus` / `haiku` |
| `argument-hint` | Autocomplete hint | `[pr-number] [priority]` |
| `disable-model-invocation` | Block programmatic invocation | boolean |

### Dynamic features

- `$ARGUMENTS` — everything passed after the command.
- `$1`, `$2`, … — positional arguments.
- `@path/to/file` — inline a file's contents before processing.
- `` !`cmd` `` — run a bash command inline to gather context (gate via `allowed-tools`).
- `$IF($1, …, …)` — conditional expansion (guard missing args).

### Real command: `feature-dev` (7-phase workflow)

```markdown
---
description: Guided feature development with codebase understanding and architecture focus
argument-hint: Optional feature description
---

# Feature Development

You are helping a developer implement a new feature. Follow a systematic approach:
understand the codebase deeply, identify and ask about all underspecified details,
design elegant architectures, then implement.

## Core Principles
- Ask clarifying questions: identify ambiguities, edge cases, underspecified
  behaviors. Ask concrete questions and wait for answers before implementing.
- Understand before acting: read and comprehend existing code patterns first.
- Read files identified by agents: after agents return, read the key files they list.
- Simple and elegant: readable, maintainable, architecturally sound code.
- Use TodoWrite: track all progress.

## Phase 1: Discovery
Goal: understand what needs to be built. Initial request: $ARGUMENTS
1. Create a todo list with all phases.
2. If the feature is unclear, ask what problem is being solved, what it should do,
   and any constraints.
3. Summarize understanding and confirm with the user.

## Phase 2: Codebase Exploration
1. Launch 2–3 code-explorer agents in parallel, each targeting a different aspect
   (similar features, high-level understanding, architecture, UX) and returning a
   list of 5–10 key files to read.
2. Read every file the agents identify to build deep understanding.
3. Present a summary of findings and patterns.

## Phase 3: Clarifying Questions  (DO NOT SKIP)
Identify underspecified aspects — edge cases, error handling, integration points,
scope boundaries, backward compatibility, performance — present them as one organized
list, and wait for answers before designing. If the user says "whatever you think is
best", give a recommendation and get explicit confirmation.

## Phase 4: Architecture Design
Launch 2–3 code-architect agents in parallel with different focuses (minimal changes
vs clean architecture vs pragmatic balance). Present each approach, a trade-off
comparison, and **your recommendation with reasoning**; ask which they prefer.

## Phase 5: Implementation  (DO NOT START WITHOUT USER APPROVAL)
Read the relevant files, implement the chosen architecture, follow codebase
conventions strictly, keep todos updated.

## Phase 6: Quality Review
Launch 3 code-reviewer agents in parallel (simplicity/DRY/elegance; bugs/functional
correctness; conventions/abstractions). Consolidate findings, surface the
highest-severity issues, and ask what to fix.

## Phase 7: Summary
Mark todos complete and summarize: what was built, key decisions, files modified,
suggested next steps.
```

### Real command: `code-review` (multi-agent PR review)

```markdown
---
allowed-tools: Bash(gh issue view:*), Bash(gh search:*), Bash(gh pr comment:*),
  Bash(gh pr diff:*), Bash(gh pr view:*), mcp__github_inline_comment__create_inline_comment
description: Code review a pull request
---

Provide a code review for the given pull request.

Agent assumptions: all tools work without error; do not test tools or make
exploratory calls; only call a tool when required.

1. Launch a haiku agent to check whether the PR is closed/draft, needs no review,
   or already has a review comment from the agent. If so, stop.
2. Launch a haiku agent to return file paths (not contents) of relevant AGENTS.md
   files (root + any in directories the PR modifies).
3. Launch a sonnet agent to summarize the changes.
4. Launch 4 agents in parallel: agents 1+2 audit AGENTS.md compliance (sonnet);
   agents 3+4 hunt bugs in the diff (opus). CRITICAL: only HIGH-SIGNAL issues —
   compile/parse failures, definite wrong results, unambiguous rule violations.
   Do NOT flag style, input-dependent maybes, or subjective suggestions. False
   positives erode trust.
5. For each issue from 3+4, launch a validation subagent to confirm it is real.
6. Filter to validated issues only.
7. Summarize to the terminal; post GitHub comments only with `--comment`.
```

The false-positive list and the "one comment per unique issue" rule are the load-
bearing parts: they turn a noisy reviewer into a high-signal one.

### Common command patterns

```markdown
# Review: pull changed files into context, then instruct
Files changed: !`git diff --name-only`
Review each file for code quality, bugs, test coverage, documentation.

# Docs: inline the target file
Generate comprehensive documentation for @$1 including function/class descriptions,
parameters, return values, usage examples, edge cases.

# Validate: fail fast with a helpful message
Validate environment: !`echo "$1" | grep -E "^(dev|staging|prod)$" || echo "INVALID"`
If $1 is valid, deploy to $1. Otherwise list valid environments and show usage.
```

## 3. Subagents

A subagent is a Markdown file with frontmatter plus a **system prompt body** that
becomes the agent's own system prompt. Description triggers it; the body defines it.

### Frontmatter

| Field | Required | Notes |
|---|---|---|
| `name` | yes | lowercase-hyphens, 3–50 chars, start/end alphanumeric |
| `description` | yes | **the trigger** — see below — 10–5,000 chars |
| `model` | yes | `inherit` (recommended) / `sonnet` / `opus` / `haiku` |
| `color` | yes | `blue` `cyan` `green` `yellow` `magenta` `red` |
| `tools` | no | array; omit ⇒ all tools. Least privilege. |

The **description** is the most critical field. It must state when to trigger and
include 2–4 `<example>` blocks with a `<commentary>` explaining why the agent fires:

```markdown
description: Use this agent when [conditions]. Examples:

<example>
Context: [situation]
user: "[request]"
assistant: "[how the agent is used]"
<commentary>[why this triggers the agent]</commentary>
</example>
```

### System-prompt design template

```markdown
You are [role] specializing in [domain].

**Your Core Responsibilities:**
1. [primary]  2. [secondary]

**Analysis Process:**
1. [step]  2. [step]  3. [step]

**Quality Standards:** [standards]

**Output Format:** [what to return, how structured]

**Edge Cases:** [case → handling]
```

Write in second person, be specific, keep it under ~10,000 characters.

### Real agents

`code-architect` — decisive feature blueprints:

```markdown
---
name: code-architect
description: Designs feature architectures by analyzing existing codebase patterns and
  conventions, then providing comprehensive implementation blueprints with specific files
  to create/modify, component designs, data flows, and build sequences
tools: Glob, Grep, LS, Read, NotebookRead, WebFetch, TodoWrite, WebSearch
model: sonnet
color: green
---

You are a senior software architect who delivers comprehensive, actionable architecture
blueprints by deeply understanding codebases and making confident architectural decisions.

## Core Process
1. Codebase Pattern Analysis — extract patterns, conventions, stack, module boundaries,
   abstraction layers, and AGENTS.md guidelines; find similar features.
2. Architecture Design — make decisive choices; pick one approach and commit; design for
   testability, performance, maintainability.
3. Complete Implementation Blueprint — every file to create/modify, responsibilities,
   integration points, data flow, phased build sequence.

## Output Guidance
- Patterns & Conventions Found (with file:line references)
- Architecture Decision (rationale + trade-offs)
- Component Design (path, responsibilities, dependencies, interfaces)
- Implementation Map (files + detailed changes)
- Data Flow (entry → transformations → output)
- Build Sequence (phased checklist)
- Critical Details (error handling, state, testing, performance, security)

Make confident choices rather than presenting multiple options. Be specific and
actionable — file paths, function names, concrete steps.
```

`code-explorer` — read-only feature tracing:

```markdown
---
name: code-explorer
description: Deeply analyzes existing codebase features by tracing execution paths,
  mapping architecture layers, understanding patterns and abstractions, and documenting
  dependencies to inform new development
tools: Glob, Grep, LS, Read, NotebookRead, WebFetch, TodoWrite, WebSearch
model: sonnet
color: yellow
---

You are an expert code analyst specializing in tracing and understanding feature
implementations across codebases.

## Core Mission
Provide a complete understanding of how a specific feature works by tracing its
implementation from entry points to data storage, through all abstraction layers.

## Analysis Approach
1. Feature Discovery — entry points, core files, boundaries, configuration.
2. Code Flow Tracing — call chains, data transformations, dependencies, side effects.
3. Architecture Analysis — layers, patterns, interfaces, cross-cutting concerns.
4. Implementation Details — algorithms, error handling, performance, technical debt.

## Output Guidance
Entry points with file:line; step-by-step flow; key components; architecture insights;
dependencies; strengths/issues/opportunities; and a list of files essential to
understanding the topic. Always include specific file paths and line numbers.
```

`code-reviewer` — confidence-scored review (the anti-false-positive pattern):

```markdown
---
name: code-reviewer
description: Reviews code for bugs, logic errors, security vulnerabilities, code quality
  issues, and adherence to project conventions, using confidence-based filtering to
  report only high-priority issues that truly matter
tools: Glob, Grep, LS, Read, NotebookRead, WebFetch, TodoWrite, WebSearch
model: sonnet
color: red
---

You are an expert code reviewer. Review code against project guidelines in AGENTS.md
with high precision to minimize false positives.

## Review Scope
By default, review unstaged changes from `git diff`; the user may specify a scope.

## Core Responsibilities
Project-guideline compliance; bug detection (logic errors, null handling, races, leaks,
security, performance); code quality (duplication, missing error handling, tests).

## Confidence Scoring (0–100)
0 = false positive; 25 = maybe; 50 = real but minor; 75 = verified & important;
100 = certainly real and frequent. **Only report issues with confidence ≥ 80.**

## Output Guidance
State what you're reviewing. For each high-confidence issue give: description + score,
file:line, the guideline reference or bug explanation, and a concrete fix. Group by
severity (Critical vs Important). If nothing qualifies, say the code meets standards.
```

### AI-assisted agent generation prompt

The agent ships a generation prompt that turns a natural-language request into an
agent definition:

```
Create an agent configuration based on this request: "[DESCRIPTION]"

Requirements:
1. Extract core intent and responsibilities.
2. Design an expert persona for the domain.
3. Create a comprehensive system prompt with clear behavioral boundaries, specific
   methodologies, edge-case handling, and an output format.
4. Create an identifier (lowercase, hyphens, 3–50 chars).
5. Write a description with triggering conditions.
6. Include 2–3 <example> blocks showing when to use it.

Return JSON:
{ "identifier": "agent-name",
  "whenToUse": "Use this agent when... Examples: <example>...</example>",
  "systemPrompt": "You are..." }
```

## 4. Hooks

Hooks are event-driven automation. Two kinds:

- **Prompt-based (recommended)** — an LLM decides, context-aware:
  `{"type":"prompt","prompt":"Evaluate if this tool use is appropriate: $TOOL_INPUT","timeout":30}`
  Supported on: Stop, SubagentStop, UserPromptSubmit, PreToolUse.
- **Command** — deterministic shell: `{"type":"command","command":"bash ${TOPCODER_PLUGIN_ROOT}/scripts/validate.sh","timeout":60}`

### Events

| Event | When | Use for |
|---|---|---|
| PreToolUse | before a tool | validate / modify / approve–deny |
| PostToolUse | after a tool | feedback, logging |
| UserPromptSubmit | user sends a prompt | add context, validate, block |
| Stop | main agent stops | completeness check |
| SubagentStop | subagent stops | task validation |
| SessionStart | session begins | load context, set env |
| SessionEnd | session ends | cleanup, logging |
| PreCompact | before compaction | preserve critical context |
| Notification | user notified | reactions, logging |

### Config formats

Plugin `hooks/hooks.json` uses a **wrapper**:

```json
{
  "description": "Hookify plugin - user-configurable hooks from .local.md files",
  "hooks": {
    "PreToolUse": [{ "hooks": [{ "type": "command",
      "command": "python3 ${TOPCODER_PLUGIN_ROOT}/hooks/pretooluse.py", "timeout": 10 }] }],
    "PostToolUse": [{ "hooks": [{ "type": "command",
      "command": "python3 ${TOPCODER_PLUGIN_ROOT}/hooks/posttooluse.py", "timeout": 10 }] }],
    "Stop": [{ "hooks": [{ "type": "command",
      "command": "python3 ${TOPCODER_PLUGIN_ROOT}/hooks/stop.py", "timeout": 10 }] }],
    "UserPromptSubmit": [{ "hooks": [{ "type": "command",
      "command": "python3 ${TOPCODER_PLUGIN_ROOT}/hooks/userpromptsubmit.py", "timeout": 10 }] }]
  }
}
```

User settings (`.topcoder/settings.json`) use the **direct** format — events at top
level, no wrapper.

A hook with a `matcher` targets tools: `"Write"`, `"Write|Edit"`, `"*"`,
`"mcp__.*"` (case-sensitive).

### Input / output contract

Hooks receive JSON on stdin:

```json
{ "session_id": "…", "transcript_path": "…", "cwd": "…",
  "permission_mode": "ask|allow", "hook_event_name": "PreToolUse",
  "tool_name": "Write", "tool_input": {…}, "tool_result": {…} }
```

Prompt fields are available as `$TOOL_INPUT`, `$TOOL_RESULT`, `$USER_PROMPT`.

`PreToolUse` output:

```json
{ "hookSpecificOutput": { "permissionDecision": "allow|deny|ask",
                          "updatedInput": { "field": "modified" } },
  "systemMessage": "Explanation for the model" }
```

`Stop` output decides whether the agent may stop: `{"decision":"approve|block","reason":"…"}`.
Exit codes: `0` success (stdout shown), `2` blocking error (stderr fed back).

Env vars in command hooks: `$TOPCODER_PROJECT_DIR`, `$TOPCODER_PLUGIN_ROOT`,
`$TOPCODER_ENV_FILE` (SessionStart; append `export …` lines to persist), and
`$TOPCODER_REMOTE`. All matching hooks run **in parallel** and never see each
other's output — design for independence.

A robust command-hook skeleton:

```python
#!/usr/bin/env python3
"""PreToolUse hook: evaluate rules, never block on internal error."""
import os, sys, json
root = os.environ.get("TOPCODER_PLUGIN_ROOT")
if root and os.path.dirname(root) not in sys.path:
    sys.path.insert(0, os.path.dirname(root))
try:
    from core.rule_engine import RuleEngine
except ImportError as e:
    print(json.dumps({"systemMessage": f"import error: {e}"})); sys.exit(0)
try:
    data = json.load(sys.stdin)
    tool = data.get("tool_name", "")
    event = "bash" if tool == "Bash" else "file" if tool in ("Edit", "Write") else None
    print(json.dumps(RuleEngine().evaluate_rules(event=event, data=data)))
except Exception as e:
    print(json.dumps({"systemMessage": f"hook error: {e}"}))
finally:
    sys.exit(0)   # ALWAYS exit 0 — never block on hook failure
```

**Lifecycle:** hooks load at session start; editing config requires a restart, and
invalid JSON fails loading. Test with `<cli> --debug` and `/hooks`.

## 5. MCP servers

`.mcp.json` at plugin root (or inline under `mcpServers` in `plugin.json`):

```json
{
  "mcpServers": {
    "server-name": {
      "command": "node",
      "args": ["${TOPCODER_PLUGIN_ROOT}/servers/server.js"],
      "env": { "API_KEY": "${API_KEY}" }
    }
  }
}
```

Server transports: **stdio** (local), **SSE** (hosted/OAuth), **HTTP** (REST),
**WebSocket** (real-time). Tools surface to the model as `mcp__<server>__<tool>`;
prompts and commands reference them by that name (e.g.
`mcp__github_inline_comment__create_inline_comment`). Prefer HTTPS/WSS and inject
credentials via env vars.

## 6. Design lessons worth copying

- **Components are prompts with conventions.** A directory layout plus frontmatter
  fields is enough to auto-discover commands, agents, skills and hooks — no central
  registry to keep in sync.
- **The description is the API.** For both commands and agents, the trigger text
  (with `<example>` blocks) does more work than the body. Write it first.
- **Confidence scoring beats heuristics.** A 0–100 score with a ≥80 cutoff is a
  compact, model-agnostic way to suppress false positives in review-style agents.
- **Prompt hooks for judgment, command hooks for facts.** Let an LLM decide when the
  rule is fuzzy; use deterministic shell when it isn't.
- **Fail open, never wedged.** Hooks exit 0 on internal error so a broken gate cannot
  block all work — a deliberate availability-over-strictness trade.
- **Parallel, order-free hooks.** Matching hooks run concurrently and can't see each
  other; contracts must be independent and idempotent.
- **Portable paths.** `${TOPCODER_PLUGIN_ROOT}` everywhere so a plugin works from any
  install location.
