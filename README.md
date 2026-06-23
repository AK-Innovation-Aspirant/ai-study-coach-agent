# 📚 AI Study Coach Agent

An agentic AI application that generates personalized study plans, recommends learning resources, and creates quizzes for revision.

## Features

* 🧠 Multi-agent architecture
* 📅 Personalized study plan generation
* 📚 Automatic resource discovery

  * Articles and websites (DuckDuckGo Search)
  * YouTube videos
* ❓ Quiz generation

  * Open-ended questions
  * Multiple-choice questions
  * Flashcards
  * Revision prompts
* 🌐 Streamlit web interface
* 🔗 OpenRouter LLM integration

---

## Project Structure

```
agentic_ai/
├── app.py                 # Streamlit UI
├── main.py                # CLI entry point
├── llm_client.py          # OpenRouter API client
├── orchestrator_agent.py  # Coordinates all agents
├── planner_agent.py       # Creates study plans
├── resource_agent.py      # Adds learning resources
├── resource_tool.py       # Web search utilities
├── youtube_tool.py        # YouTube API integration
├── resource_ranker.py     # Resource deduplication and ranking
├── quiz_agent.py          # Quiz generation
├── renderer.py            # Markdown rendering
├── models.py              # Pydantic models
├── requirements.txt
└── .env
```

---

## Installation

### 1. Clone the repository

```bash
git clone <repository-url>
cd agentic_ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it:

**Windows**

```bash
.venv\Scripts\activate
```

**Linux / macOS**

```bash
source .venv/bin/activate
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

```
                Orchestrator Agent
                         │
      ┌──────────────────┼─────────────────┐
      │                  │                 │
Planning Agent     Resource Agent      Quiz Agent
      │                  │                 │
 OpenRouter LLM    Search + YouTube    OpenRouter LLM
```

---

## Dependencies

* Streamlit
* Pydantic
* Requests
* python-dotenv
* DuckDuckGo Search (ddgs)

---

## Future Improvements

* Progress tracking
* Spaced repetition
* Persistent storage
* PDF export
* LangGraph integration
* Multi-LLM support

## License

MIT License
