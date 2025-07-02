# Long-Term Agent Memory Benchmark

A benchmark built using the **Local Agent Orchestrator** framework to evaluate long-term memory in language model agents through algorithmic tasks.

This project implements a **shortest-path-finding agent** navigating a **weighted, partially observable graph** using the **ReAct (Reasoning and Acting)** paradigm—alternating between reasoning steps and tool use to achieve optimal performance.

---

## Project Structure

```
llm-memory-project/
├── chat_templates/             # Templates for chat formatting
├── configs/                    # YAML configuration files
├── external_tools/             # Custom tools and tool schemas
│   ├── __init__.py
│   └── tool_schemas.yaml
├── graphs/                     # Graph generation logic
│   └── recursive_graph.py
├── llm/
│   └── run.py                  # Main agent execution script
├── templates/                  # Jinja2 templates for prompts
├── run_server.sh               # Script to start the LLM server
└── README.md                   # Project documentation
```

---

## Key Components

### Configs

Task-specific and model configuration files under `configs/`.

### External Tools

YAML-defined tool schemas and corresponding Python implementations. These are invoked by the agent during execution.

### LLM Code

* `run.py`: Core script that orchestrates agent behavior.

### Templates

Prompt templates using Jinja2 for:

* System instructions
* User inputs
* Agent responses

---

## Setup

### 1. Install Dependencies

```bash
conda create -n local-agent python=3.12
conda activate local-agent

pip install uv
uv pip install vllm
pip install datasets openai
```

### 2. Install Local Agent Orchestrator

```bash
cd /path/to/local-agent-orchestrator
pip install --editable .
```

### 3. Start LLM Server

```bash
./run_server.sh
```

Make sure the server is configured with an OpenAI-compatible interface.

---

## Usage

Run the agent with a configuration file:

```bash
python -m llm.run --config_file configs/shortest_path.yaml --log-level INFO
```

You can customize the graph in the config file:

```yaml
graph_params:
  base_nodes: 6              # Number of base nodes
  max_edges: 3               # Max outgoing edges per node
  recursion_depth: 0         # Recursion depth for nested graphs
  weight_choices: [1.0, 2.0] # Edge weights
  seed: 42                   # Random seed
```

---
