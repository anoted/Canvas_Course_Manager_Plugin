---
description: Assemble a complete Canvas module — overview page, files, assignment, and quiz, all as drafts
argument-hint: <course-id> <module name or topic>
---

Build a complete module in the Canvas course following the canvas-management
skill.

Request: $ARGUMENTS

1. Inspect the course (`list_modules`, `list_pages`) to match its existing
   naming and structure.
2. Show me an outline first: overview page, files to upload (ask for local
   paths), one assignment (instructions, deadline, points), and a short quiz.
3. On approval, create everything unpublished: `create_module`, then
   `create_page`, `upload_file`, `create_assignment`, and `create_quiz` +
   `add_quiz_question` — each with `module_id` so items land in the module.
4. Run the `content-reviewer` agent across the new content; fix what it flags.
5. Give me a table of created items (type, id, title) and remind me to publish
   the items and then the module when ready.
