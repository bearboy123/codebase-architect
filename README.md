# 🏗️ Codebase Architect Agent

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)
![TypeScript](https://img.shields.io/badge/typescript-5.3+-blue.svg)
![React 18](https://img.shields.io/badge/react-18.2+-61dafb.svg)

A **multi-agent AI platform** that analyzes codebases through specialized agents. Instead of relying on a single AI assistant, this system orchestrates a team of autonomous agents that collaborate to analyze code from multiple perspectives and produce actionable insights. This was developed as a part of Microsoft Agents League Hackathon 2026 #AgentsLeague .

**Transform weeks of manual code review into minutes of AI-powered analysis.**

---

## 🤖 Agent Team

- **🏗️ Architecture Agent** - Maps services, modules, dependencies, and architectural patterns
- **🔒 Security Agent** - Identifies vulnerabilities, hardcoded secrets, and risky patterns
- **⚡ Performance Agent** - Detects inefficiencies, bottlenecks, and optimization opportunities

---

## ✨ Key Features

✅ **Git Repository Analysis** - Analyze public repositories directly from GitHub/GitLab/Gitea  
✅ **File Upload Support** - Upload ZIP files of your repositories  
✅ **Multi-Agent Orchestration** - Parallel analysis from multiple perspectives  
✅ **Health Score** - Overall code health rating (0-100)  
✅ **Severity Categorization** - Critical, High, Medium, Low findings  
✅ **Smart Recommendations** - Actionable improvement suggestions  
✅ **Real-time Progress** - Live status updates during analysis  
✅ **Beautiful Dashboard** - Intuitive results visualization  
✅ **REST API** - Programmatic access to analysis capabilities  

---

## 🚀 Quick Start

### Prerequisites
- **For Development**: Python 3.10+, Node.js 18+, npm
- **For Production**: Kubernetes cluster (k3s, K3D, etc.) with `kubectl`
- Azure OpenAI API credentials

### 1. Local Development

```bash
# Clone repository
git clone https://github.com/bearboy123/codebase-architect-agent.git
cd codebase-architect-agent

# Configure environment
cp .env.example .env
# Edit .env with your Azure OpenAI credentials

# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py

# Frontend (new terminal)
cd frontend
npm install
npm run dev

# Open http://localhost:5173
```

### 2. Kubernetes Deployment (k3s/K8s)

```bash
# See k8s/README.md for complete deployment guide

# Quick start with k3s:
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
kubectl apply -f k8s/pvc.yaml
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# Or use Kustomize (recommended):
kubectl apply -k k8s/

# Check deployment status:
kubectl get pods -n codebase-architect
kubectl logs -f deployment/codebase-architect-backend -n codebase-architect
```

For detailed setup instructions, see [DEMO_SETUP.md](DEMO_SETUP.md).

---

## 📊 What You Get

### Analysis Report Includes:

1. **Health Score** (0-100)
   - Overall code quality assessment
   - Weighted by finding severity

2. **Findings** (Grouped by Agent)
   - Architecture issues
   - Security vulnerabilities
   - Performance bottlenecks

3. **Recommendations**
   - Prioritized improvements
   - Actionable next steps
   - Best practices

4. **Metrics**
   - File count and lines of code
   - Language breakdown
   - Complexity score
   - Test coverage indicators

---

## 🎯 Use Cases

- **Onboarding New Developers** - Understand large codebases faster
- **Architecture Reviews** - Validate system design and patterns
- **Security Audits** - Find vulnerabilities and security risks
- **Performance Optimization** - Identify bottlenecks and inefficiencies
- **Technical Debt Assessment** - Quantify and prioritize improvements
- **Open Source Evaluation** - Assess code quality before adoption

---

## 🏗️ Architecture

```
Frontend (React + TypeScript)
         ↓ REST API
Backend (FastAPI)
         ↓
Agents (Async Parallel)
    ├─ Architecture Agent
    ├─ Security Agent
    └─ Performance Agent
         ↓
Code Indexer → Semantic Kernel → Azure OpenAI
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed technical documentation.

---

## 📚 Documentation

- **[SETUP.md](SETUP.md)** - Installation and configuration guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Technical architecture and design
- **[API.md](docs/API.md)** - REST API reference

---

## 💡 Examples

### Analyze a Public Repository
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/openai/openai-python"}'
```

### Check Analysis Status
```bash
curl http://localhost:8000/api/analysis/{job_id}/status
```

### Get Results
```bash
curl http://localhost:8000/api/analysis/{job_id}
```

---

## 🔧 Tech Stack

**Backend:**
- Python 3.10+
- FastAPI (Web framework)
- Semantic Kernel (Agent orchestration)
- GitPython (Repository handling)
- Tree-sitter (Code parsing)
- Azure OpenAI (LLM)

**Frontend:**
- React 18
- TypeScript 5.3+
- Tailwind CSS (Styling)
- Axios (HTTP client)
- Vite (Build tool)

**Infrastructure:**
- Kubernetes (k3s, K3D, AKS)
- Azure Container Registry (production)

---

## 🧪 Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📈 Development Status

- [x] **Phase 1** - Foundation setup
- [x] **Phase 2** - Backend core (agents, orchestrator, API)
- [x] **Phase 3** - Frontend (UI, dashboard, components)
- [x] **Phase 4** - Integration & polish

### Planned Enhancements
- [ ] Documentation Agent
- [ ] Advanced visualization (dependency graphs, heat maps)
- [ ] Continuous monitoring
- [ ] Historical analysis tracking
- [ ] GitHub/GitLab integrations
- [ ] Custom report generation

---

## 🐛 Troubleshooting

**Backend won't start?**
- Check Azure OpenAI credentials in `.env`
- Verify Python 3.10+ is installed
- Check if port 8000 is available

**Frontend won't load?**
- Verify backend is running: `curl http://localhost:8000/health`
- Check port 3000 is available
- Clear npm cache: `npm cache clean --force`

**Analysis fails?**
- Check repository accessibility
- Verify Azure OpenAI credentials
- Review backend logs: `kubectl logs -f deployment/codebase-architect-backend -n codebase-architect`

See [SETUP.md](SETUP.md#-troubleshooting) for more help.

---

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Ensure tests pass
4. Submit a pull request

---

## 🎯 Project Goals

This project demonstrates:
- Multi-agent AI system architecture
- Async/concurrent processing patterns
- Semantic Kernel integration with Azure OpenAI
- Full-stack TypeScript/Python development
- Clean code and architecture practices
- Production-ready Kubernetes deployment (k3s)

---

## 📞 Support

- 📖 Check documentation: [DEMO_SETUP.md](DEMO_SETUP.md), [ARCHITECTURE.md](ARCHITECTURE.md), [ERROR_HANDLING.md](ERROR_HANDLING.md)
- 🐛 Review backend logs: `kubectl logs -f deployment/codebase-architect-backend -n codebase-architect`
- 🔍 Check browser console for frontend errors (F12)
- 💬 Open an issue for bugs or feature requests

---

**Made with Semantic Kernel, Azure OpenAI, and TypeScript**

[⬆ Back to top](#-codebase-architect-agent)
