# 📚 AI Study Coach Agent

An agentic AI application that generates personalized study plans, recommends learning resources, and provides interactive quizzes and revision support.

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
* 🌐 Streamlit web interface
* 🔗 OpenRouter LLM integration
* ⚡ Batched quiz generation for low API usage
* 🛡️ Robust JSON repair and fallback handling

---

## Project Structure

```text
agentic_ai/
├── app.py                     # Streamlit UI
├── main.py                    # CLI entry point
├── requirements.txt
├── README.md
├── .env
│
├── agents/
│   ├── __init__.py
│   ├── orchestrator_agent.py  # Coordinates all agents
│   ├── planner_agent.py       # Creates study plans
│   ├── resource_agent.py      # Adds learning resources
│   └── quiz_agent.py          # Quiz generation
│
├── core/
│   ├── __init__.py
│   ├── llm_client.py          # OpenRouter API client
│   └── models.py              # Pydantic models
│
├── tools/
│   ├── __init__.py
│   ├── resource_tool.py       # Web search utilities
│   ├── youtube_tool.py        # YouTube API integration
│   └── resource_ranker.py     # Resource deduplication and ranking
│
└── ui/
    ├── __init__.py
    └── renderer.py            # Markdown rendering
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd agentic_ai
```

### 2. Create a Conda environment

```bash
conda create -n agentic python=3.12
```

Activate it:

```bash
conda activate agentic
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Variables

Create a `.env` file:

```env
OPENROUTER_API_KEY=your_openrouter_key
YOUTUBE_API_KEY=your_youtube_api_key
```

---

## Running the Application

### Streamlit UI

```bash
streamlit run app.py
```

### Command Line Version

```bash
python main.py
```

---

## Architecture

```text
                   Orchestrator Agent
                            │
        ┌───────────────────┼──────────────────┐
        │                   │                  │
        ▼                   ▼                  ▼
 Planning Agent       Resource Agent       Quiz Agent
        │                   │                  │
 OpenRouter LLM      Search + YouTube    OpenRouter LLM
```

### Current Pipeline

```text
Frontend (Streamlit)
        │
        ▼
OrchestratorAgent
        │
 ┌──────┼─────────┐
 ▼      ▼         ▼
PlanningAgent ResourceAgent QuizAgent
    │         │         │
 OpenRouter  DDGS +     OpenRouter
    │       YouTube       │
 StudyPlan  Resources   All quizzes
                        (batched)
```

---

## API Usage

Initial study plan generation requires only two LLM calls:

1. **PlanningAgent**

   * Generates the week-by-week roadmap.

2. **QuizAgent**

   * Generates all quizzes, flashcards, MCQs, and revision questions in one batched request.

Resource retrieval uses external search and does not consume LLM calls.

Topic-based quizzes are generated on demand and require one additional LLM call.

---

## Streamlit Interface

### 📚 Study Plan

* Week-by-week roadmap
* Topics
* Expected outcomes
* Ranked learning resources

### 📝 Quiz Center

* Short-answer questions
* Multiple-choice questions
* Answer explanations
* Interactive flashcards

### 🔄 Revision Center

* Revision questions
* Topic-based quiz generation
* Separate storage of topic quizzes in session state

---

## Dependencies

* Streamlit
* Pydantic
* Requests
* python-dotenv
* DuckDuckGo Search (ddgs)

---

## Current Status

### Phase 1

✅ Study plan generation

### Phase 2

✅ Resource discovery and ranking

### Phase 3

✅ Multi-agent orchestration

### Phase 4

✅ Interactive quizzes and revision system

* Batched quiz generation
* Topic-based quizzes
* Flashcards
* Robust JSON repair
* Fallback mechanisms

### Phase 5 (Planned)

Progress tracking and memory

* Quiz scores
* Completed topics
* Weak area detection
* Study history
* Persistent storage

### Phase 6 (Planned)

Adaptive learning

* Reschedule missed tasks
* Dynamic roadmap updates
* Automatic revision scheduling
* Personalized study coach

---

## Future Improvements

* Progress dashboard
* Persistent storage
* Weak-topic analytics
* Adaptive roadmap generation
* Spaced repetition
* PDF export
* Multi-LLM support
* LangGraph integration (if workflow complexity justifies it)

---

## License

MIT License
