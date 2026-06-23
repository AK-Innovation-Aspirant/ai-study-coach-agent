from pydantic import BaseModel, Field


# Quiz related models

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