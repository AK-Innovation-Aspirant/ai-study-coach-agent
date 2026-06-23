import json
from pathlib import Path

from core.models import StudyPlan


STUDY_PLAN_PATH = Path("data/study_plan.json")


def save_study_plan(plan: StudyPlan) -> None:
    STUDY_PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(STUDY_PLAN_PATH, "w", encoding="utf-8") as f:
        json.dump(
            plan.model_dump(mode="json"),
            f,
            indent=2,
            ensure_ascii=False,
        )


def load_study_plan() -> StudyPlan | None:
    if not STUDY_PLAN_PATH.exists():
        return None

    try:
        with open(STUDY_PLAN_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)

        return StudyPlan.model_validate(data)

    except Exception:
        return None