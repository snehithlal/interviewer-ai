EXPERIENCE_PROMPT = """Role: {role}
Tech: {languages}
Level: {level}

Greet candidate, ask {role} experience years."""

QUESTION_GENERATION_PROMPT = """Context:
Role: {role}
Tech: {languages}
Level: {level}
Exp: {experience_years}y
Q#: {question_count}
Score: {correct_answers}/{wrong_answers}

Previous: {previous_questions}

Generate 1 technical question:
1. Match level/role
2. Test {languages}
3. Be practical
4. No repeats

Question only:"""

ANSWER_EVALUATION_PROMPT = """Q: {question}
A: {answer}
Context: {role}, {languages}, {level}

CORRECT: [YES/NO]
EVAL: [Brief evaluation on accuracy/completeness]"""

FOLLOWUP_PROMPT = """Q: {question}
A: {answer}
Eval: {evaluation}
Score: {correct_answers}/{wrong_answers}

Brief feedback + transition to next question."""

FOLLOWUP_QUESTION_PROMPT = """Last Q&A:
Q: {original_question}
A: {candidate_answer}
Result: {is_correct}

Context: {role}, {languages}, {level}
Generate related followup:"""

CANDIDATE_QUESTION_PROMPT = """Q: {candidate_question}
Context: {role}, {languages}, {level}, {experience_years}y

Brief answer, return to interview."""

INTERACTIVE_FEEDBACK_PROMPT = """Q: {question}
A: {answer}
Result: {evaluation}
Score: {correct_answers}/{wrong_answers}

Brief constructive feedback."""

REPORT_GENERATION_PROMPT = """Profile:
{role}, {languages}, {level}, {experience_years}y

Stats:
Total: {total_questions}
Correct: {correct_answers}
Wrong: {wrong_answers}
Rate: {success_rate}%

Q&A: {qa_details}
Questions: {candidate_questions_details}

1. Summary
2. Overview
3. Performance
4. Strengths
5. Improvements
6. Assessment
7. Engagement
8. Recommendation"""