import time
from ddgs import DDGS

from core.models import Resource, WeekPlan, StudyPlan
from tools.youtube_tool import YoutubeTool
from tools.resource_ranker import ResourceRanker


class ResourceTool:
    def __init__(self, max_results_per_type: int = 2):
        self.max_results_per_type = max_results_per_type
        self.youtube_tool = YoutubeTool(max_results=max_results_per_type * 3)
        self.ranker = ResourceRanker()

    def _search(
        self,
        query: str,
        max_results: int = 6,
        retries: int = 2,
    ) -> list[dict]:
        for attempt in range(retries + 1):
            try:
                with DDGS() as ddgs:
                    return list(ddgs.text(query, max_results=max_results))
            except Exception as e:
                print(f"[ResourceTool] Search failed: {query}")
                print(f"[ResourceTool] Attempt {attempt + 1}: {e}")
                time.sleep(1)

        return []
    
    def _make_resource(
        self,
        result: dict,
        resource_type: str,
        fallback_reason: str,
    ) -> Resource:
        snippet = (
            result.get("body")
            or result.get("snippet")
            or result.get("description")
            or fallback_reason
        )

        return Resource(
            title=result.get("title", "Untitled resource"),
            url=result.get("href"),
            resource_type=resource_type,
            reason=snippet,
        )

    def _make_queries(self, week: WeekPlan, goal: str) -> dict[str, str]:
        main_topic = week.focus
        topic_terms = " ".join(week.topics[:2])

        return {
            "video": f"{goal} {main_topic} explained tutorial",
            "article/doc": f"{goal} {main_topic} {topic_terms} guide documentation",
            "practice": f"{goal} {main_topic} hands-on project exercises examples",
        }

    def _search_articles_or_docs(self, query: str) -> list[Resource]:
        results = self._search(query, max_results=self.max_results_per_type * 4)

        return [
            self._make_resource(
                result,
                "article/doc",
                "Article, guide, or documentation related to this week’s topics.",
            )
            for result in results
        ]

    def _search_practice(self, query: str) -> list[Resource]:
        results = self._search(query, max_results=self.max_results_per_type * 4)

        return [
            self._make_resource(
                result,
                "practice",
                "Practice resource related to this week’s topics.",
            )
            for result in results
        ]

    def _search_videos_with_fallback(self, query: str) -> list[Resource]:
        try:
            return self.youtube_tool.search_videos(query)
        except Exception as e:
            print(f"[ResourceTool] YouTube API failed: {e}")
            print("[ResourceTool] Falling back to DDGS video search.")

            results = self._search(
                f"{query} site:youtube.com",
                max_results=self.max_results_per_type * 4,
            )

            return [
                self._make_resource(
                    result,
                    "video",
                    "Video related to this week’s learning focus.",
                )
                for result in results
            ]

    def add_resources_to_week(
        self,
        week: WeekPlan,
        goal: str,
        skill_level: str,
    ) -> WeekPlan:
        queries = self._make_queries(week, goal)

        video_resources = self._search_videos_with_fallback(queries["video"])
        article_resources = self._search_articles_or_docs(queries["article/doc"])
        practice_resources = self._search_practice(queries["practice"])

        ranked_videos = self.ranker.rank(
            video_resources,
            skill_level=skill_level,
            week_number=week.week,
            max_results=self.max_results_per_type,
        )

        ranked_articles = self.ranker.rank(
            article_resources,
            skill_level=skill_level,
            week_number=week.week,
            max_results=self.max_results_per_type,
        )

        ranked_practice = self.ranker.rank(
            practice_resources,
            skill_level=skill_level,
            week_number=week.week,
            max_results=self.max_results_per_type,
        )
        week.resources = ranked_videos + ranked_articles + ranked_practice
        return week

    def add_resources(self, study_plan: StudyPlan) -> StudyPlan:
        for week in study_plan.weeks:
            self.add_resources_to_week(
                week=week,
                goal=study_plan.goal,
                skill_level=study_plan.skill_level,
            )

        return study_plan