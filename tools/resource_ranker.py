from urllib.parse import urlparse, parse_qs

from core.models import Resource


class ResourceRanker:
    def __init__(self):
        self.seen_urls: set[str] = set()
        self.seen_titles: set[str] = set()

    def _domain(self, url: str | None) -> str:
        if not url:
            return ""

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        return domain

    def _normalize_url(self, url: str | None) -> str:
        if not url:
            return ""

        parsed = urlparse(url)
        domain = parsed.netloc.lower()

        if domain.startswith("www."):
            domain = domain[4:]

        # Normalize YouTube URLs
        if domain in ["youtube.com", "m.youtube.com"]:
            query = parse_qs(parsed.query)
            video_id = query.get("v", [""])[0]
            if video_id:
                return f"youtube.com/watch?v={video_id}"

        if domain == "youtu.be":
            video_id = parsed.path.strip("/")
            if video_id:
                return f"youtube.com/watch?v={video_id}"

        path = parsed.path.rstrip("/")
        return f"{domain}{path}"

    def _normalize_title(self, title: str) -> str:
        return " ".join(title.lower().strip().split())

    def _is_duplicate(self, resource: Resource) -> bool:
        normalized_url = self._normalize_url(resource.url)
        normalized_title = self._normalize_title(resource.title)

        if normalized_url and normalized_url in self.seen_urls:
            return True

        if normalized_title in self.seen_titles:
            return True

        return False

    def _mark_seen(self, resource: Resource) -> None:
        normalized_url = self._normalize_url(resource.url)
        normalized_title = self._normalize_title(resource.title)

        if normalized_url:
            self.seen_urls.add(normalized_url)

        self.seen_titles.add(normalized_title)

    def _domain_matches(self, domain: str, domains: list[str]) -> bool:
        return domain in domains or any(domain.endswith("." + d) for d in domains)

    def _domain_category_score(
        self,
        domain: str,
        resource_type: str,
        skill_level: str,
        week_number: int,
    ) -> int:
        score = 0

        official_signals = [
            "docs.",
            "developer.",
            "learn.",
            "support.",
            "help.",
            "documentation.",
        ]

        learning_domains = [
            "medium.com",
            "substack.com",
            "dev.to",
            "hashnode.dev",
            "freecodecamp.org",
            "coursera.org",
            "edx.org",
            "khanacademy.org",
            "wikipedia.org",
        ]

        academic_domains = [
            "arxiv.org",
            "scholar.google.com",
            "semanticscholar.org",
            "researchgate.net",
            "acm.org",
            "ieee.org",
            "springer.com",
            "nature.com",
            "sciencedirect.com",
        ]

        practice_domains = [
            "github.com",
            "kaggle.com",
            "leetcode.com",
            "exercism.org",
            "hackerrank.com",
            "codewars.com",
        ]

        video_domains = [
            "youtube.com",
            "youtu.be",
            "vimeo.com",
        ]

        low_quality_domains = [
            "facebook.com",
            "pinterest.com",
            "quora.com",
        ]

        if any(signal in domain for signal in official_signals):
            score += 3

        if self._domain_matches(domain, learning_domains):
            if skill_level == "beginner":
                score += 3
            elif week_number == 1:
                score += 2
            else:
                score += 1

        if self._domain_matches(domain, academic_domains):
            if skill_level == "beginner":
                score += 1
            elif week_number == 1:
                score += 2
            else:
                score += 4

        if self._domain_matches(domain, practice_domains):
            score += 4 if resource_type == "practice" else 2

        if self._domain_matches(domain, video_domains):
            score += 4 if resource_type == "video" else 1

        if self._domain_matches(domain, low_quality_domains):
            score -= 3

        return score

    def _title_score(
        self,
        title: str,
        resource_type: str,
        skill_level: str,
        week_number: int,
    ) -> int:
        title = title.lower()
        score = 0

        beginner_words = [
            "beginner",
            "introduction",
            "intro",
            "explained",
            "tutorial",
            "guide",
            "crash course",
            "basics",
            "from scratch",
            "fundamentals",
        ]

        refresher_words = [
            "refresher",
            "review",
            "recap",
            "overview",
        ]

        advanced_words = [
            "paper",
            "survey",
            "benchmark",
            "state of the art",
            "sota",
            "architecture",
            "implementation",
            "research",
        ]

        practice_words = [
            "exercise",
            "practice",
            "project",
            "hands-on",
            "notebook",
            "github",
            "example",
            "assignment",
            "problems",
        ]

        if skill_level == "beginner":
            if any(word in title for word in beginner_words):
                score += 4
            if any(word in title for word in advanced_words):
                score -= 1

        elif skill_level == "advanced":
            if any(word in title for word in advanced_words):
                score += 4

            if week_number == 1:
                if any(word in title for word in beginner_words):
                    score += 1
                if any(word in title for word in refresher_words):
                    score += 3
            else:
                if "beginner" in title:
                    score -= 1

        else:
            if any(word in title for word in beginner_words + advanced_words):
                score += 2

        if resource_type == "practice" and any(word in title for word in practice_words):
            score += 5

        if resource_type == "article/doc" and any(
            word in title for word in ["docs", "documentation", "guide", "tutorial", "handbook"]
        ):
            score += 3

        if resource_type == "video" and any(
            word in title for word in ["explained", "tutorial", "course", "lecture", "overview"]
        ):
            score += 3

        return score

    def score_resource(
        self,
        resource: Resource,
        skill_level: str,
        week_number: int,
    ) -> int:
        domain = self._domain(resource.url)

        score = 0
        score += self._domain_category_score(
            domain=domain,
            resource_type=resource.resource_type,
            skill_level=skill_level,
            week_number=week_number,
        )
        score += self._title_score(
            title=resource.title,
            resource_type=resource.resource_type,
            skill_level=skill_level,
            week_number=week_number,
        )

        if not resource.url:
            score -= 5

        return score

    def rank(
        self,
        resources: list[Resource],
        skill_level: str,
        week_number: int,
        max_results: int,
    ) -> list[Resource]:
        candidates = []

        for resource in resources:
            if self._is_duplicate(resource):
                continue

            candidates.append(resource)

        ranked = sorted(
            candidates,
            key=lambda r: self.score_resource(
                resource=r,
                skill_level=skill_level,
                week_number=week_number,
            ),
            reverse=True,
        )

        selected = ranked[:max_results]

        for resource in selected:
            self._mark_seen(resource)

        return selected