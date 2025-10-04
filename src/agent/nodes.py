from typing import Dict, Any
from src.agent.state import InterviewState, QuestionAnswer
from src.utils.prompts import (
    EXPERIENCE_PROMPT,
    QUESTION_GENERATION_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    FOLLOWUP_PROMPT,
    FOLLOWUP_QUESTION_PROMPT,
    CANDIDATE_QUESTION_PROMPT,
    INTERACTIVE_FEEDBACK_PROMPT
)
from src.config.settings import settings

def ask_experience(state: InterviewState) -> Dict[str, Any]:
    """Node to ask about candidate's experience"""
    llm = settings.get_llm()

    prompt = EXPERIENCE_PROMPT.format(
        role=state["role"],
        languages=", ".join(state["languages"]),
        level=state["level"]
    )

    response = llm.invoke(prompt)
    message = response.content

    print(f"\n🤖 Interviewer: {message}\n")

    return {
        "messages": state.get("messages", []) + [f"Interviewer: {message}"],
        "current_question_count": 0,
        "questions_asked": [],
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
        "current_phase": "main_question"
    }


def collect_experience(state: InterviewState) -> Dict[str, Any]:
    """Node to collect candidate's experience input"""
    exp_input = input("👤 You: ")

    # Try to extract years of experience from input
    experience_years = None
    words = exp_input.lower().split()

    for i, word in enumerate(words):
        if word.isdigit():
            experience_years = int(word)
            break
        if word in ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]:
            word_to_num = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5,
                          "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10}
            experience_years = word_to_num[word]
            break

    # Default to 0 if not found
    if experience_years is None:
        experience_years = 0

    return {
        "experience_years": experience_years,
        "messages": state["messages"] + [f"Candidate: {exp_input}"],
        "total_questions": settings.MAX_QUESTIONS
    }


def generate_question(state: InterviewState) -> Dict[str, Any]:
    """Node to generate next interview question"""
    llm = settings.get_llm()

    previous_questions = "\n".join([
        f"Q{i+1}: {qa.question}"
        for i, qa in enumerate(state.get("questions_asked", []))
    ]) or "None yet"

    prompt = QUESTION_GENERATION_PROMPT.format(
        role=state["role"],
        languages=", ".join(state["languages"]),
        level=state["level"],
        experience_years=state.get("experience_years", 0),
        question_count=state["current_question_count"],
        correct_answers=state["correct_answers"],
        wrong_answers=state["wrong_answers"],
        previous_questions=previous_questions
    )

    response = llm.invoke(prompt)
    question = response.content.strip()

    print(f"\n🤖 Interviewer: {question}\n")

    return {
        "current_question": question,
        "current_followup_count": 0,  # Reset follow-up count for new main question
        "messages": state["messages"] + [f"Interviewer: {question}"]
    }


def collect_answer(state: InterviewState) -> Dict[str, Any]:
    """Node to collect candidate's answer"""
    answer = input("👤 You: ")

    return {
        "current_answer": answer,
        "messages": state["messages"] + [f"Candidate: {answer}"]
    }


def evaluate_answer(state: InterviewState) -> Dict[str, Any]:
    """Node to evaluate the candidate's answer"""
    llm = settings.get_llm()

    prompt = ANSWER_EVALUATION_PROMPT.format(
        question=state["current_question"],
        answer=state["current_answer"],
        role=state["role"],
        languages=", ".join(state["languages"]),
        level=state["level"]
    )

    response = llm.invoke(prompt)
    evaluation_text = response.content.strip()

    # Parse the evaluation
    is_correct = "CORRECT: YES" in evaluation_text.upper()

    # Extract evaluation text
    eval_lines = evaluation_text.split("\n")
    evaluation = ""
    for line in eval_lines:
        if line.startswith("EVALUATION:"):
            evaluation = line.replace("EVALUATION:", "").strip()
            break

    if not evaluation:
        evaluation = evaluation_text

    # Create question-answer record
    qa = QuestionAnswer(
        question=state["current_question"],
        answer=state["current_answer"],
        is_correct=is_correct,
        evaluation=evaluation
    )

    # Update counters
    new_correct = state["correct_answers"] + (1 if is_correct else 0)
    new_wrong = state["wrong_answers"] + (0 if is_correct else 1)
    new_consecutive_wrong = 0 if is_correct else state["consecutive_wrong"] + 1
    new_question_count = state["current_question_count"] + 1

    return {
        "questions_asked": state["questions_asked"] + [qa],
        "correct_answers": new_correct,
        "wrong_answers": new_wrong,
        "consecutive_wrong": new_consecutive_wrong,
        "current_question_count": new_question_count
    }


def provide_interactive_feedback(state: InterviewState) -> Dict[str, Any]:
    """Node to provide feedback and ask if candidate has questions"""
    llm = settings.get_llm()

    last_qa = state["questions_asked"][-1]

    # Use the full interactive feedback
    prompt = INTERACTIVE_FEEDBACK_PROMPT.format(
        question=last_qa.question,
        answer=last_qa.answer,
        evaluation=last_qa.evaluation,
        result="Correct" if last_qa.is_correct else "Incorrect",
        correct_answers=state["correct_answers"],
        wrong_answers=state["wrong_answers"],
        question_count=state["current_question_count"]
    )

    response = llm.invoke(prompt)
    feedback = response.content.strip()

    print(f"\n🤖 Interviewer: {feedback}\n")

    # Only ask for candidate questions on the first question or every 3 questions
    should_ask_questions = (
        state["current_question_count"] == 1 or
        state["current_question_count"] % 3 == 0
    )

    if should_ask_questions:
        return {
            "messages": state["messages"] + [f"Interviewer: {feedback}"],
            "waiting_for_candidate_question": True,
            "current_phase": "candidate_question"
        }
    else:
        return {
            "messages": state["messages"] + [f"Interviewer: {feedback}"],
            "waiting_for_candidate_question": False,
            "current_phase": "main_question"
        }


def handle_candidate_question(state: InterviewState) -> Dict[str, Any]:
    """Node to handle candidate's questions"""
    print("\n💬 Do you have any questions about the question I just asked?")
    print("(Type your question or press Enter to continue)")

    candidate_question = input("👤 You: ").strip()

    if not candidate_question:
        # No question asked, continue with interview
        return {
            "waiting_for_candidate_question": False,
            "current_phase": "main_question"
        }

    # Answer the candidate's question
    llm = settings.get_llm()

    prompt = CANDIDATE_QUESTION_PROMPT.format(
        candidate_question=candidate_question,
        role=state["role"],
        languages=", ".join(state["languages"]),
        level=state["level"],
        experience_years=state.get("experience_years", 0)
    )

    response = llm.invoke(prompt)
    answer = response.content.strip()

    print(f"\n🤖 Interviewer: {answer}\n")

    return {
        "candidate_questions": state["candidate_questions"] + [candidate_question],
        "candidate_question_answers": state["candidate_question_answers"] + [answer],
        "messages": state["messages"] + [f"Candidate: {candidate_question}", f"Interviewer: {answer}"],
        "waiting_for_candidate_question": False,
        "current_phase": "main_question"
    }


def generate_followup_question(state: InterviewState) -> Dict[str, Any]:
    """Node to generate follow-up questions based on candidate's answer"""
    llm = settings.get_llm()

    last_qa = state["questions_asked"][-1]

    # Check if we should ask a follow-up
    should_ask_followup = (
        state["current_followup_count"] < state["max_followups_per_question"] and
        state["current_question_count"] < settings.MAX_QUESTIONS
    )

    if not should_ask_followup:
        return {
            "current_phase": "main_question",
            "current_followup_count": 0,
            "should_continue": True  # Ensure we continue to next main question
        }

    prompt = FOLLOWUP_QUESTION_PROMPT.format(
        original_question=last_qa.question,
        candidate_answer=last_qa.answer,
        evaluation=last_qa.evaluation,
        is_correct="Yes" if last_qa.is_correct else "No",
        role=state["role"],
        languages=", ".join(state["languages"]),
        level=state["level"],
        experience_years=state.get("experience_years", 0)
    )

    response = llm.invoke(prompt)
    followup_question = response.content.strip()

    print(f"\n🤖 Interviewer: {followup_question}\n")

    return {
        "current_question": followup_question,
        "followup_questions": state["followup_questions"] + [followup_question],
        "current_followup_count": state["current_followup_count"] + 1,
        "current_phase": "followup",  # Keep as followup phase
        "messages": state["messages"] + [f"Interviewer: {followup_question}"]
    }


def check_continue(state: InterviewState) -> Dict[str, Any]:
    """Node to check if interview should continue"""
    should_continue = True

    # End if max questions reached
    if state["current_question_count"] >= settings.MAX_QUESTIONS:
        should_continue = False

    # End if too many consecutive wrong answers
    if (state["consecutive_wrong"] >= settings.MAX_CONSECUTIVE_WRONG and
        state["current_question_count"] >= settings.MIN_QUESTIONS):
        should_continue = False
        print("\n⚠️  Interview ending due to multiple incorrect answers.\n")

    return {
        "should_continue": should_continue,
        "interview_complete": not should_continue
    }