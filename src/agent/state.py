from typing import TypedDict, List, Optional
from pydantic import BaseModel


class QuestionAnswer(BaseModel):
    """Model for storing question-answer pairs"""
    question: str
    answer: str
    is_correct: bool
    evaluation: str


class InterviewState(TypedDict):
    """State for the interview graph"""
    # Initial inputs
    role: str
    languages: List[str]
    level: str  # beginner, intermediate, advanced

    # Interview progress
    experience_years: Optional[int]
    current_question_count: int
    total_questions: int

    # Questions and answers
    questions_asked: List[QuestionAnswer]
    current_question: Optional[str]
    current_answer: Optional[str]

    # Follow-up questions
    followup_questions: List[str]
    current_followup_count: int
    max_followups_per_question: int

    # Candidate questions
    candidate_questions: List[str]
    candidate_question_answers: List[str]

    # Scoring
    correct_answers: int
    wrong_answers: int
    consecutive_wrong: int

    # Control flow
    should_continue: bool
    interview_complete: bool
    waiting_for_candidate_question: bool
    current_phase: str  # "main_question", "followup", "candidate_question"

    # Final report
    report: Optional[str]
    messages: List[str]  # Conversation history