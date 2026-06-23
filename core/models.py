from datetime import datetime

from pydantic import BaseModel, Field


# ==========================================================
# Quiz related models
# ==========================================================

class QuizQuestion(BaseModel):
    question: str
    answer: str


class MCQQuestion(BaseModel):
    question: str
    options: list[str]
    correct_answer: str
    explanation: str


class Flashcard(BaseModel):
    front: str
    back: str


class RevisionQuestion(BaseModel):
    question: str


class Quiz(BaseModel):
    questions: list[QuizQuestion] = Field(default_factory=list)
    mcqs: list[MCQQuestion] = Field(default_factory=list)
    flashcards: list[Flashcard] = Field(default_factory=list)
    revision_questions: list[RevisionQuestion] = Field(default_factory=list)


# ==========================================================
# Study plan models
# ==========================================================

class StudyRequest(BaseModel):
    learning_goal: str
    skill_level: str
    timeline_days: int


class Resource(BaseModel):
    title: str
    url: str | None = None
    resource_type: str
    reason: str


class WeekPlan(BaseModel):
    week: int
    focus: str
    topics: list[str]
    outcome: str
    resources: list[Resource] = Field(default_factory=list)
    quiz: Quiz | None = None


class StudyPlan(BaseModel):
    goal: str
    skill_level: str
    timeline_days: int
    weeks: list[WeekPlan]


# ==========================================================
# Phase 5 progress tracking models
# ==========================================================

class QuizAttempt(BaseModel):
    week_number: int
    quiz_type: str = "weekly"      # weekly or topic
    topic: str | None = None

    score: float                   # percentage score
    total_questions: int
    correct_answers: int

    timestamp: datetime = Field(default_factory=datetime.now)


class StudySession(BaseModel):
    week_number: int | None = None
    topic: str | None = None

    action: str                    # generated_plan, completed_topic,
                                   # completed_week, quiz_attempt

    timestamp: datetime = Field(default_factory=datetime.now)


class UserProgress(BaseModel):
    completed_weeks: list[int] = Field(default_factory=list)

    completed_topics: list[str] = Field(default_factory=list)

    quiz_attempts: list[QuizAttempt] = Field(default_factory=list)

    study_history: list[StudySession] = Field(default_factory=list)

    weak_topics: list[str] = Field(default_factory=list)