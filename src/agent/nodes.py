from typing import Dict, Any
from src.agent.state import InterviewState, QuestionAnswer
from src.utils.prompts import (
    EXPERIENCE_PROMPT,
    QUESTION_GENERATION_PROMPT,
    ANSWER_EVALUATION_PROMPT,
    FOLLOWUP_PROMPT
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
        "correct_answers": 0,
        "wrong_answers": 0,
        "consecutive_wrong": 0,
        "should_continue": True,
        "interview_complete": False
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


def provide_feedback(state: InterviewState) -> Dict[str, Any]:
    """Node to provide feedback on the answer"""
    llm = settings.get_llm()

    last_qa = state["questions_asked"][-1]

    prompt = FOLLOWUP_PROMPT.format(
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

    return {
        "messages": state["messages"] + [f"Interviewer: {feedback}"]
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