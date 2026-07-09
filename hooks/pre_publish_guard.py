#!/usr/bin/env python3
"""PreToolUse guard for Canvas content operations.

Claude Code pipes the pending tool call to this script as JSON on stdin:
{"tool_name": "...", "tool_input": {...}, ...}. The script answers with a
permission decision on stdout:

  * deny  — creating content with published=true, or an assignment with an
            empty description: the plugin's workflow is draft first, review,
            then publish.
  * ask   — anything that becomes student-visible (publishing a draft,
            posting an announcement) or destructive (deleting a module):
            the instructor confirms in the permission prompt.
  * no output (exit 0) — everything else proceeds normally.

Plugin-installed MCP tools have names like
mcp__plugin_canvas-course-manager_canvas__create_assignment; only the part
after the final "__" matters here.
"""

import json
import sys

# create_* tools must produce unpublished drafts so content review can run first
DRAFT_FIRST = {"create_assignment", "create_quiz", "create_page", "create_discussion"}

# update_* calls flipping published=true make content visible to students
PUBLISH_UPDATES = {
    "update_assignment",
    "update_quiz",
    "update_page",
    "update_module",
    "update_module_item",
}

CONFIRM_REASONS = {
    "publish_quiz": "This publishes the quiz — students can take it immediately.",
    "create_announcement": (
        "Announcements are visible to students IMMEDIATELY unless delayed_post_at is set."
    ),
    "delete_module": "Deleting a module cannot be undone.",
    "delete_module_item": "This removes the item from the module.",
}


def decide(decision: str, reason: str) -> None:
    print(
        json.dumps(
            {
                "hookSpecificOutput": {
                    "hookEventName": "PreToolUse",
                    "permissionDecision": decision,
                    "permissionDecisionReason": reason,
                }
            }
        )
    )
    sys.exit(0)


def main() -> None:
    try:
        payload = json.load(sys.stdin)
    except Exception:
        sys.exit(0)  # unparseable input — never block unrelated calls

    tool = str(payload.get("tool_name") or "").rsplit("__", 1)[-1]
    args = payload.get("tool_input") or {}

    if tool in DRAFT_FIRST and args.get("published"):
        decide(
            "deny",
            "Canvas plugin policy: create content as an unpublished draft "
            "(published=false), have the content-reviewer agent check it, and "
            "publish with the matching update_* tool after the instructor approves.",
        )

    if tool == "create_assignment" and not str(args.get("description_html") or "").strip():
        decide(
            "deny",
            "The assignment has an empty description. Write the instructions in "
            "description_html before creating it.",
        )

    if tool in PUBLISH_UPDATES and args.get("published"):
        decide(
            "ask",
            "This PUBLISHES content to Canvas where students can see it. "
            "Confirm it has passed content review.",
        )

    if tool in CONFIRM_REASONS:
        decide("ask", CONFIRM_REASONS[tool])

    sys.exit(0)


if __name__ == "__main__":
    main()
