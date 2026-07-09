---
name: canvas-management
description: Workflow for creating and managing Canvas LMS content (assignments, quizzes, modules, pages, files, announcements) with the canvas MCP server. Use whenever creating, editing, organizing, or publishing Canvas course content, or when asked to build course materials in Canvas.
---

# Canvas Course Management

All course content flows through a three-phase pipeline: **draft → review →
publish**. Students only ever see reviewed content.

## Phase 1 — Draft

- Create content with `create_assignment`, `create_quiz` + `add_quiz_question`,
  `create_page`, `create_module`, `create_discussion`, or `upload_file` — always
  with `published=false` (the default; a plugin hook blocks published creates).
- Look at existing course content first (`list_modules`, `list_pages`) and match
  its naming, tone, and structure.
- `create_assignment`, `create_quiz`, `create_page`, and `upload_file` accept an
  optional `module_id` to attach new content to a module in one call; anything
  else goes through `add_module_item`.
- Assignments need: real instructions in `description_html`, `points_possible`
  > 0, a `due_at` deadline (ISO 8601 with timezone), and sensible
  `submission_types`.
- Show the user a plan/outline before creating multiple items (e.g. a whole
  module) and get their go-ahead.

## Phase 2 — Review

- After drafting, launch the `content-reviewer` agent with the ids of the new
  content. It returns `VERDICT: APPROVE` or `VERDICT: REVISE` with specifics.
- On REVISE: fix the listed problems with the matching `update_*` tools and
  re-run the review. Do not argue with the reviewer; if a point seems wrong,
  surface it to the user.

## Phase 3 — Publish

- Only after APPROVE **and** the user's explicit confirmation, publish with
  `update_assignment` / `update_quiz` / `update_page` / `update_module`
  (`published=true`) or `publish_quiz`. A hook will ask the user to confirm each
  publish — that is expected.
- Publish the module itself last, after its items are published.

## Cautions

- `create_announcement` goes live to students immediately unless
  `delayed_post_at` is set — always show the user the exact text first.
- `delete_module` / `delete_module_item` cannot be undone; confirm with the user
  and restate what will be deleted.
- When editing a page body, fetch the current HTML first with
  `get_page(raw_html=true)` so existing formatting is preserved.

## Visualizing course data

Use the `canvas-viz` server after fetching numbers with the canvas tools:
`render_grade_distribution` (histogram of scores), `render_course_progress`
(graded-vs-pending donut), `render_assignment_averages` (bar chart across
assignments).
