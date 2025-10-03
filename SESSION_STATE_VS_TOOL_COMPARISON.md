# Google ADK: Session State vs Tool-Based Multi-Agent Patterns

## Overview

This document compares two different approaches to implementing multi-agent systems in Google ADK:

1. **Tool-Based Approach** - Sub-agent wrapped as `AgentTool`
2. **Session State Approach** - Independent agents sharing data via session state

## Architecture Comparison

### Tool-Based Approach

```
User Query
    ↓
Main Agent
    ↓
Decides to call tool
    ↓
AgentTool(sub_agent)
    ↓
Sub-agent executes
    ↓
Returns JSON to main agent
    ↓
Main agent processes result
    ↓
Response to user
```

**Code Example:**
```python
# Sub-agent
profile_fetcher_agent = LlmAgent(
    name="profile_fetcher",
    output_schema=UserProfile
)

# Wrap as tool
profile_fetcher_tool = AgentTool(agent=profile_fetcher_agent)

# Main agent uses tool
main_agent = LlmAgent(
    name="main_agent",
    tools=[profile_fetcher_tool]
)
```

### Session State Approach

```
User Query
    ↓
SequentialAgent Orchestrator
    ↓
Step 1: Data Fetcher Agent
    - Generates JSON
    - Stores in session.state["key"]
    ↓
Step 2: Presenter Agent
    - Reads from session.state["key"]
    - Presents to user
    ↓
Response to user
```

**Code Example:**
```python
# Sub-agent with output_key
data_fetcher_agent = LlmAgent(
    name="data_fetcher",
    output_schema=UserProfile,
    output_key="fetched_profile"  # ← Stores in session
)

# Main agent (no tools needed)
presenter_agent = LlmAgent(
    name="presenter",
    instruction="Read from session['fetched_profile']"
)

# Orchestrator
system = SequentialAgent(
    name="system",
    sub_agents=[
        data_fetcher_agent,
        presenter_agent
    ]
)
```

## Detailed Comparison

| Aspect | Tool-Based | Session State |
|--------|-----------|---------------|
| **Coupling** | Tight - main agent explicitly calls sub-agent | Loose - agents don't know about each other |
| **Orchestration** | Main agent decides when to call | SequentialAgent controls flow |
| **Execution** | Conditional - main agent chooses | Sequential - always runs in order |
| **State Management** | Implicit - tool return value | Explicit - session state |
| **Flexibility** | High - dynamic invocation | Medium - fixed sequence |
| **Complexity** | Higher - tool wrapping needed | Lower - simple agent chain |
| **Visibility** | Tool invocations in trace | Agent runs in trace |
| **Use Case** | Sub-agent is a "tool" for main agent | Pipeline/workflow processing |
| **Agent Independence** | No - sub-agent is dependent | Yes - fully independent |
| **Reusability** | Sub-agent tied to tool interface | Agents can be reused anywhere |

## When to Use Each Approach

### Use Tool-Based When:

✅ **Dynamic Decision Making**
- Main agent needs to decide **if** and **when** to call sub-agent
- Conditional logic based on user input
- Example: "Only fetch profile if user asks for it"

✅ **Multiple Tool Options**
- Main agent has several tools to choose from
- Sub-agent is one of many capabilities
- Example: Main agent can search web OR fetch profile OR analyze data

✅ **Interactive Workflows**
- User can guide the conversation
- Main agent adapts based on context
- Example: Chatbot that calls different services based on user needs

✅ **Sub-Agent as Capability**
- Sub-agent truly functions as a "tool"
- Main agent is the primary interface
- Example: Assistant with multiple specialized sub-agents

### Use Session State When:

✅ **Fixed Pipelines**
- Workflow always follows the same steps
- No conditional branching needed
- Example: ETL pipeline (Extract → Transform → Load)

✅ **Data Processing Chains**
- Each agent processes data sequentially
- Output of one is input to next
- Example: Data validation → Enrichment → Presentation

✅ **Loose Coupling**
- Agents should be independent
- Easy to add/remove/reorder agents
- Example: Modular data processing system

✅ **State Persistence**
- Need to preserve data across multiple steps
- Multiple agents access same state
- Example: Multi-step form processing

✅ **Simpler Architecture**
- Don't need dynamic tool selection
- Straightforward sequential flow
- Example: Report generation (Fetch → Analyze → Format)

## Implementation Details

### Tool-Based Implementation

**Advantages:**
- Main agent has full control
- Can call sub-agent multiple times
- Can pass different parameters each time
- Conditional execution based on context

**Disadvantages:**
- More complex setup (tool wrapping)
- Tighter coupling between agents
- Harder to test agents independently
- Tool invocation overhead

**Best For:**
- Conversational agents
- Dynamic workflows
- Multi-capability systems
- Interactive applications

### Session State Implementation

**Advantages:**
- Simple, clean architecture
- Agents are fully independent
- Easy to test each agent separately
- Clear data flow through state
- Easy to add new agents to pipeline

**Disadvantages:**
- Fixed execution order
- All agents always run
- Less flexible than tool-based
- Requires careful state key management

**Best For:**
- Data pipelines
- Sequential workflows
- Batch processing
- Report generation
- Multi-step transformations

## Code Patterns

### Accessing Session State in Agents

**In Sub-Agent (Writing):**
```python
data_agent = LlmAgent(
    name="data_agent",
    output_schema=MySchema,
    output_key="my_data"  # ← Automatically stores in session
)
```

**In Main Agent (Reading):**
```python
INSTRUCTION = """
You have access to session state.
The data you need is stored in session["my_data"].
Use this data to answer the user's question.
"""

main_agent = LlmAgent(
    name="main_agent",
    instruction=INSTRUCTION
)
```

### Programmatic Access to Session State

```python
from google.adk.sessions import InMemorySession

# Create session
session = InMemorySession()

# Run agent
await agent.run_async("Query", session=session)

# Access state
data = session.state.get("my_data")
print(f"Retrieved: {data}")
```

## Real-World Examples

### Example 1: Customer Service Bot (Tool-Based)

**Why Tool-Based:**
- User might ask about orders, returns, or FAQs
- Main agent decides which sub-agent to call
- Conditional based on user intent

```python
order_agent_tool = AgentTool(agent=order_lookup_agent)
return_agent_tool = AgentTool(agent=return_processor_agent)
faq_agent_tool = AgentTool(agent=faq_agent)

customer_service_bot = LlmAgent(
    name="customer_service",
    tools=[order_agent_tool, return_agent_tool, faq_agent_tool]
)
```

### Example 2: Report Generator (Session State)

**Why Session State:**
- Always follows same steps: Fetch → Analyze → Format
- Each step builds on previous
- No conditional logic needed

```python
report_system = SequentialAgent(
    name="report_generator",
    sub_agents=[
        data_fetcher_agent,      # Fetches raw data
        data_analyzer_agent,     # Analyzes data
        report_formatter_agent   # Formats final report
    ]
)
```

### Example 3: Research Assistant (Tool-Based)

**Why Tool-Based:**
- User guides the research process
- Assistant decides when to search, summarize, or cite
- Interactive and adaptive

```python
search_tool = AgentTool(agent=search_agent)
summarize_tool = AgentTool(agent=summarizer_agent)
citation_tool = AgentTool(agent=citation_agent)

research_assistant = LlmAgent(
    name="research_assistant",
    tools=[search_tool, summarize_tool, citation_tool]
)
```

### Example 4: Data Validation Pipeline (Session State)

**Why Session State:**
- Fixed validation steps
- Each validator checks different aspects
- All validators always run

```python
validation_pipeline = SequentialAgent(
    name="data_validator",
    sub_agents=[
        schema_validator_agent,    # Check schema
        business_rules_agent,      # Check business rules
        quality_checker_agent,     # Check data quality
        report_generator_agent     # Generate validation report
    ]
)
```

## Performance Considerations

### Tool-Based
- **Overhead:** Tool invocation adds latency
- **API Calls:** Each tool call = separate LLM call
- **Tokens:** Tool descriptions consume tokens
- **Flexibility:** Can optimize by selective calling

### Session State
- **Overhead:** Minimal - just sequential execution
- **API Calls:** One call per agent in sequence
- **Tokens:** No tool description overhead
- **Flexibility:** All agents always run (less efficient if not needed)

## Testing Strategies

### Tool-Based Testing

```python
# Test sub-agent independently
result = await sub_agent.run_async("Test query")

# Test main agent with mock tool
mock_tool = MockAgentTool(return_value={"data": "test"})
main_agent = LlmAgent(tools=[mock_tool])
```

### Session State Testing

```python
# Test each agent independently
session = InMemorySession()
await data_agent.run_async("Test", session=session)
assert "my_data" in session.state

# Test full pipeline
await pipeline.run_async("Test", session=session)
```

## Migration Guide

### From Tool-Based to Session State

1. Remove `AgentTool` wrappers
2. Add `output_key` to sub-agents
3. Update main agent instructions to read from session
4. Wrap in `SequentialAgent`

**Before:**
```python
tool = AgentTool(agent=sub_agent)
main_agent = LlmAgent(tools=[tool])
```

**After:**
```python
sub_agent = LlmAgent(output_key="data")
main_agent = LlmAgent(instruction="Read from session['data']")
system = SequentialAgent(sub_agents=[sub_agent, main_agent])
```

### From Session State to Tool-Based

1. Remove `output_key` from sub-agents
2. Wrap sub-agents with `AgentTool`
3. Update main agent to use tools
4. Remove `SequentialAgent` wrapper

**Before:**
```python
sub_agent = LlmAgent(output_key="data")
system = SequentialAgent(sub_agents=[sub_agent, main_agent])
```

**After:**
```python
sub_agent = LlmAgent(output_schema=Schema)
tool = AgentTool(agent=sub_agent)
main_agent = LlmAgent(tools=[tool])
```

## Best Practices

### Session State Best Practices

1. **Use Clear Key Names**
   ```python
   output_key="user_profile"  # Good
   output_key="data"          # Bad - too generic
   ```

2. **Document State Schema**
   ```python
   # State keys used:
   # - "user_profile": UserProfile - User information
   # - "analysis_result": Analysis - Analysis output
   ```

3. **Validate State Access**
   ```python
   if "my_data" not in session.state:
       raise ValueError("Required data not in session")
   ```

4. **Clean Up State**
   ```python
   # Remove temporary data after use
   session.state.pop("temp_data", None)
   ```

### Tool-Based Best Practices

1. **Clear Tool Descriptions**
   ```python
   AgentTool(
       agent=sub_agent,
       description="Fetches user profile by ID or name"
   )
   ```

2. **Limit Number of Tools**
   - Too many tools confuse the LLM
   - Group related functionality
   - Use 3-7 tools maximum

3. **Test Tool Selection**
   - Verify main agent chooses correct tool
   - Test edge cases
   - Monitor tool usage patterns

## Conclusion

Both patterns are valid and useful:

- **Tool-Based** = Flexibility, dynamic behavior, interactive systems
- **Session State** = Simplicity, fixed pipelines, loose coupling

Choose based on your specific requirements:
- Need conditional logic? → Tool-Based
- Fixed workflow? → Session State
- Interactive system? → Tool-Based
- Data pipeline? → Session State

You can even **combine both approaches** in complex systems!
