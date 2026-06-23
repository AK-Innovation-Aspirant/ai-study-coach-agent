import streamlit as st

from core.models import StudyRequest
from core.llm_client import OpenRouterClient
from agents.orchestrator_agent import OrchestratorAgent
from agents.quiz_agent import QuizAgent

from utils.storage import load_study_plan, save_study_plan


st.set_page_config(
    page_title="AI Study Coach Agent",
    page_icon="📚",
    layout="wide",
)

st.title("📚 AI Study Coach Agent")
st.caption("Phase 5: Progress tracking and memory")

orchestrator = OrchestratorAgent()

if "plan" not in st.session_state:
    st.session_state.plan = load_study_plan()

if "topic_quiz" not in st.session_state:
    st.session_state.topic_quiz = None

if "progress" not in st.session_state:
    st.session_state.progress = orchestrator.get_progress()


with st.sidebar:
    st.header("Study Goal")

    learning_goal = st.text_input("What do you want to learn?", value="world models")
    skill_level = st.selectbox(
        "Current skill level",
        ["beginner", "intermediate", "advanced"],
    )
    timeline_days = st.number_input(
        "Timeline in days",
        min_value=7,
        max_value=180,
        value=14,
        step=1,
    )

    generate = st.button("Generate Study Plan", type="primary")


def resource_card(resource):
    st.markdown(
        f"""
        <div style="
            border: 1px solid #ddd;
            border-radius: 12px;
            padding: 14px;
            margin-bottom: 10px;
            background-color: #fafafa;
        ">
            <p style="margin: 0; font-size: 14px;">
                <strong>{resource.resource_type.upper()}</strong>
            </p>
            <h4 style="margin: 6px 0;">
                <a href="{resource.url}" target="_blank">{resource.title}</a>
            </h4>
            <p style="margin: 0; color: #555;">
                {resource.reason}
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_study_plan_tab(plan):
    progress = st.session_state.progress

    st.header(f"{plan.timeline_days}-Day Study Plan: {plan.goal}")
    st.write(f"**Skill level:** {plan.skill_level}")

    for week in plan.weeks:
        st.divider()
        st.subheader(f"Week {week.week}: {week.focus}")

        if week.week in progress.completed_weeks:
            st.success("Week completed")

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("### Topics")

            for topic in week.topics:
                topic_done = topic in progress.completed_topics

                topic_col, button_col = st.columns([3, 1])

                with topic_col:
                    if topic_done:
                        st.markdown(f"✅ ~~{topic}~~")
                    else:
                        st.markdown(f"- {topic}")

                with button_col:
                    if not topic_done:
                        if st.button(
                            "Complete",
                            key=f"complete_topic_week_{week.week}_{topic}",
                        ):
                            st.session_state.progress = orchestrator.mark_topic_complete(
                                topic=topic,
                                week_number=week.week,
                            )
                            st.rerun()

            st.markdown("### Expected Outcome")
            st.info(week.outcome)

            if week.week not in progress.completed_weeks:
                if st.button(
                    f"Mark Week {week.week} Complete",
                    key=f"complete_week_{week.week}",
                ):
                    st.session_state.progress = orchestrator.mark_week_complete(
                        week.week
                    )
                    st.rerun()

        with col2:
            st.markdown("### Recommended Resources")

            videos = [r for r in week.resources if r.resource_type == "video"]
            articles = [r for r in week.resources if r.resource_type == "article/doc"]
            practice = [r for r in week.resources if r.resource_type == "practice"]

            if videos:
                st.markdown("#### Videos")
                for resource in videos:
                    resource_card(resource)

            if articles:
                st.markdown("#### Articles / Docs")
                for resource in articles:
                    resource_card(resource)

            if practice:
                st.markdown("#### Practice")
                for resource in practice:
                    resource_card(resource)

            if not videos and not articles and not practice:
                st.info("No resources found for this week.")


def render_quiz_center(plan):
    st.header("📝 Quiz Center")

    week_lookup = {week.week: week for week in plan.weeks}
    week_options = list(week_lookup.keys())

    selected_week_number = st.selectbox(
        "Choose a week",
        week_options,
        format_func=lambda week_num: f"Week {week_num}: {week_lookup[week_num].focus}",
        key="quiz_center_week",
    )

    selected_week = week_lookup[selected_week_number]
    quiz = selected_week.quiz

    if not quiz:
        st.info("No quiz generated for this week.")
        return

    if quiz.questions:
        st.markdown("### Short Answer Questions")
        for i, question in enumerate(quiz.questions, start=1):
            with st.expander(f"Question {i}: {question.question}"):
                st.write(f"**Answer:** {question.answer}")

    if quiz.mcqs:
        st.markdown("### MCQs")

        correct_count = 0
        answered_count = 0

        for i, mcq in enumerate(quiz.mcqs, start=1):
            with st.expander(f"MCQ {i}: {mcq.question}"):
                selected = st.radio(
                    "Choose an answer:",
                    mcq.options,
                    key=f"quiz_week_{selected_week.week}_mcq_{i}",
                )

                if selected:
                    answered_count += 1

                if selected == mcq.correct_answer:
                    correct_count += 1

                if st.button(
                    "Check Answer",
                    key=f"quiz_week_{selected_week.week}_check_{i}",
                ):
                    if selected == mcq.correct_answer:
                        st.success("Correct.")
                    else:
                        st.error(f"Incorrect. Correct answer: {mcq.correct_answer}")

                    st.info(mcq.explanation)

        st.divider()

        if st.button(
            f"Submit Week {selected_week.week} Quiz",
            key=f"submit_week_quiz_{selected_week.week}",
        ):
            total_questions = len(quiz.mcqs)
            score = (correct_count / total_questions) * 100 if total_questions else 0

            st.session_state.progress = orchestrator.record_quiz_attempt(
                week_number=selected_week.week,
                score=score,
                total_questions=total_questions,
                correct_answers=correct_count,
                quiz_type="weekly",
                topic=selected_week.focus,
            )

            st.success(f"Quiz saved. Score: {score:.1f}%")

    if quiz.flashcards:
        st.markdown("### Flashcards")
        for i, card in enumerate(quiz.flashcards, start=1):
            card_key = f"quiz_week_{selected_week.week}_flashcard_{i}_flipped"

            if card_key not in st.session_state:
                st.session_state[card_key] = False

            if st.button(
                card.back if st.session_state[card_key] else card.front,
                key=f"quiz_week_{selected_week.week}_flashcard_button_{i}",
                use_container_width=True,
            ):
                st.session_state[card_key] = not st.session_state[card_key]
                st.rerun()


def render_revision_center(plan):
    st.header("🔄 Revision Center")

    week_lookup = {week.week: week for week in plan.weeks}
    week_options = list(week_lookup.keys())

    selected_week_number = st.selectbox(
        "Choose a week to revise",
        week_options,
        format_func=lambda week_num: f"Week {week_num}: {week_lookup[week_num].focus}",
        key="revision_center_week",
    )

    selected_week = week_lookup[selected_week_number]
    quiz = selected_week.quiz

    if quiz and quiz.revision_questions:
        st.markdown("### Revision Questions")
        for i, revision in enumerate(quiz.revision_questions, start=1):
            st.markdown(f"{i}. {revision.question}")
    else:
        st.info("No revision questions generated for this week.")

    st.divider()
    st.markdown("### Topic-Based Quiz")

    topic = st.text_input(
        "Enter a topic to quiz yourself on",
        value=selected_week.focus,
        key="topic_quiz_topic",
    )

    topic_difficulty = st.selectbox(
        "Difficulty",
        ["beginner", "intermediate", "advanced"],
        key="topic_quiz_difficulty",
    )

    num_questions = st.number_input(
        "Number of MCQs",
        min_value=1,
        max_value=10,
        value=5,
        step=1,
        key="topic_quiz_num_questions",
    )

    if st.button("Generate Topic Quiz", key="generate_topic_quiz"):
        with st.spinner("Generating topic quiz..."):
            llm_client = OpenRouterClient()
            quiz_agent = QuizAgent(llm_client)
            st.session_state.topic_quiz = quiz_agent.generate_topic_quiz(
                topic=topic,
                skill_level=topic_difficulty,
                num_questions=num_questions,
            )

    if st.session_state.topic_quiz and st.session_state.topic_quiz.mcqs:
        st.markdown("### Generated Topic Quiz")

        correct_count = 0

        for i, mcq in enumerate(st.session_state.topic_quiz.mcqs, start=1):
            with st.expander(f"Topic MCQ {i}: {mcq.question}"):
                selected = st.radio(
                    "Choose an answer:",
                    mcq.options,
                    key=f"topic_quiz_mcq_{i}",
                )

                if selected == mcq.correct_answer:
                    correct_count += 1

                if st.button("Check Answer", key=f"topic_quiz_check_{i}"):
                    if selected == mcq.correct_answer:
                        st.success("Correct.")
                    else:
                        st.error(f"Incorrect. Correct answer: {mcq.correct_answer}")

                    st.info(mcq.explanation)

        if st.button("Submit Topic Quiz", key="submit_topic_quiz"):
            total_questions = len(st.session_state.topic_quiz.mcqs)
            score = (correct_count / total_questions) * 100 if total_questions else 0

            st.session_state.progress = orchestrator.record_quiz_attempt(
                week_number=selected_week.week,
                score=score,
                total_questions=total_questions,
                correct_answers=correct_count,
                quiz_type="topic",
                topic=topic,
            )

            st.success(f"Topic quiz saved. Score: {score:.1f}%")


def render_progress_dashboard():
    progress = st.session_state.progress

    st.header("📊 Progress Dashboard")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Completed Topics", len(progress.completed_topics))

    with col2:
        st.metric("Completed Weeks", len(progress.completed_weeks))

    with col3:
        st.metric("Quiz Attempts", len(progress.quiz_attempts))

    st.divider()

    st.markdown("### Weak Areas")

    if progress.weak_topics:
        for topic in progress.weak_topics:
            st.warning(topic)
    else:
        st.success("No weak areas detected yet.")

    st.markdown("### Quiz History")

    if progress.quiz_attempts:
        for attempt in reversed(progress.quiz_attempts):
            st.markdown(
                f"""
                **{attempt.quiz_type.title()} Quiz**  
                Week: {attempt.week_number}  
                Topic: {attempt.topic or "N/A"}  
                Score: {attempt.score:.1f}%  
                Correct: {attempt.correct_answers}/{attempt.total_questions}  
                Time: {attempt.timestamp}
                """
            )
            st.divider()
    else:
        st.info("No quiz attempts recorded yet.")

    st.markdown("### Study History")

    if progress.study_history:
        for session in reversed(progress.study_history[-20:]):
            st.markdown(
                f"""
                **{session.action}**  
                Week: {session.week_number or "N/A"}  
                Topic: {session.topic or "N/A"}  
                Time: {session.timestamp}
                """
            )
    else:
        st.info("No study activity recorded yet.")


if generate:
    request = StudyRequest(
        learning_goal=learning_goal,
        skill_level=skill_level,
        timeline_days=timeline_days,
    )

    with st.spinner("Creating roadmap, finding resources, and generating quizzes..."):
        st.session_state.plan = orchestrator.create_study_plan(request)
        save_study_plan(st.session_state.plan)
        st.session_state.progress = orchestrator.reset_progress()

    st.success("Multi-agent study plan generated.")


if st.session_state.plan:
    plan = st.session_state.plan

    study_tab, quiz_tab, revision_tab, progress_tab = st.tabs(
        [
            "📚 Study Plan",
            "📝 Quiz Center",
            "🔄 Revision Center",
            "📊 Progress Dashboard",
        ]
    )

    with study_tab:
        render_study_plan_tab(plan)

    with quiz_tab:
        render_quiz_center(plan)

    with revision_tab:
        render_revision_center(plan)

    with progress_tab:
        render_progress_dashboard()

else:
    st.info("Enter a learning goal and generate a study plan.")