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

    # Scoring
    correct_answers: int
    wrong_answers: int
    consecutive_wrong: int

    # Control flow
    should_continue: bool
    interview_complete: bool

    # Final report
    report: Optional[str]
    messages: List[str]  # Conversation history