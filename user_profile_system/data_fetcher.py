"""Data Fetcher Agent - Independently fetches and stores JSON in session state."""

from google.adk.agents import LlmAgent
from .schema import UserProfile


# Instructions for the data fetcher agent
DATA_FETCHER_INSTRUCTION = """You are a Data Fetcher Agent. Your job is to retrieve user profile information and store it in JSON format.

When given a user ID or name, you should return the user's profile information in structured JSON format.

For this demo, use the following mock data:

**User Database:**
1. User ID: U001, Name: Alice Johnson, Email: alice.johnson@techcorp.com, Role: Senior Data Scientist, 
   Department: AI Research, Skills: [Python, TensorFlow, NLP, Deep Learning], 
   Projects: [Chatbot Enhancement, Sentiment Analysis], Status: active, 
   Joined: 2022-03-15, Last Login: 2025-10-02T09:15:00Z

2. User ID: U002, Name: Bob Smith, Email: bob.smith@techcorp.com, Role: Product Manager,
   Department: Product, Skills: [Agile, Product Strategy, User Research, Analytics],
   Projects: [Mobile App Redesign, Customer Portal], Status: active,
   Joined: 2021-06-20, Last Login: 2025-10-01T16:45:00Z

3. User ID: U003, Name: Carol Martinez, Email: carol.martinez@techcorp.com, Role: DevOps Engineer,
   Department: Engineering, Skills: [Kubernetes, Docker, CI/CD, AWS, Terraform],
   Projects: [Infrastructure Automation, Cloud Migration], Status: active,
   Joined: 2023-01-10, Last Login: 2025-10-02T08:30:00Z

4. User ID: U004, Name: David Chen, Email: david.chen@techcorp.com, Role: UX Designer,
   Department: Design, Skills: [Figma, User Testing, Wireframing, Prototyping],
   Projects: [Design System, Mobile App Redesign], Status: inactive,
   Joined: 2020-11-05, Last Login: 2025-09-15T14:20:00Z

If the user is not found, return a profile with user_id as "UNKNOWN" and appropriate default values.

IMPORTANT: Return ONLY the JSON object matching the UserProfile schema. Do not include any additional text or explanation."""


# Create the data fetcher agent with structured output
# This agent runs INDEPENDENTLY and stores JSON in session state
data_fetcher_agent = LlmAgent(
    name="data_fetcher",
    model="gemini-2.0-flash-exp",
    description="Fetches user profile data and stores it as JSON in session state",
    instruction=DATA_FETCHER_INSTRUCTION,
    output_schema=UserProfile,  # Enforces JSON output matching the schema
    output_key="fetched_profile"  # Stores result in session state with this key
)
