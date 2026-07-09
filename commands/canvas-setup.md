---
description: Verify the Canvas plugin installation — Python deps, credentials, and a live connection test
---

Verify this plugin's installation end to end and fix what you can:

1. Check that `python` is available and version >= 3.10.
2. Check the Python dependencies from both server requirement files
   (`servers/canvas/requirements.txt`, `servers/visualization/requirements.txt`
   under the plugin root). If any are missing, offer to `pip install -r` them.
3. Check that `servers/canvas/.env` exists. If not, copy `.env.example` to
   `.env` and tell the user to fill in `CANVAS_BASE_URL` and `CANVAS_API_TOKEN`
   (Canvas → Account → Settings → **+ New Access Token**) — the user should edit
   the file themselves rather than paste the token into chat. Never print the
   token's value.
4. If the canvas MCP tools are available in this session, call `list_courses`
   as a live connection test and show the result. If tools are not available
   yet, remind the user to restart Claude Code so the plugin's MCP servers
   start.

Finish with a short PASS/FAIL checklist of the four steps.
