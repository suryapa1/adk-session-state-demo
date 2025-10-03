# ADK Session State Demo - Independent Agents with JSON Handover

This project demonstrates a **session-state-based multi-agent architecture** using Google's Agent Development Kit (ADK), where:
- A **sub-agent runs independently** and stores JSON in session state
- A **main agent reads from session state** and presents data to the user
- **No AgentTool** - agents communicate through shared session state

## Architecture

```
User Query
    ↓
┌─────────────────────────────────────┐
│  Sequential Agent (Orchestrator)    │
│                                     │
│  Step 1: Data Fetcher Agent         │
│  - Fetches user profile             │
│  - Generates structured JSON        │
│  - Stores in session["fetched_profile"] │
│                                     │
│  Step 2: Presenter Agent            │
│  - Reads session["fetched_profile"] │
│  - Presents data to user            │
│  - No tool invocation needed        │
└─────────────────────────────────────┘
    ↓
User Response
```

## Key Differences from Tool-Based Approach

### This Demo (Session State)
```python
# Sub-agent stores JSON independently
data_fetcher_agent = LlmAgent(
    output_schema=UserProfile,
    output_key="fetched_profile"  # ← Stores in session
)

# Main agent reads from session (no tools)
presenter_agent = LlmAgent(
    instruction="Read from session['fetched_profile']"
)

# Orchestrator runs them sequentially
system = SequentialAgent(agents=[
    data_fetcher_agent,
    presenter_agent
])
```

### Previous Demo (Tool-Based)
```python
# Sub-agent wrapped as tool
tool = AgentTool(agent=sub_agent)

# Main agent uses tool
main_agent = LlmAgent(
    tools=[tool]  # ← Sub-agent as tool
)
```

## Benefits of Session State Approach

1. **Loose Coupling** - Agents don't need to know about each other
2. **Independent Execution** - Each agent runs on its own
3. **Flexible Orchestration** - Easy to add/remove/reorder agents
4. **State Persistence** - Data persists across agent executions
5. **No Tool Overhead** - Simpler architecture, no tool wrapping

## Project Structure

```
adk-session-state-demo/
├── user_profile_system/
│   ├── __init__.py
│   ├── agent.py              # SequentialAgent orchestrator
│   ├── data_fetcher.py       # Sub-agent: stores JSON
│   ├── presenter.py          # Main agent: reads JSON
│   └── schema.py             # Pydantic models
├── pyproject.toml
├── .env
└── README.md
```

## Setup Instructions

### Prerequisites
- Python 3.11+
- Poetry
- Google Gemini API key

### Installation

1. **Navigate to the directory**:
   ```bash
   cd adk-session-state-demo
   ```

2. **Install dependencies**:
   ```bash
   poetry install
   ```

3. **API key is already configured** in `.env`

## Running the Demo

### Option 1: ADK Web UI (Recommended)

Launch the interactive web interface:

```bash
poetry run adk web --host 0.0.0.0 --port 8001
```

Then open your browser to the URL shown.

**Try these queries:**
- "Tell me about Alice Johnson"
- "What projects is Bob working on?"
- "What are Carol's skills?"
- "When did David join the company?"

### Option 2: Command Line

```bash
poetry run adk run . --query "Tell me about Alice Johnson"
```

### Option 3: Python Script

```python
from user_profile_system import root_agent
from google.adk.sessions import InMemorySession

# Create a session
session = InMemorySession()

# Run the agent
async def test_agent():
    response = await root_agent.run_async(
        user_message="Tell me about Alice Johnson",
        session=session
    )
    print(response)
    
    # Check session state
    print("Session state:", session.state)
    print("Fetched profile:", session.state.get("fetched_profile"))

import asyncio
asyncio.run(test_agent())
```

## How It Works

### Step 1: Data Fetcher Agent

**File:** `user_profile_system/data_fetcher.py`

```python
data_fetcher_agent = LlmAgent(
    name="data_fetcher",
    model="gemini-2.0-flash-exp",
    instruction=DATA_FETCHER_INSTRUCTION,
    output_schema=UserProfile,      # ← Enforces JSON structure
    output_key="fetched_profile"    # ← Stores in session state
)
```

**What happens:**
1. Agent receives user query (e.g., "Tell me about Alice")
2. Agent generates JSON matching `UserProfile` schema
3. JSON is automatically stored in `session.state["fetched_profile"]`
4. Agent execution completes

### Step 2: Presenter Agent

**File:** `user_profile_system/presenter.py`

```python
presenter_agent = LlmAgent(
    name="presenter",
    model="gemini-2.0-flash-exp",
    instruction=PRESENTER_INSTRUCTION  # Knows to read from session
)
```

**What happens:**
1. Agent starts execution
2. Agent instruction tells it to read `session.state["fetched_profile"]`
3. Agent formats the JSON data naturally
4. Agent presents to user

### Step 3: Sequential Orchestration

**File:** `user_profile_system/agent.py`

```python
user_profile_system = SequentialAgent(
    name="user_profile_system",
    agents=[
        data_fetcher_agent,  # Runs first
        presenter_agent      # Runs second
    ]
)
```

**What happens:**
1. User sends query
2. `SequentialAgent` runs `data_fetcher_agent` first
3. Data is stored in session state
4. `SequentialAgent` runs `presenter_agent` second
5. Presenter reads from session and responds

## Session State Flow

```python
# Initial state
session.state = {}

# After data_fetcher_agent runs
session.state = {
    "fetched_profile": {
        "user_id": "U001",
        "name": "Alice Johnson",
        "email": "alice.johnson@techcorp.com",
        "role": "Senior Data Scientist",
        "department": "AI Research",
        "skills": ["Python", "TensorFlow", "NLP", "Deep Learning"],
        "projects": ["Chatbot Enhancement", "Sentiment Analysis"],
        "status": "active",
        "joined_date": "2022-03-15",
        "last_login": "2025-10-02T09:15:00Z"
    }
}

# presenter_agent reads from session.state["fetched_profile"]
# and presents it to the user
```

## Mock Data

The demo includes 4 mock users:
- **Alice Johnson** (U001) - Senior Data Scientist
- **Bob Smith** (U002) - Product Manager
- **Carol Martinez** (U003) - DevOps Engineer
- **David Chen** (U004) - UX Designer (inactive)

## Key ADK Concepts Demonstrated

1. **SequentialAgent** - Orchestrates multiple agents in sequence
2. **Session State** - Shared data store between agents
3. **output_key** - Automatically stores agent output in session
4. **output_schema** - Enforces structured JSON output
5. **Independent Agents** - No tool wrapping needed

## Advantages Over Tool-Based Approach

| Feature | Session State | Tool-Based |
|---------|---------------|------------|
| Coupling | Loose | Tight |
| Complexity | Lower | Higher |
| Flexibility | High | Medium |
| State Management | Built-in | Manual |
| Agent Independence | Yes | No |
| Orchestration | Easy | Complex |

## When to Use Each Approach

### Use Session State When:
- Agents should be independent
- You want loose coupling
- State needs to persist across steps
- You're building pipelines/workflows
- Agents don't need to "call" each other

### Use Tool-Based When:
- Main agent needs to decide when to call sub-agent
- Conditional execution is needed
- Sub-agent is truly a "tool" for the main agent
- You want dynamic invocation

## Extending the Demo

### Add More Agents to Pipeline

```python
user_profile_system = SequentialAgent(
    agents=[
        data_fetcher_agent,      # Step 1: Fetch data
        data_enricher_agent,     # Step 2: Enrich data
        data_validator_agent,    # Step 3: Validate data
        presenter_agent          # Step 4: Present to user
    ]
)
```

### Access Session State in Custom Code

```python
from google.adk.sessions import InMemorySession

session = InMemorySession()

# Run agent
await root_agent.run_async("Tell me about Alice", session=session)

# Access stored data
profile = session.state.get("fetched_profile")
print(f"Retrieved: {profile['name']}")
```

### Add Parallel Execution

```python
from google.adk.agents import ParallelAgent

# Fetch multiple data sources in parallel
parallel_fetcher = ParallelAgent(
    agents=[
        profile_fetcher_agent,
        projects_fetcher_agent,
        skills_fetcher_agent
    ]
)
```

## Troubleshooting

### Session state is empty
- Check that `output_key` is set on the data fetcher agent
- Verify the agent is running successfully
- Check the execution order in `SequentialAgent`

### Presenter can't find data
- Ensure data fetcher runs before presenter
- Check the `output_key` matches what presenter expects
- Verify session is shared between agents

### JSON validation errors
- Check Pydantic model matches expected structure
- Verify all required fields are present
- Review agent instructions for clarity

## Resources

- **ADK Documentation:** https://google.github.io/adk-docs/
- **SequentialAgent Guide:** https://google.github.io/adk-docs/agents/sequential-agents/
- **Session Management:** https://google.github.io/adk-docs/sessions/
- **ADK Samples:** https://github.com/google/adk-samples

## License

Apache 2.0 - See LICENSE file for details
