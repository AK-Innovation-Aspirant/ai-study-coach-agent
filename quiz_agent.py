import json

from models import (
    StudyPlan,
    WeekPlan,
    Quiz,
    QuizQuestion,
    MCQQuestion,
    Flashcard,
    RevisionQuestion,
)


class QuizAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def add_quizzes_to_plan(self, plan: StudyPlan) -> StudyPlan:
        quizzes_by_week = self._generate_quizzes_for_plan(plan)

        for week in plan.weeks:
            week.quiz = quizzes_by_week.get(
                week.week,
                self._fallback_quiz(week),
            )

        return plan

    def generate_topic_quiz(
        self,
        topic: str,
        skill_level: str,
        num_questions: int = 5,
    ) -> Quiz:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a topic-based quiz generation agent. "
                    "Return ONLY valid JSON. "
                    "Do not include markdown or explanations outside the JSON. "
                    "The JSON must contain exactly these keys: "
                    "questions, mcqs, flashcards, revision_questions. "
                    "questions must be an empty list. "
                    "flashcards must be an empty list. "
                    "revision_questions must be an empty list. "
                    "mcqs must contain only MCQ objects with question, options, "
                    "correct_answer, and explanation."
                ),
            },
            {
                "role": "user",
                "content": f"""
Create a topic-based quiz.

Topic: {topic}
Skill level: {skill_level}
Number of MCQs: {num_questions}

Return JSON in exactly this format:

{{
  "questions": [],
  "mcqs": [
    {{
      "question": "string",
      "options": ["string", "string", "string", "string"],
      "correct_answer": "string",
      "explanation": "string"
    }}
  ],
  "flashcards": [],
  "revision_questions": []
}}
""",
            },
        ]

        for attempt in range(2):
            try:
                raw_response = self.llm_client.generate(messages)
                data = json.loads(raw_response)

                if "mcqs" not in data or not data["mcqs"]:
                    raise ValueError("Topic quiz did not include MCQs")

                data["questions"] = []
                data["flashcards"] = []
                data["revision_questions"] = []

                return Quiz.model_validate(data)

            except Exception as e:
                print(f"[QuizAgent] Topic quiz attempt {attempt + 1} failed: {e}")
                try:
                    print(f"[QuizAgent] Raw response: {raw_response}")
                except UnboundLocalError:
                    pass

        return Quiz(
            mcqs=[
                MCQQuestion(
                    question=f"What is the main idea of {topic}?",
                    options=[
                        topic,
                        "An unrelated concept",
                        "A previous topic",
                        "A general study strategy",
                    ],
                    correct_answer=topic,
                    explanation=f"This quiz is focused on {topic}.",
                )
            ]
        )

    def _generate_quizzes_for_plan(self, plan: StudyPlan) -> dict[int, Quiz]:
        weeks_payload = [
            {
                "week": week.week,
                "focus": week.focus,
                "topics": week.topics,
                "outcome": week.outcome,
            }
            for week in plan.weeks
        ]

        messages = [
            {
                "role": "system",
                "content": (
                    "You are a quiz and revision generation agent. "
                    "Return ONLY valid JSON. "
                    "Do not include markdown or explanations outside the JSON. "
                    "Generate learning support for every week in one response. "
                    "Each quiz object MUST contain exactly these four top-level keys: "
                    "questions, mcqs, flashcards, revision_questions. "
                    "Do NOT put MCQs inside questions. "
                    "Do NOT put flashcards inside questions. "
                    "Do NOT put revision questions inside questions. "
                    "questions must contain only objects with question and answer. "
                    "mcqs must contain only objects with question, options, correct_answer, explanation. "
                    "flashcards must contain only objects with front and back. "
                    "revision_questions must contain only objects with question."
                ),
            },
            {
                "role": "user",
                "content": f"""
Create quizzes and revision material for this full study plan.

Goal: {plan.goal}
Skill level: {plan.skill_level}
Timeline days: {plan.timeline_days}
Weeks: {weeks_payload}

Return JSON in exactly this format:

{{
  "weeks": [
    {{
      "week": 1,
      "quiz": {{
        "questions": [
          {{
            "question": "string",
            "answer": "string"
          }},
          {{
            "question": "string",
            "answer": "string"
          }},
          {{
            "question": "string",
            "answer": "string"
          }}
        ],
        "mcqs": [
          {{
            "question": "string",
            "options": ["string", "string", "string", "string"],
            "correct_answer": "string",
            "explanation": "string"
          }},
          {{
            "question": "string",
            "options": ["string", "string", "string", "string"],
            "correct_answer": "string",
            "explanation": "string"
          }},
          {{
            "question": "string",
            "options": ["string", "string", "string", "string"],
            "correct_answer": "string",
            "explanation": "string"
          }}
        ],
        "flashcards": [
          {{
            "front": "string",
            "back": "string"
          }},
          {{
            "front": "string",
            "back": "string"
          }},
          {{
            "front": "string",
            "back": "string"
          }}
        ],
        "revision_questions": [
          {{
            "question": "string"
          }},
          {{
            "question": "string"
          }},
          {{
            "question": "string"
          }}
        ]
      }}
    }}
  ]
}}

For each week, create:
- exactly 3 short-answer questions
- exactly 3 MCQs
- exactly 3 flashcards
- exactly 3 revision questions
""",
            },
        ]

        for attempt in range(2):
            try:
                raw_response = self.llm_client.generate(messages)
                data = json.loads(raw_response)

                quizzes_by_week = {}

                for week_item in data.get("weeks", []):
                    week_number = week_item.get("week")
                    quiz_data = week_item.get("quiz", {})

                    quiz_data = self._normalize_quiz_data(quiz_data)

                    quiz = Quiz.model_validate(quiz_data)
                    quizzes_by_week[week_number] = quiz

                if not quizzes_by_week:
                    raise ValueError("No quizzes returned")

                for week in plan.weeks:
                    if week.week not in quizzes_by_week:
                        quizzes_by_week[week.week] = self._fallback_quiz(week)

                return quizzes_by_week

            except Exception as e:
                print(f"[QuizAgent] Batch attempt {attempt + 1} failed: {e}")
                try:
                    print(f"[QuizAgent] Raw response: {raw_response}")
                except UnboundLocalError:
                    pass

        return {
            week.week: self._fallback_quiz(week)
            for week in plan.weeks
        }

    def _normalize_quiz_data(self, quiz_data: dict) -> dict:
        normalized = {
            "questions": [],
            "mcqs": [],
            "flashcards": [],
            "revision_questions": [],
        }

        for item in quiz_data.get("questions", []):
            if isinstance(item, str):
                normalized["questions"].append(
                    {
                        "question": item,
                        "answer": "Review the week's topic materials to answer this.",
                    }
                )
            elif isinstance(item, dict):
                if "question" in item and "answer" in item:
                    normalized["questions"].append(item)
                elif (
                    "question" in item
                    and "options" in item
                    and "correct_answer" in item
                    and "explanation" in item
                ):
                    normalized["mcqs"].append(item)
                elif "front" in item and "back" in item:
                    normalized["flashcards"].append(item)
                elif "question" in item:
                    normalized["revision_questions"].append(
                        {"question": item["question"]}
                    )

        for item in quiz_data.get("mcqs", []):
            if isinstance(item, dict):
                normalized["mcqs"].append(item)

        for item in quiz_data.get("flashcards", []):
            if isinstance(item, dict) and "front" in item and "back" in item:
                normalized["flashcards"].append(
                    {
                        "front": item["front"],
                        "back": item["back"],
                    }
                )

        for item in quiz_data.get("revision_questions", []):
            if isinstance(item, str):
                normalized["revision_questions"].append({"question": item})
            elif isinstance(item, dict) and "question" in item:
                normalized["revision_questions"].append(
                    {"question": item["question"]}
                )

        return normalized

    def _fallback_quiz(self, week: WeekPlan) -> Quiz:
        return Quiz(
            questions=[
                QuizQuestion(
                    question=f"What is the main focus of Week {week.week}?",
                    answer=week.focus,
                )
            ],
            mcqs=[
                MCQQuestion(
                    question=f"What is the main focus of Week {week.week}?",
                    options=[
                        week.focus,
                        "Unrelated topic",
                        "Previous week's topic",
                        "General review",
                    ],
                    correct_answer=week.focus,
                    explanation=(
                        f"The main focus of Week {week.week} is {week.focus}."
                    ),
                )
            ],
            flashcards=[
                Flashcard(
                    front=f"Week {week.week} Focus",
                    back=week.focus,
                )
            ],
            revision_questions=[
                RevisionQuestion(
                    question=(
                        f"Explain the main ideas behind {week.focus} "
                        "without looking at notes."
                    )
                )
            ],
        )