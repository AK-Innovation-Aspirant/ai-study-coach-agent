# 📚 AI Study Coach Agent

An agentic AI application that generates personalized study plans, recommends learning resources, provides interactive quizzes, and maintains persistent learning progress across sessions.

## Features

* 🧠 Multi-agent architecture
* 📅 Personalized study plan generation
* 📚 Automatic resource discovery

  * Articles and websites (DuckDuckGo Search)
  * YouTube videos
* ❓ Interactive quiz generation

  * Open-ended questions
  * Multiple-choice questions
  * Flashcards
  * Revision prompts
* 🔄 Topic-based quizzes on demand
* 📊 Progress dashboard
* ✅ Topic and week completion tracking
* 📈 Quiz history and weak-area detection
* 💾 Persistent study plans and progress
* 🌐 Streamlit web interface
* 🔗 OpenRouter LLM integration
* ⚡ Batched quiz generation for low API usage
* 🛡️ Robust JSON repair and fallback handling

---

# Project Structure

```text
agentic_ai/
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── .env
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator_agent.py
│   ├── planner_agent.py
│   ├── resource_agent.py
│   ├── quiz_agent.py
│   └── progress_agent.py
│
├── core/
│   ├── __init__.py
│   ├── llm_client.py
│   └── models.py
│
├── tools/
│   ├── __init__.py
│   ├── resource_tool.py
│   ├── youtube_tool.py
│   └── resource_ranker.py
│
├── utils/
│   └── storage.py
│
├── data/
│   ├── study_plan.json
│   └── progress.json
│
└── ui/
    ├── __init__.py
    └── renderer.py
```

---

# Installation

## 1. Clone the repository

```bash
git clone https://github.com/AK-Innovation-Aspirant/ai-study-coach-agent
cd ai-study-coach-agent
```

## 2. Create a Conda environment

```bash
conda create -n agentic python=3.11
```

Activate it:

```bash
conda activate agentic
```

## 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

# Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_key
YOUTUBE_API_KEY=your_youtube_api_key
```

## Obtaining an OpenRouter API Key

1. Visit:

   https://openrouter.ai

2. Sign in or create an account.

3. Navigate to:

   **API Keys**

4. Create a new API key.

5. Copy the key and place it into:

```env
OPENROUTER_API_KEY=your_openrouter_key
```

---

## Obtaining a YouTube API Key

1. Visit:

   https://console.cloud.google.com/

2. Create a new Google Cloud project (or select an existing project).

3. Navigate to:

   **APIs & Services → Library**

4. Search for:

   **YouTube Data API v3**

5. Click **Enable**.

6. Navigate to:

   **APIs & Services → Credentials**

7. Click:

   **Create Credentials → API Key**

8. Copy the generated key and place it into:

```env
YOUTUBE_API_KEY=your_youtube_api_key
```

---

## Example `.env`

```env
OPENROUTER_API_KEY=sk-or-v1-xxxxxxxxxxxxxxxx

YOUTUBE_API_KEY=AIzaSyxxxxxxxxxxxxxxxx
```

The `.env` file should be placed in the root of the project directory and should not be committed to Git.

---

# Running the Application

## Streamlit UI

```bash
streamlit run app.py
```

## Command Line Version

```bash
python main.py
```

---

# Architecture

```text
Frontend (Streamlit)
        │
        ▼
OrchestratorAgent
        │
┌───────┼─────────┬──────────┐
▼       ▼         ▼          ▼
Planning Resource Quiz    Progress
 Agent    Agent  Agent      Agent
    │        │      │          │
OpenRouter DDGS+  OpenRouter Persistent
   LLM     YouTube    LLM      Storage
```

---

# API Usage

Initial study plan generation requires only two LLM calls:

1. **PlanningAgent**

   * Generates the week-by-week roadmap.

2. **QuizAgent**

   * Generates all short-answer questions, MCQs, flashcards, and revision questions in one batched request.

Resource retrieval uses external search and does not consume LLM calls.

Topic-based quizzes are generated on demand and require one additional LLM call.

---

# Streamlit Interface

## 📚 Study Plan

* Week-by-week roadmap
* Topics and outcomes
* Ranked learning resources
* Topic completion tracking
* Week completion tracking

## 📝 Quiz Center

* Short-answer questions
* Multiple-choice questions
* Answer explanations
* Interactive flashcards
* Quiz score recording

## 🔄 Revision Center

* Revision questions
* Topic-based quiz generation

## 📊 Progress Dashboard

* Completed topics
* Completed weeks
* Quiz history and scores
* Weak areas detected from quiz performance
* Study history with timestamps
* Persistent progress across restarts

---

# Persistent Memory

Progress is stored locally and survives restarts.

Files:

```text
data/study_plan.json
data/progress.json
```

Stored information:

* Completed topics
* Completed weeks
* Quiz attempts
* Weak areas
* Study history

Generating a new study plan automatically resets progress.

---

# Weak Area Detection

Quiz performance is used to identify weak topics automatically.

Each quiz attempt records:

* Quiz type
* Topic
* Score percentage
* Number of correct answers
* Timestamp

Weak topics are determined using an average score threshold.

Current threshold:

```text
70%
```

Topics whose average quiz score falls below 70% are automatically added to the weak-area list and displayed in the Progress Dashboard.

This information serves as the foundation for future adaptive learning features planned in Phase 6.

---

# Current Status

## Phase 1

✅ Study plan generation

## Phase 2

✅ Resource discovery and ranking

## Phase 3

✅ Multi-agent orchestration

## Phase 4

✅ Interactive quizzes and revision system

* Batched quiz generation
* Topic-based quizzes
* Flashcards
* Robust JSON repair
* Fallback mechanisms

## Phase 5

✅ Progress tracking and memory

* Persistent storage
* Topic completion tracking
* Week completion tracking
* Quiz history
* Weak-area detection using a 70% score threshold
* Study history
* Progress dashboard
* Session recovery

## Phase 6 (Planned)

Adaptive learning

* Dynamic roadmap updates
* Automatic revision scheduling
* Missed-task recovery
* Personalized study coach

---

# Future Improvements

* Adaptive learning agent
* Automatic revision scheduling
* Missed-task recovery
* Spaced repetition
* PDF export
* Multi-LLM support
* LangGraph integration (if workflow complexity justifies it)

---

# License

MIT License
