# Adding Custom Tools to MCP Toolbox with Looker

**Complete Guide - All Files in One Document**

Last Updated: January 2025

---

## 📋 Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [File 1: custom_tools.yaml](#file-1-custom_toolsyaml)
4. [File 2: custom_service.py](#file-2-custom_servicepy)
5. [Setup Instructions](#setup-instructions)
6. [Running the System](#running-the-system)
7. [What You'll See](#what-youll-see)
8. [Customization Examples](#customization-examples)
9. [Troubleshooting](#troubleshooting)
10. [Common Use Cases](#common-use-cases)

---

## Overview

This guide shows how to add **custom tools** to Google's MCP Toolbox alongside **prebuilt Looker tools**, all running in a **single MCP server instance**.

### What You'll Achieve

- ✅ **One MCP server** with prebuilt Looker tools + your custom tools
- ✅ **Single UI** to view and test all tools
- ✅ **One endpoint** for AI assistants to connect
- ✅ **Easy integration** of custom Python logic, ML models, or external APIs

### Key Components

1. **custom_tools.yaml** - Configuration file defining your custom tools
2. **custom_service.py** - Python HTTP service implementing your custom tools
3. **MCP Toolbox** - Runs with `--prebuilt looker --config custom_tools.yaml`

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      MCP Toolbox Server                      │
│                     (Port 5000 + UI)                         │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  Prebuilt Looker Tools          Custom Tools                 │
│  ├── get_models                 ├── hello_world              │
│  ├── get_explores               ├── echo_message             │
│  ├── get_dimensions             ├── enhance_looker_data      │
│  ├── get_measures               └── (your custom tools)      │
│  ├── query                                                    │
│  ├── query_sql                         ↓                     │
│  ├── query_url                    Calls HTTP                 │
│  ├── make_look                         ↓                     │
│  ├── run_look                                                │
│  └── get_looks          ┌─────────────────────────────┐     │
│                         │  Custom Python Service      │     │
│         ↓               │  (Port 8080)                │     │
│    Looker API           │  - /hello                   │     │
│                         │  - /echo                    │     │
│                         │  - /enhance                 │     │
│                         │  - Your endpoints...        │     │
│                         └─────────────────────────────┘     │
└─────────────────────────────────────────────────────────────┘
```

---

## File 1: custom_tools.yaml

**Purpose:** Configuration file that defines your custom tools and connects them to the MCP Toolbox.

**Location:** Save this as `custom_tools.yaml` in your project directory.

```yaml
# custom_tools.yaml
# MCP Toolbox Configuration - Combines Prebuilt Looker + Custom Tools

# ============================================================================
# SOURCES SECTION
# Define where tools get their data from
# ============================================================================

sources:
  # Looker source (required for prebuilt Looker tools)
  looker-source:
    kind: looker
    base_url: ${LOOKER_BASE_URL}           # Set via environment variable
    client_id: ${LOOKER_CLIENT_ID}         # Set via environment variable
    client_secret: ${LOOKER_CLIENT_SECRET} # Set via environment variable
    verify_ssl: true
    timeout: 600s
  
  # Custom HTTP service source
  custom-service:
    kind: http
    base_url: http://localhost:8080  # Your Python service
    timeout: 30s

# ============================================================================
# TOOLS SECTION
# Define available tools and their configurations
# ============================================================================

tools:
  # ==========================================================================
  # CUSTOM TOOL #1: Hello World (GET Request)
  # ==========================================================================
  hello_world:
    kind: http-get
    source: custom-service
    endpoint: /hello
    description: |
      Simple hello world tool that returns a greeting message.
      
      This tool demonstrates a basic GET request with optional parameters.
      
      Parameters:
      - name: The name to greet (optional, defaults to 'World')
      
      Example usage:
      "Say hello to Alice"
      
      Returns:
      {
        "message": "Hello, Alice!",
        "status": "success"
      }
    input_schema:
      type: object
      properties:
        name:
          type: string
          description: Name to greet
          default: World
  
  # ==========================================================================
  # CUSTOM TOOL #2: Echo Message (POST Request)
  # ==========================================================================
  echo_message:
    kind: http-post
    source: custom-service
    endpoint: /echo
    description: |
      Echoes back a message with additional metadata.
      
      This tool demonstrates a POST request with required and optional parameters.
      
      Parameters:
      - message: The message to echo back (required)
      - include_timestamp: Whether to include timestamp (optional, default: false)
      
      Example usage:
      "Echo the message 'Hello MCP' with timestamp"
      
      Returns:
      {
        "original": "Hello MCP",
        "echo": "You said: Hello MCP",
        "length": 9,
        "timestamp": "2025-01-24T12:00:00"
      }
    input_schema:
      type: object
      properties:
        message:
          type: string
          description: Message to echo back
        include_timestamp:
          type: boolean
          description: Include timestamp in response
          default: false
      required:
        - message
  
  # ==========================================================================
  # CUSTOM TOOL #3: Enhance Looker Data (POST Request)
  # ==========================================================================
  enhance_looker_data:
    kind: http-post
    source: custom-service
    endpoint: /enhance
    description: |
      Enhances Looker query results with custom analytics or ML predictions.
      
      This tool demonstrates how to create a custom tool that works with
      Looker data. The typical workflow is:
      
      1. First use Looker prebuilt tools to query data (e.g., 'query' tool)
      2. Then pass the results to this tool for enhancement
      
      Parameters:
      - data: The Looker query results as JSON object (required)
      - enhancement_type: Type of enhancement to apply (optional)
        Options: 'summary', 'analysis', 'forecast'
        Default: 'summary'
      
      Example usage:
      "Query sales data from Looker and enhance it with forecast analysis"
      
      Returns:
      {
        "enhancement_type": "forecast",
        "original_data": {...},
        "insights": ["Insight 1", "Insight 2"],
        "metadata": {
          "processed_at": "2025-01-24T12:00:00",
          "records_analyzed": 150
        }
      }
      
      You can customize this to:
      - Apply ML models for predictions
      - Add statistical analysis
      - Enrich with external data sources
      - Apply business rules or calculations
    input_schema:
      type: object
      properties:
        data:
          type: object
          description: Data from Looker query to enhance
        enhancement_type:
          type: string
          enum: [summary, analysis, forecast]
          description: Type of enhancement to apply
          default: summary
      required:
        - data
  
  # ==========================================================================
  # ADD YOUR CUSTOM TOOLS HERE
  # ==========================================================================
  
  # Example: Add more custom tools by following the pattern above
  # 
  # my_custom_tool:
  #   kind: http-post
  #   source: custom-service
  #   endpoint: /my-endpoint
  #   description: |
  #     Description of what your tool does
  #   input_schema:
  #     type: object
  #     properties:
  #       param1:
  #         type: string
  #         description: Description of parameter
  #     required:
  #       - param1
```

---

## File 2: custom_service.py

**Purpose:** Python HTTP service that implements the custom tools defined in the YAML configuration.

**Location:** Save this as `custom_service.py` in your project directory.

```python
#!/usr/bin/env python3
"""
Custom MCP Tools Service
Provides HTTP endpoints for custom tools in MCP Toolbox

This service runs alongside MCP Toolbox and provides custom tool implementations.
Each endpoint corresponds to a tool defined in custom_tools.yaml.
"""

from flask import Flask, request, jsonify
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# ============================================================================
# ENDPOINT #1: Hello World
# ============================================================================

@app.route('/hello', methods=['GET'])
def hello():
    """
    Simple hello world endpoint
    
    Query Parameters:
    - name: Name to greet (optional, defaults to 'World')
    
    Returns:
    - JSON with greeting message
    """
    try:
        name = request.args.get('name', 'World')
        logger.info(f"Hello endpoint called with name: {name}")
        
        return jsonify({
            "message": f"Hello, {name}!",
            "status": "success",
            "service": "custom-mcp-tools"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in hello endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


# ============================================================================
# ENDPOINT #2: Echo Message
# ============================================================================

@app.route('/echo', methods=['POST'])
def echo():
    """
    Echo endpoint that returns the message with metadata
    
    Request Body (JSON):
    - message: Message to echo (required)
    - include_timestamp: Include timestamp (optional, default: false)
    
    Returns:
    - JSON with echoed message and metadata
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                "error": "Request body is required",
                "status": "error"
            }), 400
        
        message = data.get('message', '')
        if not message:
            return jsonify({
                "error": "Message parameter is required",
                "status": "error"
            }), 400
        
        include_timestamp = data.get('include_timestamp', False)
        
        logger.info(f"Echo endpoint called with message: {message}")
        
        response = {
            "original_message": message,
            "echoed_message": f"You said: {message}",
            "message_length": len(message),
            "status": "success"
        }
        
        if include_timestamp:
            response["timestamp"] = datetime.now().isoformat()
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error in echo endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


# ============================================================================
# ENDPOINT #3: Enhance Looker Data
# ============================================================================

@app.route('/enhance', methods=['POST'])
def enhance():
    """
    Enhance Looker data with custom analytics
    
    This is a template endpoint - customize it with your actual logic:
    - ML model predictions
    - Statistical analysis
    - Business rules
    - External API calls
    
    Request Body (JSON):
    - data: Looker query results (required)
    - enhancement_type: Type of enhancement (optional)
      Options: 'summary', 'analysis', 'forecast'
    
    Returns:
    - JSON with enhanced data and insights
    """
    try:
        data = request.json
        if not data:
            return jsonify({
                "error": "Request body is required",
                "status": "error"
            }), 400
        
        looker_data = data.get('data', {})
        if not looker_data:
            return jsonify({
                "error": "Data parameter is required",
                "status": "error"
            }), 400
        
        enhancement_type = data.get('enhancement_type', 'summary')
        
        logger.info(f"Enhance endpoint called with enhancement_type: {enhancement_type}")
        
        # =====================================================================
        # CUSTOMIZE THIS SECTION WITH YOUR LOGIC
        # =====================================================================
        
        if enhancement_type == 'summary':
            result = {
                "enhancement_type": "summary",
                "original_data": looker_data,
                "summary": f"Data contains {len(str(looker_data))} characters",
                "insights": [
                    "This is a sample insight",
                    "Replace with your actual analytics",
                    "Add ML predictions here"
                ],
                "metadata": {
                    "processed_at": datetime.now().isoformat(),
                    "enhancement_applied": True
                }
            }
            
        elif enhancement_type == 'analysis':
            result = {
                "enhancement_type": "analysis",
                "original_data": looker_data,
                "analysis": {
                    "description": "Detailed analysis results",
                    "metrics": {
                        "data_size": len(str(looker_data)),
                        "processed_at": datetime.now().isoformat()
                    }
                },
                "insights": [
                    "Analysis insight 1",
                    "Analysis insight 2"
                ]
            }
            
        elif enhancement_type == 'forecast':
            result = {
                "enhancement_type": "forecast",
                "original_data": looker_data,
                "forecast": {
                    "description": "Forecast predictions would go here",
                    "predictions": [100, 105, 110, 115, 120],
                    "confidence_score": 0.85
                },
                "insights": [
                    "Forecast shows upward trend",
                    "Confidence level is high"
                ]
            }
            
        else:
            return jsonify({
                "error": f"Invalid enhancement_type: {enhancement_type}",
                "valid_types": ["summary", "analysis", "forecast"],
                "status": "error"
            }), 400
        
        return jsonify(result), 200
        
    except Exception as e:
        logger.error(f"Error in enhance endpoint: {str(e)}")
        return jsonify({
            "error": str(e),
            "status": "error"
        }), 500


# ============================================================================
# HEALTH CHECK ENDPOINT
# ============================================================================

@app.route('/health', methods=['GET'])
def health():
    """
    Health check endpoint
    
    Returns:
    - JSON with service status
    """
    return jsonify({
        "status": "healthy",
        "service": "custom-mcp-tools",
        "timestamp": datetime.now().isoformat(),
        "endpoints": [
            "GET /hello",
            "POST /echo",
            "POST /enhance",
            "GET /health"
        ]
    }), 200


# ============================================================================
# ADD YOUR CUSTOM ENDPOINTS HERE
# ============================================================================

# Example: Add more endpoints following the pattern above
#
# @app.route('/my-endpoint', methods=['POST'])
# def my_custom_endpoint():
#     """Your custom endpoint implementation"""
#     try:
#         data = request.json
#         # Your logic here
#         return jsonify({"result": "your result"}), 200
#     except Exception as e:
#         logger.error(f"Error: {str(e)}")
#         return jsonify({"error": str(e)}), 500


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    print("\n" + "="*70)
    print("🚀 Custom MCP Tools Service Starting...")
    print("="*70)
    print(f"\n📍 Service URL: http://localhost:8080")
    print(f"\n📝 Available Endpoints:")
    print(f"   GET  /hello?name=YourName")
    print(f"   POST /echo")
    print(f"   POST /enhance")
    print(f"   GET  /health")
    print("\n" + "="*70 + "\n")
    
    # Run Flask app
    app.run(
        host='0.0.0.0',
        port=8080,
        debug=True
    )
```

---

## Setup Instructions

### Prerequisites

1. **Python 3.8+** installed
2. **MCP Toolbox** binary downloaded from [Google's GenAI Toolbox](https://github.com/googleapis/genai-toolbox)
3. **Looker credentials** (base URL, client ID, client secret)

### Step 1: Install Python Dependencies

```bash
# Install Flask (only dependency needed)
pip install flask

# Or if using a virtual environment:
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install flask
```

### Step 2: Set Environment Variables

Create a file `setup_env.sh`:

```bash
#!/bin/bash
# Looker Configuration
export LOOKER_BASE_URL="https://your-looker-instance.com"
export LOOKER_CLIENT_ID="your_client_id"
export LOOKER_CLIENT_SECRET="your_client_secret"
export LOOKER_VERIFY_SSL="true"

echo "✅ Environment variables set!"
```

Make it executable and run:

```bash
chmod +x setup_env.sh
source setup_env.sh
```

### Step 3: Create the Files

1. Copy the YAML configuration above and save as `custom_tools.yaml`
2. Copy the Python service code above and save as `custom_service.py`
3. Make the Python file executable:

```bash
chmod +x custom_service.py
```

---

## Running the System

### Terminal 1: Start Custom Service

```bash
# Start the Python service
python3 custom_service.py
```

You should see:
```
======================================================================
🚀 Custom MCP Tools Service Starting...
======================================================================

📍 Service URL: http://localhost:8080

📝 Available Endpoints:
   GET  /hello?name=YourName
   POST /echo
   POST /enhance
   GET  /health

======================================================================

 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:8080
 * Running on http://192.168.1.x:8080
```

### Terminal 2: Start MCP Toolbox

```bash
# Load environment variables
source setup_env.sh

# Start MCP Toolbox with prebuilt Looker + custom tools
./toolbox --prebuilt looker --config custom_tools.yaml --port 5000 --ui
```

You should see:
```
MCP Toolbox started successfully
Server running on http://localhost:5000
UI available at: http://localhost:5000
```

### Terminal 3: Open the UI

Open your browser and navigate to:
```
http://localhost:5000
```

---

## What You'll See

### In the MCP Toolbox UI

**Prebuilt Looker Tools (11 tools):**
- `get_models` - List all LookML models
- `get_explores` - List explores in a model
- `get_dimensions` - List dimensions in an explore
- `get_measures` - List measures in an explore
- `get_filters` - List filters in an explore
- `get_parameters` - List parameters in an explore
- `query` - Run a Looker query and get results
- `query_sql` - Get SQL for a Looker query
- `query_url` - Get URL to a Looker query
- `get_looks` - Search for saved Looks
- `run_look` - Run a saved Look
- `make_look` - Create a new Look

**Your Custom Tools (3 tools):**
- `hello_world` - Simple greeting tool
- `echo_message` - Echo message with metadata
- `enhance_looker_data` - Enhance Looker data with analytics

### Test Your Tools

You can test the tools directly from the UI or using curl:

```bash
# Test hello_world
curl "http://localhost:8080/hello?name=Alice"

# Test echo_message
curl -X POST http://localhost:8080/echo \
  -H "Content-Type: application/json" \
  -d '{"message": "Hello MCP!", "include_timestamp": true}'

# Test enhance_looker_data
curl -X POST http://localhost:8080/enhance \
  -H "Content-Type: application/json" \
  -d '{
    "data": {"sales": 1000, "region": "US"},
    "enhancement_type": "forecast"
  }'

# Test health check
curl http://localhost:8080/health
```

---

## Customization Examples

### Example 1: Add a Database Query Tool

```yaml
# In custom_tools.yaml
sources:
  my-database:
    kind: postgres
    connection_string: ${DATABASE_URL}

tools:
  query_database:
    kind: sql
    source: my-database
    description: |
      Execute SQL query against database
    input_schema:
      type: object
      properties:
        query:
          type: string
          description: SQL query to execute
      required:
        - query
```

### Example 2: Add an External API Tool

```yaml
# In custom_tools.yaml
sources:
  weather-api:
    kind: http
    base_url: https://api.weather.com
    timeout: 10s

tools:
  get_weather:
    kind: http-get
    source: weather-api
    endpoint: /forecast
    description: |
      Get weather forecast
    input_schema:
      type: object
      properties:
        city:
          type: string
          description: City name
      required:
        - city
```

### Example 3: Add ML Model Endpoint

```python
# In custom_service.py

@app.route('/predict', methods=['POST'])
def predict():
    """ML model prediction endpoint"""
    try:
        data = request.json
        input_data = data.get('input_data', [])
        
        # Load your ML model
        # model = load_model('my_model.pkl')
        # predictions = model.predict(input_data)
        
        # Mock prediction for example
        predictions = [x * 1.2 for x in input_data]
        
        return jsonify({
            "predictions": predictions,
            "model_version": "1.0.0",
            "status": "success"
        }), 200
        
    except Exception as e:
        logger.error(f"Error in predict: {str(e)}")
        return jsonify({"error": str(e)}), 500
```

Then add to YAML:

```yaml
tools:
  ml_predict:
    kind: http-post
    source: custom-service
    endpoint: /predict
    description: |
      Make ML predictions on input data
    input_schema:
      type: object
      properties:
        input_data:
          type: array
          items:
            type: number
          description: Input data for prediction
      required:
        - input_data
```

---

## Troubleshooting

### Issue: Tools Not Appearing in UI

**Solution:**
1. Check YAML syntax (indentation must be correct)
2. Verify custom service is running: `curl http://localhost:8080/health`
3. Check toolbox logs for errors
4. Restart toolbox after YAML changes

### Issue: "Connection Refused" Error

**Solution:**
1. Ensure custom service is running on port 8080
2. Check if port is already in use: `lsof -i :8080`
3. Verify `base_url` in YAML matches service URL
4. Check firewall settings

### Issue: Looker Tools Not Working

**Solution:**
1. Verify environment variables are set: `echo $LOOKER_BASE_URL`
2. Test Looker credentials manually
3. Check `verify_ssl` setting if using self-signed cert
4. Increase timeout if queries are slow

### Issue: Custom Tool Returns Error

**Solution:**
1. Check Python service logs for errors
2. Verify request format matches `input_schema`
3. Test endpoint directly with curl
4. Check for missing required parameters

### Common Errors

**YAML Parse Error:**
```
Error: Invalid YAML syntax
```
Fix: Check indentation (use spaces, not tabs)

**Port Already in Use:**
```
Error: Address already in use
```
Fix: Kill existing process or use different port

**Missing Environment Variable:**
```
Error: LOOKER_BASE_URL not set
```
Fix: Run `source setup_env.sh`

---

## Common Use Cases

### Use Case 1: Looker + ML Predictions

**Workflow:**
1. Query sales data from Looker using `query` tool
2. Pass results to `enhance_looker_data` with type='forecast'
3. Get predictions and insights combined with historical data

**Example Conversation:**
```
User: "Show me sales forecast for Q4"
AI: Uses query tool → Gets historical sales
    Uses enhance_looker_data → Gets forecast
    Returns: Combined historical + predicted data
```

### Use Case 2: Multi-Source Data Enrichment

**Workflow:**
1. Query customer data from Looker
2. Enrich with external API data (demographics, social, etc.)
3. Add custom business rules
4. Return comprehensive customer profile

**Implementation:**
```python
@app.route('/enrich-customer', methods=['POST'])
def enrich_customer():
    looker_data = request.json.get('looker_data')
    
    # Fetch from external API
    demographics = fetch_demographics(looker_data['customer_id'])
    
    # Apply business rules
    segment = classify_customer(looker_data, demographics)
    
    return jsonify({
        "looker_data": looker_data,
        "demographics": demographics,
        "segment": segment
    })
```

### Use Case 3: Automated Insights Generation

**Workflow:**
1. Schedule regular Looker queries
2. Analyze results for anomalies
3. Generate automated insights
4. Send alerts for significant findings

---

## Advanced Topics

### Authentication

To add authentication to your custom service:

```python
from functools import wraps
from flask import request

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('X-API-Key')
        if api_key != os.environ.get('API_KEY'):
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/secure-endpoint', methods=['POST'])
@require_api_key
def secure_endpoint():
    # Your secure logic here
    pass
```

### Async Processing

For long-running tasks:

```python
from threading import Thread

def async_task(task_id, data):
    # Long running task
    result = process_data(data)
    # Store result with task_id
    
@app.route('/async-process', methods=['POST'])
def async_process():
    task_id = generate_task_id()
    data = request.json
    
    thread = Thread(target=async_task, args=(task_id, data))
    thread.start()
    
    return jsonify({
        "task_id": task_id,
        "status": "processing"
    })

@app.route('/task-status/<task_id>', methods=['GET'])
def task_status(task_id):
    # Return task status
    pass
```

### Caching

Add caching for frequently accessed data:

```python
from functools import lru_cache
import time

@lru_cache(maxsize=100)
def cached_computation(input_data):
    # Expensive computation
    return result

@app.route('/cached-endpoint', methods=['POST'])
def cached_endpoint():
    data = request.json
    result = cached_computation(tuple(data['input']))
    return jsonify(result)
```

---

## Production Considerations

### 1. Security

- ✅ Use HTTPS in production
- ✅ Implement proper authentication
- ✅ Validate all input data
- ✅ Use environment variables for secrets
- ✅ Enable CORS only for trusted domains

### 2. Performance

- ✅ Add connection pooling for databases
- ✅ Implement caching where appropriate
- ✅ Use async processing for long tasks
- ✅ Set appropriate timeouts
- ✅ Monitor resource usage

### 3. Monitoring

- ✅ Add structured logging
- ✅ Implement health checks
- ✅ Track metrics (requests, latency, errors)
- ✅ Set up alerts for failures
- ✅ Use monitoring tools (Prometheus, Grafana, etc.)

### 4. Deployment

- ✅ Use Docker for containerization
- ✅ Implement CI/CD pipelines
- ✅ Use load balancing for scalability
- ✅ Implement graceful shutdowns
- ✅ Have rollback procedures

---

## Docker Deployment (Optional)

### Dockerfile for Custom Service

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY custom_service.py .
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

EXPOSE 8080

CMD ["python", "custom_service.py"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  custom-service:
    build: .
    ports:
      - "8080:8080"
    environment:
      - LOG_LEVEL=INFO
    restart: unless-stopped

  toolbox:
    image: gcr.io/google/genai-toolbox:latest
    ports:
      - "5000:5000"
    environment:
      - LOOKER_BASE_URL=${LOOKER_BASE_URL}
      - LOOKER_CLIENT_ID=${LOOKER_CLIENT_ID}
      - LOOKER_CLIENT_SECRET=${LOOKER_CLIENT_SECRET}
    command: --prebuilt looker --config /config/custom_tools.yaml --port 5000 --ui
    volumes:
      - ./custom_tools.yaml:/config/custom_tools.yaml
    depends_on:
      - custom-service
```

---

## Summary

### What We've Built

✅ **Single MCP Server** with both prebuilt and custom tools  
✅ **YAML Configuration** for easy tool definition  
✅ **Python Service** for custom logic implementation  
✅ **Complete Examples** for common use cases  

### Key Commands

```bash
# Start custom service
python3 custom_service.py

# Start MCP Toolbox
./toolbox --prebuilt looker --config custom_tools.yaml --port 5000 --ui

# Access UI
http://localhost:5000
```

### Files Created

1. `custom_tools.yaml` - Tool configuration
2. `custom_service.py` - Python service implementation
3. `setup_env.sh` - Environment variables

### Next Steps

1. Copy the YAML and Python code from this document
2. Customize the tools for your use case
3. Add your ML models, analytics, or API integrations
4. Test using the UI or curl commands
5. Deploy to production when ready

---

## Resources

- **MCP Toolbox**: https://github.com/googleapis/genai-toolbox
- **Looker API**: https://cloud.google.com/looker/docs/api
- **MCP Protocol**: https://modelcontextprotocol.io
- **Flask Documentation**: https://flask.palletsprojects.com/

---

## Questions?

If you encounter issues:

1. Check the Troubleshooting section
2. Verify all prerequisites are installed
3. Check logs for error messages
4. Test each component individually
5. Review the examples in this document

---

**That's it!** You now have a complete guide to add custom tools to MCP Toolbox alongside prebuilt Looker tools. Everything you need is in this single document - just copy the code sections and customize for your needs!

---

*Created: January 2025*  
*Version: 1.0*
