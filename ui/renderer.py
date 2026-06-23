from core.models import StudyPlan

def render_study_plan(plan: StudyPlan) -> str:
    lines = []

    lines.append(f"# {plan.timeline_days}-Day Study Plan: {plan.goal}")
    lines.append("")
    lines.append(f"**Skill level:** {plan.skill_level}")
    lines.append("")

    for week in plan.weeks:
        lines.append(f"## Week {week.week}: {week.focus}")
        lines.append("")

        lines.append("### Topics")
        for topic in week.topics:
            lines.append(f"- {topic}")
        lines.append("")

        lines.append("### Expected Outcome")
        lines.append(f"- {week.outcome}")
        lines.append("")

        if week.resources:
            lines.append("### Recommended Resources")
            for resource in week.resources:
                lines.append(
                    f"- **{resource.resource_type.title()}**: "
                    f"[{resource.title}]({resource.url})"
                )
                lines.append(f"  - Why: {resource.reason}")
            lines.append("")

        if week.quiz and week.quiz.questions:
            lines.append("### Quiz")
            for i, question in enumerate(week.quiz.questions, start=1):
                lines.append(f"{i}. {question.question}")
                lines.append(f"   - Answer: {question.answer}")
            lines.append("")

    return "\n".join(lines)