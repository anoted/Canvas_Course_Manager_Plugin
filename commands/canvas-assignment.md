---
description: Draft a new Canvas assignment (created unpublished, then reviewed)
argument-hint: <course-id> <topic or instructions>
---

Create a new assignment in the Canvas course using the canvas-management skill's
draft → review → publish pipeline.

Request: $ARGUMENTS

1. If the course id or topic is missing, ask (use `list_courses` to help).
2. Draft the assignment: title, full instructions (HTML), points, due date, and
   submission types. Look at existing assignments in the course to match style
   and typical point values. Show the draft to me before creating anything.
3. On my go-ahead, `create_assignment` with `published=false` (pass `module_id`
   if I named a module).
4. Run the `content-reviewer` agent on it; apply fixes if it says REVISE.
5. Tell me the assignment id and ask whether to publish now
   (`update_assignment` with `published=true`) or leave it as a draft.
