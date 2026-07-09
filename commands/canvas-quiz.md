---
description: Build a Canvas quiz — draft questions for approval, then create it unpublished
argument-hint: <course-id> <topic> [number of questions]
---

Build a quiz in the Canvas course following the canvas-management skill.

Request: $ARGUMENTS

1. If course id or topic is missing, ask. Default to 10 questions, mixed
   difficulty, mostly multiple choice with 4 options, plus 1–2 short answer
   or essay questions where appropriate.
2. Draft ALL questions with their answers (mark the correct ones) and show them
   to me for review before touching Canvas.
3. On approval: `create_quiz` (unpublished), then `add_quiz_question` for each
   question. Pass `module_id` if I named a module.
4. Run the `content-reviewer` agent on the quiz; fix anything it flags.
5. Report the quiz id and question count. Do not publish — remind me to say the
   word when I want `publish_quiz` run.
