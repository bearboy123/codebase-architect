# Demo Setup & Quick Start

## Quick Start (5 minutes)

### Prerequisites
- Python 3.10+
- Node.js 16+
- Git
- Azure OpenAI API key

### 1. Environment Setup

```bash
# Clone the repository
cd agent-league-hackathon

# Create .env file
cp .env.example .env

# Fill in your Azure OpenAI credentials in .env:
# - AZURE_OPENAI_ENDPOINT
# - AZURE_OPENAI_KEY
# - AZURE_OPENAI_DEPLOYMENT_NAME
```

### 2. Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/Scripts/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server
python main.py
# Server will start on http://localhost:8000
```

### 3. Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
# Frontend will start on http://localhost:5173
```

### 4. Run Demo Analysis

**Option A: Using the Web UI**
1. Open http://localhost:5173 in your browser
2. Enter a GitHub repository URL (e.g., `https://github.com/torvalds/linux`)
3. Click "Analyze"
4. Wait for completion and explore results

**Option B: Using API Directly**

```bash
# Start analysis
curl -X POST http://localhost:8000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"repo_url": "https://github.com/your-repo/url"}'

# Check status
curl http://localhost:8000/api/analysis/{job_id}/status

# Get results
curl http://localhost:8000/api/analysis/{job_id}
```

## Kubernetes (k3s) Deployment

### Prerequisites
- k3s installed on WSL2 with Docker Desktop
- `kubectl` configured and pointing to your k3s cluster

### Setup Steps

```bash
# 1. Create namespace
kubectl apply -f k8s/namespace.yaml

# 2. Create ConfigMap for application config
kubectl apply -f k8s/configmap.yaml

# 3. Create Secret for Azure OpenAI credentials
# First, edit k8s/secret.yaml with your credentials
kubectl apply -f k8s/secret.yaml

# 4. Create PVC for persistent storage (optional)
kubectl apply -f k8s/pvc.yaml

# 5. Deploy backend
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/backend-service.yaml

# 6. Deploy frontend
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

# Or deploy everything at once with Kustomize (recommended):
kubectl apply -k k8s/
```

### Verify Deployment

```bash
# Check pods are running
kubectl get pods -n codebase-architect

# View logs
kubectl logs -f deployment/codebase-architect-backend -n codebase-architect
kubectl logs -f deployment/codebase-architect-frontend -n codebase-architect

# Check services
kubectl get svc -n codebase-architect
```

### Access the Application

```bash
# Option 1: Port Forwarding
kubectl port-forward svc/backend-service 8000:8000 -n codebase-architect &
kubectl port-forward svc/frontend-service 5173:5173 -n codebase-architect &

# Open http://localhost:5173

# Option 2: Using Ingress (if configured)
# Check k8s/ingress.yaml for hostname configuration
# Add to /etc/hosts: codebase-architect.local
# Then open http://codebase-architect.local
```

### Autoscaling (HPA)

```bash
# Deploy Horizontal Pod Autoscaler
kubectl apply -f k8s/hpa.yaml

# Monitor scaling
kubectl get hpa -n codebase-architect -w
```

### Cleanup

```bash
# Remove all resources
kubectl delete namespace codebase-architect
```

## Example Repositories to Analyze

- Small: `https://github.com/pallets/flask` (Python web framework)
- Medium: `https://github.com/nodejs/nodejs-en` (Node.js docs)
- Large: `https://github.com/torvalds/linux` (Linux kernel)

## Demo Features

### 1. Architecture Agent
- Maps service/module structure
- Identifies service boundaries
- Visualizes dependency graph
- Detects circular dependencies

### 2. Security Agent
- Finds hardcoded secrets/credentials
- Identifies auth/authorization issues
- Detects common vulnerabilities
- Provides remediation advice

### 3. Performance Agent
- Identifies inefficient code patterns
- Detects potential scalability issues
- Suggests optimizations
- Analyzes algorithm complexity

### 4. Documentation Agent
- Generates project summary
- Creates onboarding guide
- Extracts technical overview
- Documents key components

## Troubleshooting

### Backend Connection Error
```bash
# Check if backend is running
curl http://localhost:8000/health

# Check logs
tail -f backend.log
```

### Analysis Timeout
- Try with a smaller repository
- Check Azure OpenAI quota/rate limits
- Increase timeout in settings

### Frontend Not Loading
```bash
# Verify Node version
node --version  # Should be 16+

# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## Production Considerations

1. **Database**: Replace in-memory job storage with PostgreSQL/MongoDB
2. **Message Queue**: Use Redis/RabbitMQ for background tasks
3. **Caching**: Cache analysis results to reduce API calls
4. **Authentication**: Add user authentication and API keys
5. **Rate Limiting**: Implement rate limiting per user/IP
6. **Monitoring**: Add structured logging and metrics collection
7. **Security**: Run in private VPC, use managed identities for Azure

## Performance Metrics

Typical analysis times (mid-sized repo, ~10k files):
- Code indexing: 10-20s
- Architecture analysis: 20-30s
- Security analysis: 15-25s
- Performance analysis: 20-30s
- Documentation generation: 10-15s
- **Total**: ~2-3 minutes

## Next Steps

1. **Expand agents** - Add more specialized agents (testing, scalability, etc.)
2. **Improve findings** - Add domain-specific analysis rules
3. **Interactive UI** - Add filtering, search, and drill-down capabilities
4. **Export reports** - Support PDF, HTML, Markdown export
5. **Collaboration** - Add team sharing and annotation features
6. **Continuous monitoring** - Run periodic analyses and track trends

## Support

For issues or questions:
1. Check logs: `docker logs <container>`
2. Review error message in API response
3. Check Azure OpenAI quota and keys
4. Refer to agent implementation files

---

**Happy analyzing!** 🎉
