import json

from core.models import StudyRequest, StudyPlan


class PlanningAgent:
    def __init__(self, llm_client):
        self.llm_client = llm_client

    def create_plan(self, request: StudyRequest) -> StudyPlan:
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a study planning agent. "
                    "Return ONLY valid JSON. "
                    "Do not include markdown. "
                    "Do not include explanations. "
                    "Do not recommend resources yet. "
                    "Do not generate quizzes yet. "
                    "Do not include a resources field. "
                    "Do not include a quiz field. "
                    "Never use placeholder values such as 'string', 'topic', 'example', or 'TBD'. "
                    "Every focus, topic, and outcome must be specific to the user's learning goal. "
                    "For timeline_days <= 14, create exactly 2 weeks. "
                    "For timeline_days <= 30, create exactly 4 weeks. "
                    "For timeline_days > 30, create one week per 7 days. "
                    "Every topic must be a valid JSON string."
                ),
            },
            {
                "role": "user",
                "content": f"""
Create a structured week-wise study roadmap.

Learning goal: {request.learning_goal}
Skill level: {request.skill_level}
Timeline: {request.timeline_days} days

Return JSON in exactly this format:

{{
  "goal": "{request.learning_goal}",
  "skill_level": "{request.skill_level}",
  "timeline_days": {request.timeline_days},
  "weeks": [
    {{
      "week": 1,
      "focus": "specific weekly focus title",
      "topics": ["specific topic 1", "specific topic 2", "specific topic 3"],
      "outcome": "specific learning outcome for the week"
    }}
  ]
}}
""",
            },
        ]

        raw_response = ""

        for attempt in range(3):
            raw_response = self.llm_client.generate(messages)

            try:
                if raw_response.strip().startswith("User Safety"):
                    raise ValueError("Model returned safety wrapper instead of JSON")

                data = json.loads(raw_response)

                if self._contains_placeholders(data):
                    raise ValueError("Model returned placeholder values")

                return StudyPlan.model_validate(data)

            except Exception as e:
                print(f"[PlanningAgent] Attempt {attempt + 1} failed: {e}")
                print(f"[PlanningAgent] Raw response: {raw_response}")

        raise ValueError(
            f"Failed to parse LLM response as StudyPlan after retries.\n\n"
            f"Raw response:\n{raw_response}"
        )

    def _contains_placeholders(self, data: dict) -> bool:
        bad_values = {
            "string",
            "topic",
            "topics",
            "example",
            "placeholder",
            "tbd",
            "n/a",
            "none",
        }

        for week in data.get("weeks", []):
            values = [
                week.get("focus", ""),
                week.get("outcome", ""),
            ]

            values.extend(week.get("topics", []))

            for value in values:
                if str(value).strip().lower() in bad_values:
                    return True

        return False