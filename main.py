from models import StudyRequest
from orchestrator_agent import OrchestratorAgent
from renderer import render_study_plan


def main():
    print("AI Study Coach Agent - Phase 3")
    print("--------------------------------")

    learning_goal = input("Learning goal: ")
    skill_level = input("Skill level: ")
    timeline_days = int(input("Timeline in days: "))

    request = StudyRequest(
        learning_goal=learning_goal,
        skill_level=skill_level,
        timeline_days=timeline_days,
    )

    orchestrator = OrchestratorAgent()
    plan = orchestrator.create_study_plan(request)

    print("\nGenerated Multi-Agent Study Plan")
    print("================================")
    print(render_study_plan(plan))


if __name__ == "__main__":
    main()