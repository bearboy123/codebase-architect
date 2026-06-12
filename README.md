# Codebase Architect Agent

A multi-agent platform that analyzes codebases through specialized AI agents. Instead of relying on a single AI assistant, this system orchestrates a team of specialized agents that collaborate to analyze a codebase from multiple perspectives.

## 🎯 MVP Features

- **Architecture Agent**: Maps services, modules, dependencies, and data flows
- **Security Agent**: Reviews code for vulnerabilities and risky patterns
- **Performance Agent**: Detects inefficient code paths and scalability concerns
- **Documentation Agent**: Generates developer-friendly summaries and onboarding docs

## 🏗️ Tech Stack

**Backend:**
- Python 3.10+
- Semantic Kernel (multi-agent orchestration)
- FastAPI (REST API)
- AST/tree-sitter (code analysis)
- Azure OpenAI (LLM)

**Frontend:**
- React 18 + TypeScript
- TailwindCSS (styling)
- Axios (API client)

## 📁 Project Structure

```
codebase-architect-agent/
├── backend/              # Python backend with agents
├── frontend/             # React TypeScript dashboard
├── docker-compose.yml    # Development environment
├── .env.example          # Configuration template
└── README.md
```

## 🚀 Getting Started (Coming Soon)

Instructions for setup, running agents, and accessing the dashboard.

## 📋 Development Phases

- [x] Phase 1: Foundation Setup
- [ ] Phase 2: Backend Development
- [ ] Phase 3: Frontend Development
- [ ] Phase 4: Integration & Polish

## 📝 License

MIT
