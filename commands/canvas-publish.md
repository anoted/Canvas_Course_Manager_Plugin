---
description: Review draft Canvas content and publish it after approval
argument-hint: <course-id> [what to publish]
---

Run the review → publish phase of the canvas-management skill on existing draft
content.

Request: $ARGUMENTS

1. Find unpublished content in the course (`list_assignments`, `list_quizzes`,
   `list_modules`, `list_pages` — check the `published` flags). If I named
   specific items, limit to those.
2. Run the `content-reviewer` agent on each draft. Fix REVISE findings with the
   `update_*` tools where the fix is unambiguous; otherwise show me the finding.
3. Present the publish list: item, id, reviewer verdict.
4. On my approval, publish each item (`update_*` with `published=true`,
   `publish_quiz` for quizzes), items before their module. Confirm each hook
   prompt deliberately — that guard is part of this plugin.
5. Report what is now live and what stayed in draft.
