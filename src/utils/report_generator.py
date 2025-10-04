import os
from datetime import datetime
from src.agent.state import InterviewState
from src.utils.prompts import REPORT_GENERATION_PROMPT
from src.config.settings import settings


def generate_report(state: InterviewState) -> str:
    """Generate a comprehensive interview report"""
    llm = settings.get_llm()

    # Calculate success rate
    total = state["current_question_count"]
    success_rate = (state["correct_answers"] / total * 100) if total > 0 else 0

    # Format Q&A details
    qa_details = []
    for i, qa in enumerate(state["questions_asked"], 1):
        result = "✓ CORRECT" if qa.is_correct else "✗ INCORRECT"
        qa_details.append(f"""
Question {i}: {qa.question}
Answer: {qa.answer}
Result: {result}
Evaluation: {qa.evaluation}
""")

    qa_text = "\n---\n".join(qa_details)

    # Generate report using LLM
    prompt = REPORT_GENERATION_PROMPT.format(
        role=state["role"],
        languages=", ".join(state["languages"]),
        level=state["level"],
        experience_years=state.get("experience_years", 0),
        total_questions=state["current_question_count"],
        correct_answers=state["correct_answers"],
        wrong_answers=state["wrong_answers"],
        success_rate=round(success_rate, 2),
        qa_details=qa_text
    )

    response = llm.invoke(prompt)
    report = response.content.strip()

    # Add header
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    header = f"""
{'='*80}
                        INTERVIEW REPORT
{'='*80}
Date: {timestamp}
Candidate Level: {state["level"]}
Role: {state["role"]}
Technologies: {", ".join(state["languages"])}
Experience: {state.get("experience_years", 0)} years
{'='*80}

"""

    full_report = header + report

    # Save report to file
    save_report(full_report, state)

    return full_report


def save_report(report: str, state: InterviewState) -> str:
    """Save the report to a file"""
    # Create reports directory if it doesn't exist
    os.makedirs(settings.REPORTS_DIR, exist_ok=True)

    # Generate filename
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    role_clean = state["role"].replace(" ", "_").lower()
    filename = f"interview_report_{role_clean}_{timestamp}.txt"
    filepath = os.path.join(settings.REPORTS_DIR, filename)

    # Write report
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n✅ Report saved to: {filepath}\n")

    return filepath