# Capability mapping & replacements

The corpus (01–07) names capabilities that are specific to the reference harness:
built-in tools (`TodoWrite`, `WebFetch`, `Agent`, `Artifact`, …), skills
(`artifact-design`, `code-review`, the `plugin-dev` set, …), and MCP servers
(`mcp__browser__*`, `mcp__github_*`). This reference tells you how to **resolve each
name** in another harness — either by **reusing the original directly** or by
**substituting a maintained equivalent** — with as little functional loss as possible.

> Repo identifiers below are the verbatim proper nouns of third-party projects, given
> so you can verify activity yourself. Star counts and last-push dates are as of
> **2026-10-24** and drift; re-check before adopting.

## 1. Resolution procedure

For every harness-specific name in the corpus, in order:

1. **Reuse directly if the harness speaks the format.** The extension formats in 07
   (`SKILL.md` skills, `agents/*.md`, `commands/*.md`, `hooks/hooks.json`, `.mcp.json`)
   are portable. If the target harness loads them, the same skills, subagents, commands
   and MCP servers work unchanged — nothing to replace.
2. **Map tool names to native equivalents** (§2). Most reference-harness built-ins have
   a one-to-one native tool in modern harnesses (opencode, Cursor, Codex, …).
3. **Replace anything not native** with a maintained equivalent (§3–§4), preferring
   the selection criteria in §6.
4. **Never silently drop a capability.** If nothing replaces it, name the closest
   substitute and state the residual loss (§5).

## 2. Built-in tool → native equivalent (direct reuse)

| Reference tool | Purpose | Native equivalent (opencode-style) |
|---|---|---|
| `TodoWrite` | task list | `todowrite` |
| `Task` / `Agent` | subagents | `task` (subagent_type) |
| `WebFetch` | fetch a URL | `webfetch` / `brightdatav scrape_as_markdown` |
| `WebSearch` | web search | `brightdatav search_engine` or a search MCP (§3) |
| `Read` `Write` `Edit` `MultiEdit` | file ops | `read` `write` `edit` |
| `Glob` `Grep` `LS` | find / search / list | `glob` `grep` |
| `Bash` `KillShell` `BashOutput` `Monitor` | shell + process control | `bash` (background + timeout) |
| `Skill` | invoke a skill | `skill` |
| `AskUserQuestion` | ask the user | `question` |
| `EnterPlanMode` / `ExitPlanMode` | plan mode | plan agent / built-in plan mode |
| `EnterWorktree` / `ExitWorktree` | git worktree isolation | `git worktree` (native) |
| `NotebookEdit` | edit notebooks | Jupyter MCP (§3) |
| `LSP` | code intelligence | Serena (§3) |
| `CronCreate` / `CronDelete` / `CronList` | scheduled prompts | system `cron`/`at`, or a scheduler MCP |
| `SendMessage` `TaskStop` `WaitForMcpServers` | agent/MCP orchestration | harness-native or dropped (see §5) |

## 3. Capability replacements (MCP servers)

| Corpus capability | Replace with | Repo | ★ | Last push |
|---|---|---|---|---|
| Browser automation (`mcp__browser__*`) | Chrome DevTools MCP | `ChromeDevTools/chrome-devtools-mcp` | 54.1k | 2026-10-23 |
| Browser automation (alt) | Playwright MCP (Microsoft) | `microsoft/playwright-mcp` | 38.6k | 2026-10-22 |
| GitHub / PR inline comments | GitHub MCP Server (official) | `github/github-mcp-server` | 33.9k | 2026-10-23 |
| Filesystem · fetch · git · memory · time | Reference servers | `modelcontextprotocol/servers` | 91.5k | 2026-10-22 |
| Docs / library knowledge | Context7 | `upstash/context7` | 63.6k | 2026-10-23 |
| Semantic code retrieval, LSP | Serena | `oraios/serena` | 30.7k | 2026-10-20 |
| Codebase indexing | claude-context | `zilliztech/claude-context` | 12.6k | 2026-07-14 |
| Long-term memory | Mem0 | `mem0ai/mem0` | 67.7k | 2026-10-23 |
| Design-system sync (`DesignSync`) | Figma Context MCP | `GLips/Figma-Context-MCP` | 16.1k | 2026-10-24 |
| Shared data store (`ArtifactData`) | Supabase MCP | `supabase/mcp` | 3.0k | 2026-10-24 |
| Shared data store (alt) | Postgres MCP Pro | `crystaldba/postgres-mcp` | 3.4k | 2026-08-17 |
| Serverless / edge backends | Cloudflare MCP | `cloudflare/mcp-server-cloudflare` | 4.4k | 2026-10-22 |
| Notebooks (`NotebookEdit`) | Jupyter MCP | `datalayer/jupyter-mcp-server` | 1.3k | 2026-10-24 |
| Slack messaging | Slack MCP | `korotovsky/slack-mcp-server` | 1.9k | 2026-07-16 |
| Notion docs | Notion MCP (official) | `makenotion/notion-mcp-server` | 4.7k | 2026-09-20 |
| **Web search** | Exa MCP | `exa-labs/exa-mcp-server` | 5.2k | 2026-10-19 |
| Web search (alt) | Tavily MCP | `tavily-ai/tavily-mcp` | 2.5k | 2026-10-22 |
| Web search (alt) | Brave Search MCP (official) | `brave/brave-search-mcp-server` | 1.5k | 2026-10-22 |
| MCP discovery / registry | Official registry | `modelcontextprotocol/registry` | 7.4k | 2026-10-23 |

## 4. Skills & agent collections

For the skills the corpus references (`code-review`, `feature-dev`, `pr-review-toolkit`,
`frontend-design`, `plugin-dev`, `security-guidance`, `ralph-wiggum`, `hookify`,
output styles), reuse the installed skill directly where the harness supports `SKILL.md`
(07 §4); otherwise draw equivalents from an actively-developed collection:

| Collection | Repo | ★ | Last push | Notes |
|---|---|---|---|---|
| Superpowers | `obra/superpowers` | 304.4k | 2026-10-23 | Large, daily-active skill/agent library |
| Official skills | `anthropics/skills` | 183.4k | 2026-10-09 | Vendor reference skills |
| Agents | `wshobson/agents` | 41.6k | 2026-10-24 | Wide catalogue of subagents |
| Templates | `davila7/claude-code-templates` | 32.9k | 2026-10-24 | Commands, agents, settings, hooks |
| Subagents | `VoltAgent/awesome-claude-code-subagents` | 26.0k | 2026-10-11 | Curated subagent list |
| SuperClaude | `SuperClaude-Org/SuperClaude_Framework` | 23.9k | 2026-09-27 | Commands, personas, hooks |
| Index | `hesreallyhim/awesome-claude-code` | 56.4k | 2026-10-24 | Discovery index |

The `plugin-dev` skills (`agent-development`, `command-development`, `hook-development`,
`mcp-integration`, `plugin-structure`, `plugin-settings`, `skill-development`) are
format-level and already portable — reuse them directly.

## 5. Not directly replaceable (closest substitute + residual loss)

Some reference-harness capabilities have no 1:1 open-source drop-in. Substitute and
state the loss rather than pretending parity:

| Capability | Closest substitute | Residual loss |
|---|---|---|
| `Artifact` (hosted page) | Emit standalone HTML/Markdown (or push to a static host / GitHub Pages) | No private-by-default hosted URL or live republish/collab |
| `ArtifactData` (page-side shared DB) | Supabase / Postgres / Neon MCP | Requires your own project; no implicit per-artifact DB |
| `ArtifactComments` | GitHub PR/issue comments, or a review tool | Comment threads tied to the hosting service, not the page |
| `DesignSync` / design-system pane | Figma Context MCP | No first-party claude.ai/design project sync |
| `PushNotification` | ntfy / webhook MCP, or OS notifications | Delivery depends on your channel |
| `EndConversation` (safety control) | Harness-level session control | Safety semantics differ by harness; keep the guidance in 03 |
| Statusline integration | Harness-native statusline | Format-specific to the reference shell |
| File-based memory (`MEMORY.md`) | Filesystem + memory MCP (knowledge graph) | Loses the auto-loaded index convention unless reimplemented |

## 6. Selection criteria

When choosing a replacement, prefer, in order:

1. **Vendor/official** (e.g. `github/github-mcp-server`, `brave/brave-search-mcp-server`).
2. **High adoption + recent commits** — a useful heuristic is **≥ 1,000 ★ and a push
   within ~90 days** of the date you read this.
3. **Not archived / not stale.** Check `archived` and `pushed_at`. Examples to avoid as
   of the date above: `browserbase/mcp-server-browserbase` (archived),
   `contains-studio/agents` (last push 2025-07), `Tritlo/lsp-mcp` (last push 2025-07),
   `wong2/awesome-mcp-servers` (last push 2026-07).
4. **Portability** — an MCP server or `SKILL.md` skill beats a harness-specific plugin.

Verify before adopting:

```bash
gh api repos/OWNER/REPO --jq '{stars:.stargazers_count, forks:.forks_count,
  open_issues:.open_issues_count, pushed:.pushed_at, archived:.archived}'
```

## 7. Design lesson

- **Ship the mapping, not the dependency.** A prompt corpus is portable; the *names*
  inside it are not. Any harness-portable corpus should carry a resolution table so a
  reader can restore every capability without guessing.
- **Directories are the interface.** Because 07's formats (`SKILL.md`, `agents/*.md`,
  `.mcp.json`) are simple conventions, most "replacements" are just the same thing —
  only *tool names* and *hosted-service* features actually change.
