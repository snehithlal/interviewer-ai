from langgraph.graph import StateGraph, END
from src.agent.state import InterviewState
from src.agent.nodes import (
    ask_experience,
    collect_experience,
    generate_question,
    collect_answer,
    evaluate_answer,
    provide_feedback,
    check_continue
)
from src.utils.report_generator import generate_report


def should_continue_interview(state: InterviewState) -> str:
    """Conditional edge to determine if interview should continue"""
    if state.get("should_continue", True):
        return "continue"
    else:
        return "end"


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
    workflow.add_node("provide_feedback", provide_feedback)
    workflow.add_node("check_continue", check_continue)

    # Define the flow
    workflow.set_entry_point("ask_experience")

    workflow.add_edge("ask_experience", "collect_experience")
    workflow.add_edge("collect_experience", "generate_question")
    workflow.add_edge("generate_question", "collect_answer")
    workflow.add_edge("collect_answer", "evaluate_answer")
    workflow.add_edge("evaluate_answer", "provide_feedback")
    workflow.add_edge("provide_feedback", "check_continue")

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
        "correct_answers": 0,
        "wrong_answers": 0,
        "consecutive_wrong": 0,
        "should_continue": True,
        "interview_complete": False,
        "report": None,
        "messages": []
    }

    # Create and run the graph
    app = create_interview_graph()

    # Execute the interview
    final_state = None
    for output in app.stream(initial_state):
        final_state = output

    # Extract the actual state from the output
    if final_state:
        # The output is a dict with node names as keys
        # Get the last state from the last node executed
        state_key = list(final_state.keys())[-1]
        final_state = final_state[state_key]

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