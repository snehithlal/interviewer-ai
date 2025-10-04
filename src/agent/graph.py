from langgraph.graph import StateGraph, END
from src.agent.state import InterviewState
from src.agent.nodes import (
    ask_experience,
    collect_experience,
    generate_question,
    collect_answer,
    evaluate_answer,
    provide_interactive_feedback,
    handle_candidate_question,
    generate_followup_question,
    check_continue
)
from src.utils.report_generator import generate_report


def should_continue_interview(state: InterviewState) -> str:
    """Conditional edge to determine if interview should continue"""
    if state.get("should_continue", True):
        return "continue"
    else:
        return "end"


def determine_next_step(state: InterviewState) -> str:
    """Determine the next step after feedback"""
    if state.get("waiting_for_candidate_question", False):
        return "candidate_question"
    else:
        return "check_continue"


def should_ask_followup(state: InterviewState) -> str:
    """Determine if we should ask a follow-up question"""
    # Only ask follow-up if we're in followup phase and haven't exceeded limits
    if (state.get("current_phase") == "followup" and
        state.get("current_followup_count", 0) < state.get("max_followups_per_question", 2) and
        state.get("current_question_count", 0) < 10):  # MAX_QUESTIONS
        return "followup_question"
    else:
        return "check_continue"


def create_interview_graph():
    """Create the interview workflow graph"""

    # Initialize the graph
    workflow = StateGraph(InterviewState)

    # Add nodes
    workflow.add_node("ask_experience", ask_experience)
    workflow.add_node("collect_experience", collect_experience)
    workflow.add_node("generate_question", generate_question)
    workflow.add_node("collect_answer", collect_answer)
    workflow.add_node("evaluate_answer", evaluate_answer)
    workflow.add_node("provide_interactive_feedback", provide_interactive_feedback)
    workflow.add_node("handle_candidate_question", handle_candidate_question)
    workflow.add_node("generate_followup_question", generate_followup_question)
    workflow.add_node("check_continue", check_continue)

    # Define the flow
    workflow.set_entry_point("ask_experience")

    workflow.add_edge("ask_experience", "collect_experience")
    workflow.add_edge("collect_experience", "generate_question")
    workflow.add_edge("generate_question", "collect_answer")
    workflow.add_edge("collect_answer", "evaluate_answer")
    workflow.add_edge("evaluate_answer", "provide_interactive_feedback")

    # Conditional edge after feedback
    workflow.add_conditional_edges(
        "provide_interactive_feedback",
        determine_next_step,
        {
            "candidate_question": "handle_candidate_question",
            "check_continue": "check_continue"
        }
    )

    # After candidate question handling - go directly to check continue
    workflow.add_edge("handle_candidate_question", "check_continue")

    # Conditional edge based on continue decision
    workflow.add_conditional_edges(
        "check_continue",
        should_continue_interview,
        {
            "continue": "generate_question",
            "end": END
        }
    )

    # Compile the graph
    app = workflow.compile()

    return app


def run_interview(role: str, languages: list, level: str):
    """Run the interview with the given parameters"""

    print("\n" + "="*80)
    print("🎯 INTERVIEWR AI - Technical Interview System")
    print("="*80)
    print(f"\nRole: {role}")
    print(f"Languages/Technologies: {', '.join(languages)}")
    print(f"Level: {level}")
    print("\n" + "="*80 + "\n")

    # Create initial state
    initial_state: InterviewState = {
        "role": role,
        "languages": languages,
        "level": level,
        "experience_years": None,
        "current_question_count": 0,
        "total_questions": 0,
        "questions_asked": [],
        "current_question": None,
        "current_answer": None,
        "followup_questions": [],
        "current_followup_count": 0,
        "max_followups_per_question": 2,
        "candidate_questions": [],
        "candidate_question_answers": [],
        "correct_answers": 0,
        "wrong_answers": 0,
        "consecutive_wrong": 0,
        "should_continue": True,
        "interview_complete": False,
        "waiting_for_candidate_question": False,
        "current_phase": "main_question",
        "report": None,
        "messages": []
    }

    # Create and run the graph
    app = create_interview_graph()

    # Execute the interview
    final_state = initial_state.copy()
    for output in app.stream(initial_state):
        # Merge all state updates from each node
        for node_name, node_output in output.items():
            if isinstance(node_output, dict):
                final_state.update(node_output)

    # Generate report
    print("\n" + "="*80)
    print("📊 Generating Interview Report...")
    print("="*80 + "\n")

    report = generate_report(final_state)

    print("\n" + "="*80)
    print("INTERVIEW REPORT")
    print("="*80 + "\n")
    print(report)
    print("\n" + "="*80)
    print("✅ Interview Complete!")
    print("="*80 + "\n")

    return final_state, report