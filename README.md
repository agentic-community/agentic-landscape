# Agentic AI Landscape

An interactive landscape of open source and commercial projects in the agentic AI ecosystem, built with [CNCF landscape2](https://github.com/cncf/landscape2).

**Live site:** [landscape.agentic-community.com](https://landscape.agentic-community.com)

## Overview

### Agentic

The core agentic ecosystem: frameworks, protocols, tooling, and infrastructure for building and running AI agents.

- **Agent Protocols** -- Standards for agent interoperability
- **Frameworks** -- SDKs and libraries for building agents
- **Workflow Orchestration** -- Durable execution engines for multi-step agent workflows
- **Coding Agents** -- Autonomous software engineering agents
- **Voice Agents** -- Voice and multimodal agent frameworks
- **Tool Integration** -- Connecting agents to external tools and browsers
- **Search & Web Access** -- Web crawling and search for agents
- **Structured Output** -- Constraining LLM outputs to schemas
- **RAG** -- Retrieval-augmented generation pipelines
- **Memory** -- Persistent memory for agents
- **Evaluations** -- Testing and benchmarking agents
- **Guardrails** -- Safety and output validation
- **Observability** -- Tracing, logging, and monitoring
- **Code Sandbox** -- Isolated execution environments
- **IAM** -- Identity and access management
- **LLM Gateway** -- Routing and load balancing for LLM APIs
- **Agentic Gateways** -- Agent-specific gateway infrastructure

### Infrastructure

Data storage and retrieval infrastructure that agents depend on.

- **Vector DBs** -- Vector similarity search
- **Knowledge Graphs** -- Graph databases for structured knowledge

### LLMs

Model serving and training infrastructure.

- **Serving** -- LLM inference engines
- **Fine-tuning** -- Model training tools

## Licensing tags

Every project is tagged with one of:

| Tag | Meaning |
|---|---|
| **Open Source** | Fully open source with a permissive or copyleft license |
| **Open Core** | Open source core with a commercial cloud or enterprise offering |
| **Commercial** | Proprietary SaaS product |

## Contributing

### Adding a project

Edit `agentic-landscape/data.yml` and add an entry under the appropriate subcategory. Each item needs:

```yaml
- name: Project Name
  homepage_url: https://example.com/
  repo_url: https://github.com/org/repo
  extra:
    summary_tags: Open Source
  logo: projectname.png
```

Place the project logo (SVG preferred, PNG accepted) in `agentic-landscape/logos/`.

### Sort order

Items within each subcategory must be in **alphabetical order** by name. A CI check enforces this. To fix sort order locally:

```
python .github/scripts/sort-data.py
```

### Building locally

landscape2 pulls GitHub repo stats (stars, contributors, license, etc.) during the build. Set the `GITHUB_TOKENS` environment variable to one or more [personal access tokens](https://github.com/settings/tokens) to avoid rate limiting:

```
export GITHUB_TOKENS=ghp_yourtoken
```

Multiple tokens can be comma-separated to increase throughput.

Then build and serve:

```
# Install landscape2 (https://github.com/cncf/landscape2/releases)
landscape2 build \
  --data-file agentic-landscape/data.yml \
  --settings-file agentic-landscape/settings.yml \
  --guide-file agentic-landscape/guide.yml \
  --logos-path agentic-landscape/logos \
  --output-dir build

# Serve locally
landscape2 serve --landscape-dir build
```

## Trademark notice

All logos in `agentic-landscape/logos/` are property of their respective owners and are used here solely for identification purposes within this landscape. Their inclusion does not imply endorsement by or affiliation with the Agentic Community project. If you are a trademark owner and would like your logo removed or updated, please open an issue.

## License

This project is licensed under the Apache License 2.0. See [LICENSE](LICENSE) for details.
