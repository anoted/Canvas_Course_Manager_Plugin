# Canvas Course Manager — Claude Plugin

A full Claude plugin for running a Canvas LMS course from Claude: create and manage
**assignments, quizzes, modules, pages, files, announcements, and discussions**, grade
submissions against rubrics, and render grade/progress charts inline — all behind a
**draft → review → publish** pipeline so nothing reaches students unreviewed.

This repository is also its **own plugin marketplace**: point Claude Code at it and
install directly (see [Installation](#installation)).

## What's inside

| Component | What it does |
|---|---|
| **`canvas` MCP server** (33 tools) | The Canvas REST API as MCP tools: courses, assignments + grading, submission text extraction (PDF/DOCX), quizzes, modules, pages, file upload, announcements, discussions, roster. Plus read-only `canvas://` resources, 4 reusable prompts, and two [MCP Apps](#mcp-apps-interactive-panels-in-claude-desktop): a Course Explorer and a Content Composer. |
| **`canvas-viz` MCP server** (3 tools) | Inline PNG charts: grade histograms, graded-vs-pending donut, per-assignment averages bar chart. In Claude Desktop each chart also renders as an interactive panel (tooltips, sorting, data table). |
| **8 slash commands** | `/canvas-setup`, `/canvas-courses`, `/canvas-assignment`, `/canvas-quiz`, `/canvas-module`, `/canvas-grade`, `/canvas-publish`, `/canvas-status` |
| **2 agents** | `content-reviewer` (checks drafts before publishing, read-only) and `homework-grader` (drafts grades + feedback, never posts them) |
| **2 skills** | `canvas-management` (draft → review → publish workflow) and `canvas-grading` (rubric → proposal → approval → post) |
| **1 hook** | A `PreToolUse` guard that **blocks** creating content as published or with empty instructions, and **asks for confirmation** before anything becomes student-visible (publishing, announcements) or destructive (module deletion). |

## Repository layout

```
.claude-plugin/
  plugin.json            # plugin manifest
  marketplace.json       # makes this repo installable as a marketplace
.mcp.json                # bundles both MCP servers with the plugin
commands/                # slash commands (canvas-*.md)
agents/                  # content-reviewer, homework-grader
skills/                  # canvas-management, canvas-grading (SKILL.md each)
hooks/
  hooks.json             # PreToolUse wiring
  pre_publish_guard.py   # the publish/delete guard
servers/
  canvas/                # Canvas LMS MCP server (Python, stdio)
    apps/                # MCP Apps: course-explorer, content-composer + bridge
  visualization/         # chart-rendering MCP server (Python, stdio)
    apps/                # MCP Apps: interactive views of the three charts
```

## Prerequisites

- **Python 3.10+** on your PATH as `python`
- **Canvas API token**: Canvas → Account → Settings → **+ New Access Token**.
  The token has the full power of your Canvas account — treat it like a password.
- **Claude Code v2+** for the full plugin, or **Claude Desktop / Cowork** for the
  MCP servers (see [Claude Desktop / Cowork](#option-b--claude-desktop--cowork-mcp-servers-only)).

Install the Python dependencies once:

```bash
pip install -r servers/canvas/requirements.txt -r servers/visualization/requirements.txt
```

## Configure Canvas credentials

The canvas server reads credentials from environment variables first, then from a
`.env` file **next to the server script**. Two options:

**Option 1 — `.env` file** (per-install):

```bash
cd servers/canvas
cp .env.example .env    # then edit .env: CANVAS_BASE_URL + CANVAS_API_TOKEN
```

> When installed from the marketplace, the plugin lives in Claude's plugin cache —
> run **`/canvas-setup`** in Claude Code and it will locate the installed copy,
> create the `.env` for you, and test the connection.

**Option 2 — system environment variables** (survives plugin updates):
set `CANVAS_BASE_URL` and `CANVAS_API_TOKEN` in your OS environment (on Windows:
Settings → System → About → Advanced system settings → Environment Variables).

Never commit `.env` — it is gitignored here on purpose.

## Installation

### Option A — Claude Code (recommended: full plugin)

This repo is its own marketplace. In Claude Code:

```
/plugin marketplace add anoted/canvas-course-manager
/plugin install canvas-course-manager@canvas-tools
```

Restart Claude Code when prompted, then run:

```
/canvas-setup
```

to verify dependencies, create the `.env`, and test the Canvas connection.

**Installing a local checkout instead** (for development):

```
/plugin marketplace add C:/path/to/canvas-course-manager
/plugin install canvas-course-manager@canvas-tools
```

**Uninstall / manage:** run `/plugin` for the interactive manager, or
`/plugin uninstall canvas-course-manager`.

### Option B — Claude Desktop / Cowork (MCP servers only)

Plugins (commands, agents, skills, hooks) are Claude Code features. Claude Desktop
and Cowork can still use both MCP servers — that covers all Canvas tools, the
chart tools, the server's built-in prompts (`grade_homework`, `build_quiz`,
`build_course_module`, `assess_single_submission`), which show up in Desktop's
prompt picker, **and the interactive MCP Apps panels** (Course Explorer, Content
Composer, and the chart views), which only render in hosts that support MCP Apps —
Claude Desktop being the main one.

1. Clone this repo somewhere permanent and install the Python deps (above).
2. Open the config file — Claude Desktop → **Settings → Developer → Edit Config**,
   or edit it directly:
   - Windows: `%APPDATA%\Claude\claude_desktop_config.json`
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
3. Add the servers (use YOUR absolute paths; on Windows use `\\` or `/` in JSON):

```json
{
  "mcpServers": {
    "canvas": {
      "command": "python",
      "args": ["C:/path/to/canvas-course-manager/servers/canvas/canvas_mcp_server.py"],
      "env": {
        "CANVAS_BASE_URL": "https://yourschool.instructure.com",
        "CANVAS_API_TOKEN": "your_canvas_token_here"
      }
    },
    "canvas-viz": {
      "command": "python",
      "args": ["C:/path/to/canvas-course-manager/servers/visualization/visualization_mcp_server.py"]
    }
  }
}
```

   (If you configured `servers/canvas/.env`, you can omit the `env` block.)

4. Fully restart Claude Desktop / Cowork. The tools appear under the
   **search & tools** (plug) icon; enable them for your chat.

### Option C — just the MCP servers in Claude Code (no plugin)

```bash
claude mcp add canvas -- python "C:/path/to/servers/canvas/canvas_mcp_server.py"
claude mcp add canvas-viz -- python "C:/path/to/servers/visualization/visualization_mcp_server.py"
```

Or over HTTP (e.g. to share one server between clients on the same machine):

```bash
# terminal 1 — run the server with the HTTP transport
MCP_TRANSPORT=streamable-http python servers/canvas/canvas_mcp_server.py
# terminal 2 — connect
claude mcp add --transport http canvas http://127.0.0.1:8017/mcp
```

> The HTTP endpoint has **no authentication** — keep `MCP_HOST=127.0.0.1` so only
> local clients can reach it.

## Usage

Slash commands (Claude Code):

| Command | What it does |
|---|---|
| `/canvas-setup` | Verify deps, create `.env`, live connection test |
| `/canvas-courses` | List your courses with ids |
| `/canvas-assignment 123 binary search trees` | Draft an assignment (unpublished), review it, offer to publish |
| `/canvas-quiz 123 recursion 12` | Draft quiz questions for approval, then create the quiz unpublished |
| `/canvas-module 123 Week 5: Graphs` | Build a whole module: page, files, assignment, quiz — as drafts |
| `/canvas-grade 123 456` | Read ungraded submissions, propose grades + feedback, post after approval |
| `/canvas-publish 123` | Review draft content and publish what you approve |
| `/canvas-status 123` | Grading backlog, deadlines, drafts — with charts |

Or just talk to Claude — the skills route these automatically:

- *"Create a homework assignment on SQL joins in my Databases course, due next Friday, 50 points."*
- *"Grade the ungraded submissions for assignment 456 with this rubric: …"*
- *"Show me the grade distribution for the midterm."*
- *"What needs my attention in course 123?"*

### MCP Apps (interactive panels in Claude Desktop)

Both servers ship [MCP Apps](https://github.com/modelcontextprotocol/ext-apps) —
HTML views that hosts supporting the apps extension (Claude Desktop) render inline
in the chat. Hosts without support (Claude Code today) ignore them and fall back
to the tools' normal output, so nothing breaks.

| App | Opened by | What you can do in it |
|---|---|---|
| **Course Explorer** | `open_course_explorer` — *"open the course explorer"* | Browse a course's modules, assignments, quizzes, pages, announcements, files, and students in tabs. Drill into an assignment's submissions, read a submission, and **post a grade + feedback inline**. Preview page/file/module-item content. Publish drafts. Every write asks for confirmation first. |
| **Content Composer** | `open_content_composer` — *"open the content composer"* | Forms for creating content: assignments (points, dates, submission types, module placement), quizzes with a **question-by-question builder** (multiple choice, true/false, short answer, essay, …) and running points total, pages, announcements (with a big "posts immediately" warning + optional scheduling), discussions, and modules. Everything except announcements starts as an unpublished draft. |
| **Chart views** | the three `render_*` chart tools | The PNG chart, upgraded: hover tooltips, re-binning / sorting, and an accessible data table — in light and dark theme. |

The apps talk back to the same MCP tools you'd use in chat, so the plugin's
publish guard and draft-first behavior still apply in Claude Code; in Desktop the
apps ask for confirmation themselves before grading, publishing, or announcing.

### The review pipeline

1. Everything is created **unpublished** (`published=false`) — the hook denies
   attempts to create content live, and denies assignments with empty instructions.
2. The **content-reviewer** agent checks drafts (completeness, points, deadlines,
   quiz answer keys, placeholder text) and returns `APPROVE` or `REVISE` with specifics.
3. Publishing (`update_* published=true`, `publish_quiz`, announcements, module
   deletion) always triggers a **confirmation prompt** via the hook — you have the
   final word before students see anything.
4. Grades follow the same shape: the **homework-grader** agent proposes, you approve,
   only then does `grade_submission` write to the gradebook.

## Security notes

- Your Canvas token grants full account access. Keep it in `.env` (gitignored) or OS
  environment variables; never paste it into chats or commit it.
- The MCP servers run locally; nothing is sent anywhere except your Canvas instance.
- Announcements go live to students immediately unless `delayed_post_at` is set —
  the hook makes Claude confirm the text with you first.

## Development

```bash
# validate plugin + marketplace manifests
claude plugin validate .

# exercise a server interactively with the MCP Inspector
npx @modelcontextprotocol/inspector python servers/canvas/canvas_mcp_server.py

# test the hook by hand
echo '{"tool_name":"mcp__x_canvas__create_assignment","tool_input":{"published":true,"description_html":"x"}}' | python hooks/pre_publish_guard.py
```

Bump `version` in `.claude-plugin/plugin.json` when you change the plugin; installed
copies update via `/plugin marketplace update canvas-tools`.

## License

[MIT](LICENSE)
