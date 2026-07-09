---
description: Course status dashboard — grading backlog, drafts, deadlines, with inline charts
argument-hint: <course-id>
---

Give me a status overview of the Canvas course.

Request: $ARGUMENTS

1. If no course id was given, call `list_courses` and ask which one.
2. Gather: `list_assignments` (due dates, `needs_grading_count`, published
   flags), `list_quizzes`, `list_modules` (draft vs published items), and
   recent `list_announcements`.
3. Report, in order: **grading backlog** (assignments with ungraded
   submissions), **upcoming deadlines** (next 14 days), **unpublished drafts**,
   and anything odd (past-due unpublished content, empty modules).
4. Render charts with the canvas-viz tools: `render_course_progress` for
   graded vs pending submissions, and `render_assignment_averages` if there are
   graded assignments to compare.
5. End with a short suggested to-do list.
