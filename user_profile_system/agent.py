"""Main orchestrator using SequentialAgent to coordinate independent agents."""

from google.adk.agents import SequentialAgent
from .data_fetcher import data_fetcher_agent
from .presenter import presenter_agent


# Create a sequential agent that runs:
# 1. Data Fetcher Agent - Fetches data and stores JSON in session state
# 2. Presenter Agent - Reads JSON from session state and presents to user
user_profile_system = SequentialAgent(
    name="user_profile_system",
    description="User profile system with independent data fetching and presentation agents",
    sub_agents=[
        data_fetcher_agent,  # First: Fetch data and store in session
        presenter_agent      # Second: Read from session and present
    ]
)


# Export as root_agent for ADK
root_agent = user_profile_system
