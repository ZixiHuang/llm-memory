# Long-term Agent Memory Benchmark

A project-specific implementation using the Local Agent Orchestrator framework.

## Project Structure

```
llm-memory-project/
├── configs/                 # Configuration files
├── external_tools/          # Custom tools and schemas
│   ├── __init__.py
│   └── tool_schemas.yaml
├── src/                     # Source code
│   ├── handlers/            # Custom game handlers
│   │   └── custom_game.py
│   └── main.py              # Main execution script
├── templates/               # Jinja2 templates for prompts
├── requirements.txt         # Dependencies
└── README.md               # This file
```

## Overview

This project demonstrates how to use the Local Agent Orchestrator framework to build custom agentic applications. The structure is organized to separate concerns and make the codebase maintainable and extensible.

## Key Components

### Configs
Configuration files for different tasks and environments.

### External Tools
Custom tools that the agent can use, defined in YAML schemas and implemented in Python.

### Source Code
- **handlers/**: Custom game classes that extend the framework's AbstractGame
- **main.py**: Main execution script that orchestrates the agent workflow

### Templates
Jinja2 templates for system prompts, user prompts, and response guidance.

## Prerequisites

1. Install project dependencies:
```bash
conda create -n local-agent python=3.12
conda activate local-agent
pip install uv
uv pip install vllm
pip install datasets openai
```

2. Install the Local Agent Orchestrator framework:
```bash
cd /path/to/local-agent-orchestrator
pip install --editable .
```

3. Set up your OpenAI-compatible language model server

## Usage

```bash
# Run the main script
python -m src.main --config_file configs/shortest_path.yaml --log-level INFO
```

## Customization

1. **Add new tools**: Define them in `external_tools/tool_schemas.yaml` and implement in `external_tools/__init__.py`
2. **Create custom handlers**: Add new game classes in `src/handlers/`
3. **Modify templates**: Edit Jinja2 templates in the `templates/` directory
4. **Update configuration**: Modify YAML files in `configs/`