from models import StudyRequest, StudyPlan
from llm_client import OpenRouterClient
from planner_agent import PlanningAgent
from resource_agent import ResourceAgent
from quiz_agent import QuizAgent


class OrchestratorAgent:
    def __init__(self):
        self.llm_client = OpenRouterClient()

        self.planning_agent = PlanningAgent(self.llm_client)
        self.resource_agent = ResourceAgent()
        self.quiz_agent = QuizAgent(self.llm_client)

    def create_study_plan(self, request: StudyRequest) -> StudyPlan:
        plan = self.planning_agent.create_plan(request)

        plan = self.resource_agent.enrich_plan(plan)

        plan = self.quiz_agent.add_quizzes_to_plan(plan)

        return plan