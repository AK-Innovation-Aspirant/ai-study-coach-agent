from models import StudyPlan
from resource_tool import ResourceTool


class ResourceAgent:
    def __init__(self):
        self.resource_tool = ResourceTool()

    def enrich_plan(self, study_plan: StudyPlan) -> StudyPlan:
        return self.resource_tool.add_resources(study_plan)