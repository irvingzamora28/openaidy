# openaidy_agents

A modular Python agent framework for analyzing Chrome Web Store reviews using the OpenAI Agents SDK and browser automation (Playwright MCP).

## Overview
This package provides a set of composable agents and an orchestrator to extract, analyze, and process reviews from Chrome Web Store extension pages. Each agent is responsible for a specific step in the pipeline, enabling flexible orchestration and easy extension.

## Features
- **Structure Discovery Agent**: Extracts references (refs) to all reviews and their components (container, heading, text, developer reply) from the accessibility tree or DOM snapshot.
- **Interaction Discovery Agent**: Identifies all interactive elements that affect which reviews are shown, including load more buttons, sorting controls, filters, pagination, tabs, dropdowns, etc.
- **Orchestrator**: Coordinates the workflow, running each agent in sequence and passing outputs between them.
- **Shared LLM Environment**: Centralized setup for OpenAI API credentials and model configuration.

## Directory Structure
```
openaidy_agents/
├── llm_env.py                  # Shared LLM/OpenAI environment setup
├── structure_discovery_agent.py
├── interaction_discovery_agent.py
├── review_analysis_orchestrator.py
├── orchestrator_structure_example.py
├── playwright_mcp_server_example.py
```

## Setup
1. **Install dependencies** (see `requirements.txt`):
    - `openai`
    - `python-dotenv`
    - `openai-agents` (OpenAI Agents SDK)
    - `openai-agents[litellm]` (OpenAI Agents SDK with non-OpenAI models support)
    - `playwright` and `@playwright/mcp` (Node.js, for browser automation)
2. **Environment variables**: Create a `.env` file with:
    ```
    LLM_API_URL=...
    LLM_API_KEY=...
    LLM_MODEL=...
    ```
3. **Node.js** and `npx` are required for MCP browser automation.

## Usage
### Run the Orchestrator Example
```
python orchestrator_structure_example.py
```
This will:
- Run the orchestrator pipeline on a hardcoded Chrome Web Store reviews page URL
- Print the extracted review structure and discovered interactions

### Example Output
```
Orchestrator result:
{
  'success': True,
  'structure': ...json with review refs...
  'interactions': ...json with interactive element refs...
}
```

## Extending the Pipeline
- Add new agents (e.g., review extraction, sentiment analysis) as new modules.
- Update the orchestrator to call new agents and pass the necessary data.

## Code Style and Structure
- Agents are stateless modules with an async `run()` function.
- All LLM config and client setup is centralized in `llm_env.py`.
- Prompts are carefully crafted for each agent's task and can be easily modified.

## References
- [OpenAI Agents SDK Documentation](https://openai.github.io/openai-agents-python/agents/)
- [Playwright MCP](https://www.npmjs.com/package/@playwright/mcp)

---

*This project is under active development.*
