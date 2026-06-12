# Codebase Architect Agent - Complete Setup Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.10+, Node.js 18+, npm (for local development)
- OR: Kubernetes cluster 1.20+ for production
- Git
- Azure OpenAI API credentials

### Option 1: Local Development Setup

```bash
# Clone the repository
git clone https://github.com/bearboy123/codebase-architect-agent.git
cd codebase-architect-agent

# Copy environment file
cp .env.example .env

# Edit .env with your Azure OpenAI credentials
nano .env
```

### Option 2: Kubernetes Deployment (Recommended for Production)

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env
# Edit .env with your credentials

# Run the server
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at: http://localhost:3000
```

---

## ☸️ Kubernetes Deployment

For production deployments, use Kubernetes. This provides:
- High availability with multiple replicas
- Auto-scaling based on CPU/memory
- Load balancing and ingress routing
- Zero-downtime updates
- Easy horizontal scaling

### Quick Start with Kubernetes

**Prerequisites:**
- Kubernetes cluster (AKS, GKE, EKS, or local minikube)
- kubectl configured to access your cluster
- Docker images pushed to a registry

```bash
# 1. Build and push images
docker build -f Dockerfile.backend -t your-registry.azurecr.io/codebase-architect-backend:latest .
docker push your-registry.azurecr.io/codebase-architect-backend:latest

docker build -f frontend/Dockerfile -t your-registry.azurecr.io/codebase-architect-frontend:latest .
docker push your-registry.azurecr.io/codebase-architect-frontend:latest

# 2. Update k8s manifests with your registry and domain
# Edit k8s/backend-deployment.yaml, k8s/frontend-deployment.yaml, and k8s/ingress.yaml

# 3. Deploy to Kubernetes
kubectl apply -f k8s/

# 4. Wait for rollout
kubectl rollout status deployment/codebase-architect-backend -n codebase-architect
kubectl rollout status deployment/codebase-architect-frontend -n codebase-architect

# 5. Get the ingress IP
kubectl get ingress -n codebase-architect
```

**See [k8s/README.md](k8s/README.md) for detailed Kubernetes deployment guide.**

### Using Kustomize

For environment-specific deployments:

```bash
# Deploy with Kustomize
kubectl apply -k k8s/

# Preview changes
kubectl kustomize k8s/

# Deploy to specific namespace
kubectl apply -k k8s/ -n production
```

---

#### Backend Setup
```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment file
cp ../.env.example .env
# Edit .env with your credentials

# Run the server
uvicorn api.app:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend Setup
```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at: http://localhost:3000
```

---

## 🏗️ Architecture Overview

### Multi-Agent System
The platform uses a team of specialized AI agents that analyze different aspects of your codebase:

```
┌─────────────────────────────────────────────────────┐
│         User Interface (React + TypeScript)           │
└──────────────────┬──────────────────────────────────┘
                   │
         HTTP/REST API (FastAPI)
                   │
┌──────────────────▼──────────────────────────────────┐
│         Agent Orchestrator                            │
│  ┌─────────┬─────────────┬──────────────────────┐   │
│  │Architecture  │  Security  │   Performance     │   │
│  │   Agent      │   Agent    │    Agent          │   │
│  └─────────┴─────────────┴──────────────────────┘   │
│                                                      │
│  Shared: CodeIndexer, Analyzers, Memory             │
└──────────────────────────────────────────────────────┘
```

### Component Breakdown

#### Backend (`backend/`)
- **`analyzers/`** - Code indexing and AST parsing
- **`agents/`** - Specialized analysis agents
- **`orchestrator/`** - Agent coordination and result consolidation
- **`api/`** - FastAPI application and routes
- **`config/`** - Settings and Semantic Kernel configuration

#### Frontend (`frontend/`)
- **`src/components/`** - Reusable UI components
- **`src/pages/`** - Page components (Upload, Dashboard)
- **`src/hooks/`** - Custom React hooks
- **`src/services/`** - API client service

---

## 📋 API Endpoints

### Analysis
- **POST** `/api/analyze` - Start analysis with Git URL
- **POST** `/api/analyze/upload` - Upload and analyze repository
- **GET** `/api/analysis/{job_id}` - Get analysis results
- **GET** `/api/analysis/{job_id}/status` - Get job status

### System
- **GET** `/health` - Health check
- **GET** `/api/metrics` - System metrics and job statistics

### Example: Start Analysis
```bash
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/username/repo.git"}'

# Response:
{
  "job_id": "abc-123-def",
  "status": "pending"
}
```

### Example: Check Status
```bash
curl http://localhost:8000/api/analysis/abc-123-def/status

# Response:
{
  "job_id": "abc-123-def",
  "status": "running",
  "progress": 45,
  "message": "Analysis in progress... 45%"
}
```

---

## 🤖 Agents Explained

### Architecture Agent
**What it does:**
- Maps module and service structure
- Identifies architectural patterns (MVC, microservices, API-first)
- Detects circular dependencies
- Analyzes coupling and cohesion

**Findings Include:**
- Module structure assessment
- Dependency analysis
- Service boundary identification
- Architectural anti-patterns

### Security Agent
**What it does:**
- Scans for hardcoded secrets (API keys, passwords, tokens)
- Detects unsafe coding patterns
- Identifies risky library usage
- Checks authentication/authorization patterns

**Findings Include:**
- Hardcoded credentials
- SQL injection vulnerabilities
- Command injection risks
- Unsafe deserialization
- Unencrypted communication

### Performance Agent
**What it does:**
- Detects performance anti-patterns (N+1, nested loops)
- Identifies scalability bottlenecks
- Finds inefficient algorithms
- Suggests optimization opportunities

**Findings Include:**
- Large files and modules
- Nested loop patterns
- N+1 query patterns
- Synchronous blocking operations
- Caching opportunities

---

## 📊 Results & Health Score

### Health Score (0-100)
The platform calculates an overall health score based on findings:
- **80-100**: Excellent - Well-structured, secure codebase
- **60-79**: Good - Some issues to address
- **40-59**: Fair - Significant improvements needed
- **0-39**: Poor - Critical issues present

### Findings by Severity
- **Critical** (🔴) - Security risks, major issues
- **High** (🟠) - Important problems to fix
- **Medium** (🟡) - Should be addressed
- **Low** (🔵) - Nice-to-haves

---

## 🔧 Environment Variables

```env
# Azure OpenAI Configuration
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_MODEL_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Server Configuration
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
DEBUG=true

# Frontend
FRONTEND_URL=http://localhost:3000

# Analysis Settings
MAX_ANALYSIS_TIME_SECONDS=300
MAX_FILE_SIZE_MB=50
ANALYZE_HIDDEN_FILES=false
```

---

## 🧪 Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### Running Tests
```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test
```

---

## 📦 Dependencies

### Backend
- **fastapi** - Web framework
- **semantic-kernel** - Multi-agent orchestration
- **gitpython** - Git operations
- **tree-sitter** - Code parsing
- **azure-openai** - LLM integration
- **uvicorn** - ASGI server

### Frontend
- **react** - UI framework
- **typescript** - Type safety
- **axios** - HTTP client
- **tailwindcss** - Styling
- **vite** - Build tool

### Infrastructure
- **Kubernetes** 1.20+ - Container orchestration
- **kubectl** - Kubernetes CLI
- **Docker** - Container images (optional for local dev)

---

## 🐛 Troubleshooting

### Backend won't start
1. Check Azure OpenAI credentials in .env
2. Ensure port 8000 is available
3. Verify Python 3.10+ is installed
4. Check logs: `docker logs codebase-architect-backend`

### Frontend won't load
1. Check if backend is running: `curl http://localhost:8000/health`
2. Ensure port 3000 is available
3. Clear npm cache: `npm cache clean --force`
4. Rebuild: `npm install && npm run build`

### Analysis fails
1. Check repository accessibility (for Git URLs)
2. Verify Azure OpenAI credentials
3. Check MAX_ANALYSIS_TIME_SECONDS setting
4. Review backend logs for detailed error

### CORS errors
The backend has CORS enabled for all origins by default. If you see CORS errors:
1. Ensure backend is running on correct port
2. Check FRONTEND_URL in environment

---

## 📚 Examples

### Analyze a Public Repository
1. Go to http://localhost:3000
2. Select "Git Repository URL" tab
3. Enter: `https://github.com/openai/openai-python`
4. Click "Analyze Repository"
5. Wait for analysis to complete (~2-5 minutes)
6. View detailed findings and recommendations

### Analyze Your Own Repository
1. Zip your repository
2. Go to http://localhost:3000
3. Select "Upload Repository" tab
4. Choose your ZIP file
5. Click "Upload & Analyze"
6. Results will appear on completion

---

## 🚀 Production Deployment

### Docker Hub
```bash
docker build -f Dockerfile.backend -t youruser/codebase-architect:latest .
docker push youruser/codebase-architect:latest
```

### Azure Container Instances
```bash
az container create \
  --resource-group myGroup \
  --name codebase-architect \
  --image youruser/codebase-architect:latest \
  --environment-variables AZURE_OPENAI_ENDPOINT=... AZURE_OPENAI_API_KEY=...
```

---

## 📝 Configuration Files

- **`.env`** - Environment variables (create from `.env.example`)
- **`backend/requirements.txt`** - Python dependencies
- **`frontend/package.json`** - Node.js dependencies
- **`docker-compose.yml`** - Docker services configuration
- **`Dockerfile.backend`** - Backend Docker image
- **`frontend/Dockerfile`** - Frontend Docker image

---

## 📄 License

MIT License - See LICENSE file for details

---

## 🤝 Contributing

Contributions are welcome! Please ensure:
1. Code follows project style
2. Tests pass
3. Documentation is updated
4. Commit messages are clear

---

## 📞 Support

For issues, questions, or suggestions:
1. Check the Troubleshooting section above
2. Review backend logs: `docker logs codebase-architect-backend`
3. Check frontend console for errors (F12 in browser)
4. Review API responses for detailed error messages

---

## 🎯 Roadmap

### Completed (MVP)
- ✅ Architecture Agent
- ✅ Security Agent
- ✅ Performance Agent
- ✅ React Dashboard
- ✅ REST API
- ✅ Docker Support

### Planned (Future)
- 📋 Documentation Agent
- 📊 Advanced visualizations (dependency graphs)
- 🔄 Continuous monitoring
- 📈 Historical analysis tracking
- 🧪 Unit test recommendations
- 🎨 Custom report generation
- 🔌 GitHub/GitLab integrations
- ⚙️ Configuration analysis

---

**Happy coding! 🎉**
