---
description: Grade ungraded Canvas submissions against a rubric — proposals first, posting only after approval
argument-hint: <course-id> <assignment-id> [rubric]
---

Grade submissions for the Canvas assignment following the canvas-grading skill.

Request: $ARGUMENTS

1. If ids are missing, help me find them (`list_courses`, `list_assignments` —
   the assignments list shows `needs_grading_count`).
2. Confirm the rubric with me (derive one from the assignment description if I
   didn't give one).
3. Launch the `homework-grader` agent to read every ungraded submission and
   draft scores + feedback. It never posts grades.
4. Show me the full proposal table and wait for my approval or adjustments.
5. Only then post with `grade_submission` (grade + feedback comment) per
   student, report what was posted, and offer a `render_grade_distribution`
   chart of the results.
