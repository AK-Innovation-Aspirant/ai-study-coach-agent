import json
from pathlib import Path

from core.models import UserProgress, QuizAttempt, StudySession


class ProgressAgent:
    def __init__(self, progress_path: str = "data/progress.json"):
        self.progress_path = Path(progress_path)
        self.progress_path.parent.mkdir(parents=True, exist_ok=True)
        self.progress = self.load_progress()

    def load_progress(self) -> UserProgress:
        if not self.progress_path.exists():
            return UserProgress()

        try:
            with open(self.progress_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return UserProgress.model_validate(data)
        except Exception:
            return UserProgress()

    def save_progress(self) -> None:
        with open(self.progress_path, "w", encoding="utf-8") as f:
            json.dump(
                self.progress.model_dump(mode="json"),
                f,
                indent=2,
                ensure_ascii=False,
            )

    def get_progress(self) -> UserProgress:
        return self.progress

    def mark_topic_complete(self, topic: str, week_number: int | None = None) -> UserProgress:
        if topic not in self.progress.completed_topics:
            self.progress.completed_topics.append(topic)

        self.progress.study_history.append(
            StudySession(
                week_number=week_number,
                topic=topic,
                action="completed_topic",
            )
        )

        self.save_progress()
        return self.progress

    def mark_week_complete(self, week_number: int) -> UserProgress:
        if week_number not in self.progress.completed_weeks:
            self.progress.completed_weeks.append(week_number)

        self.progress.study_history.append(
            StudySession(
                week_number=week_number,
                action="completed_week",
            )
        )

        self.save_progress()
        return self.progress

    def record_quiz_attempt(
        self,
        week_number: int,
        score: float,
        total_questions: int,
        correct_answers: int,
        quiz_type: str = "weekly",
        topic: str | None = None,
    ) -> UserProgress:
        attempt = QuizAttempt(
            week_number=week_number,
            quiz_type=quiz_type,
            topic=topic,
            score=score,
            total_questions=total_questions,
            correct_answers=correct_answers,
        )

        self.progress.quiz_attempts.append(attempt)

        self.progress.study_history.append(
            StudySession(
                week_number=week_number,
                topic=topic,
                action="quiz_attempt",
            )
        )

        self.update_weak_topics()
        self.save_progress()
        return self.progress

    def update_weak_topics(self, threshold: float = 70.0) -> list[str]:
        topic_scores: dict[str, list[float]] = {}

        for attempt in self.progress.quiz_attempts:
            if attempt.topic:
                topic_scores.setdefault(attempt.topic, []).append(attempt.score)

        weak_topics = []

        for topic, scores in topic_scores.items():
            average_score = sum(scores) / len(scores)
            if average_score < threshold:
                weak_topics.append(topic)

        self.progress.weak_topics = weak_topics
        return weak_topics

    def reset_progress(self) -> UserProgress:
        self.progress = UserProgress()
        self.save_progress()
        return self.progress