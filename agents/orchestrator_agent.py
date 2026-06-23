from core.models import StudyRequest, StudyPlan
from core.llm_client import OpenRouterClient
from agents.planner_agent import PlanningAgent
from agents.resource_agent import ResourceAgent
from agents.quiz_agent import QuizAgent
from agents.progress_agent import ProgressAgent


class OrchestratorAgent:
    def __init__(self):
        self.llm_client = OpenRouterClient()

        self.planning_agent = PlanningAgent(self.llm_client)
        self.resource_agent = ResourceAgent()
        self.quiz_agent = QuizAgent(self.llm_client)
        self.progress_agent = ProgressAgent()

    def create_study_plan(self, request: StudyRequest) -> StudyPlan:
        plan = self.planning_agent.create_plan(request)

        plan = self.resource_agent.enrich_plan(plan)

        plan = self.quiz_agent.add_quizzes_to_plan(plan)

        return plan
    
    def get_progress(self):
        return self.progress_agent.get_progress()

    def mark_topic_complete(self, topic, week_number=None):
        return self.progress_agent.mark_topic_complete(
            topic,
            week_number,
        )

    def mark_week_complete(self, week_number):
        return self.progress_agent.mark_week_complete(
            week_number,
        )

    def record_quiz_attempt(
        self,
        week_number,
        score,
        total_questions,
        correct_answers,
        quiz_type="weekly",
        topic=None,
    ):
        return self.progress_agent.record_quiz_attempt(
            week_number=week_number,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
            quiz_type=quiz_type,
            topic=topic,
        )
    
    def reset_progress(self):
        return self.progress_agent.reset_progress()