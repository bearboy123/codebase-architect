# Codebase Architect Agent - Architecture Documentation

## System Design Overview

The Codebase Architect Agent is built as a distributed multi-agent system that analyzes source code from multiple specialized perspectives. The architecture follows a modular design pattern with clear separation of concerns.

```
┌────────────────────────────────────────────────────────────┐
│                    Frontend Layer                           │
│            (React 18 + TypeScript + Vite)                  │
│                                                             │
│  Upload Page │ Analysis Dashboard │ Results Components    │
│                 (Job Polling)                              │
└──────────────────────────┬─────────────────────────────────┘
                           │ REST/HTTP
                           │ (Axios)
┌──────────────────────────▼─────────────────────────────────┐
│                 API Layer (FastAPI)                         │
│                                                             │
│  GET /api/analysis/{job_id}                               │
│  POST /api/analyze                                        │
│  POST /api/analyze/upload                                 │
│  Background Job Processing                               │
└──────────────────────────┬─────────────────────────────────┘
                           │
┌──────────────────────────▼─────────────────────────────────┐
│            Application Logic Layer                          │
│                                                             │
│  ┌─ Code Indexer ──────────────────────────────────────┐  │
│  │  • File scanning and metrics                         │  │
│  │  • Dependency extraction                            │  │
│  │  • Language detection                               │  │
│  │  • Module structure analysis                        │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
│  ┌─ Agent Orchestrator ────────────────────────────────┐  │
│  │  • Parallel agent execution                         │  │
│  │  • Result consolidation                            │  │
│  │  • Health score calculation                        │  │
│  │  • Report generation                               │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
    ┌──────▼──────┐ ┌─────▼──────┐ ┌─────▼──────┐
    │ Architecture │ │  Security  │ │Performance │
    │    Agent     │ │   Agent    │ │   Agent    │
    └──────────────┘ └────────────┘ └────────────┘
           │               │               │
           └───────────────┼───────────────┘
                           │
                    ┌──────▼──────┐
                    │ Semantic    │
                    │ Kernel      │
                    │ (Azure      │
                    │ OpenAI)     │
                    └─────────────┘
```

## Component Architecture

### 1. Frontend Layer (`frontend/`)

#### Purpose
Provides an intuitive web interface for repository analysis and result visualization.

#### Key Components

**Pages:**
- `UploadPage.tsx` - Repository input (Git URL or file upload)
- `AnalysisDashboard.tsx` - Results visualization with multi-tab interface

**Components:**
- `Layout.tsx` - Header, Footer, Loading spinners, Messages
- `Results.tsx` - Finding cards, Health score, Severity summaries

**Services:**
- `apiClient.ts` - Axios-based REST client

**Hooks:**
- `useAnalysis.ts` - Job polling, status tracking, style helpers

**Styling:**
- `index.css` - Tailwind directives and custom utilities
- `tailwind.config.js` - Design system configuration

#### Data Flow
```
User Input (Upload/URL)
    ↓
API Call (startAnalysis)
    ↓
Job ID Received
    ↓
useAnalysisJob Hook (Polling every 2s)
    ↓
Status Updates → UI Progress Bar
    ↓
Results Received → Dashboard Tabs
    ↓
FindingsList Components (Filtered by severity)
```

### 2. API Layer (`backend/api/`)

#### Purpose
Handles HTTP requests and orchestrates backend processing.

#### Key Endpoints

**Analysis**
```python
POST /api/analyze
  Input: {repo_url: string}
  Returns: {job_id: string, status: string}

POST /api/analyze/upload
  Input: File (multipart)
  Returns: {job_id: string, status: string}

GET /api/analysis/{job_id}
  Returns: {job_id, status, results}

GET /api/analysis/{job_id}/status
  Returns: {job_id, status, progress, message}
```

**System**
```python
GET /health
  Returns: {status, service, version}

GET /api/metrics
  Returns: {total_jobs, completed, failed, running, pending}
```

#### Job Processing
- **Async Model**: Uses FastAPI BackgroundTasks for long-running analyses
- **Job Storage**: In-memory dict (production: use database)
- **Status Tracking**: pending → running → completed/failed
- **Error Handling**: Graceful degradation with error messages

### 3. Application Layer (`backend/`)

#### Code Indexer (`analyzers/code_indexer.py`)

**Responsibilities:**
- Scan repository structure
- Extract dependencies (Python, JavaScript)
- Compute code metrics
- Build module hierarchy

**Key Methods:**
```python
index() → CodeMetrics
  - Scans all files
  - Extracts dependencies
  - Builds module structure
  - Computes complexity

get_files(language) → Dict[str, FileInfo]
get_dependencies() → List[DependencyInfo]
get_metrics() → CodeMetrics
to_dict() → Dict (export for agents)
```

**Data Structures:**
```python
@dataclass
class FileInfo:
    path: str
    language: str
    size_bytes: int
    lines_of_code: int
    has_tests: bool

@dataclass
class CodeMetrics:
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    avg_file_size: float
    has_tests: bool
    complexity_score: float

@dataclass
class DependencyInfo:
    source: str
    target: str
    dependency_type: str
```

#### Agent Framework (`agents/base_agent.py`)

**Abstract Base Class:**
```python
class BaseAgent(ABC):
    @abstractmethod
    async def analyze() → AnalysisResult
    
    def add_finding(title, description, severity)
    def add_recommendation(text)
    def get_result() → AnalysisResult
```

**Result Structure:**
```python
@dataclass
class AnalysisResult:
    agent_name: str
    agent_type: str
    findings: List[Dict] = []
    recommendations: List[str] = []
    severity_scores: Dict[str, float] = {}
    metadata: Dict[str, Any] = {}
    execution_time_ms: float = 0.0
    status: str = "success"
    error_message: Optional[str] = None
```

#### Specialized Agents

**Architecture Agent** (`agents/architecture_agent.py`)
- Analyzes module structure
- Detects circular dependencies
- Identifies architectural patterns
- Assesses service boundaries

**Security Agent** (`agents/security_agent.py`)
- Scans for hardcoded secrets
- Detects unsafe patterns (SQL injection, eval, etc.)
- Identifies risky libraries
- Analyzes auth patterns

**Performance Agent** (`agents/performance_agent.py`)
- Finds performance anti-patterns
- Checks code complexity
- Identifies scalability issues
- Suggests optimizations

#### Agent Orchestrator (`orchestrator/agent_orchestrator.py`)

**Responsibilities:**
- Initialize all agents
- Execute agents in parallel
- Consolidate findings
- Generate unified report
- Calculate health score

**Health Score Calculation:**
```python
penalty = critical_count × 100 +
          high_count × 50 +
          medium_count × 20 +
          low_count × 5

health_score = max(0, 100 - (penalty / (critical_weight × 10)))
```

**Report Structure:**
```python
{
    'status': 'success',
    'timestamp': ISO-8601,
    'execution_time_ms': float,
    'indexed_metrics': CodeMetrics,
    'summary': {
        'total_findings': int,
        'findings_by_severity': {critical, high, medium, low},
        'health_score': float,
        'total_recommendations': int,
        'agents_executed': int
    },
    'agents': {
        'architecture': AgentStatus,
        'security': AgentStatus,
        'performance': AgentStatus
    },
    'findings': [Finding, ...],
    'recommendations': [str, ...]
}
```

### 4. Configuration Layer (`backend/config/`)

**settings.py** - Pydantic settings for environment variables
```python
class Settings(BaseSettings):
    azure_openai_endpoint: str
    azure_openai_api_key: str
    backend_host: str = "0.0.0.0"
    backend_port: int = 8000
    debug: bool = False
    # ... more settings
```

**semantic_kernel_config.py** - Semantic Kernel initialization
```python
def create_kernel() → Kernel
  - Creates SK instance
  - Adds Azure OpenAI service
  - Initializes memory
```

## Data Flow Diagrams

### Analysis Request Flow
```
Frontend User Input
    │
    ├─→ UploadPage.tsx
    │    └─→ apiClient.startAnalysis()
    │
    └─→ FastAPI POST /api/analyze
         │
         ├─→ Create Job ID
         ├─→ Store in analysis_jobs
         ├─→ Queue BackgroundTask
         │
         └─→ Return {job_id: string}
             │
             └─→ AnalysisDashboard.tsx
                 └─→ useAnalysisJob(jobId)
                    └─→ Poll /api/analysis/{job_id}/status every 2s
```

### Analysis Execution Flow
```
BackgroundTask _run_analysis()
    │
    ├─→ Clone repo (if URL provided) or use uploaded path
    │
    ├─→ CodeIndexer.index()
    │    ├─→ Scan files
    │    ├─→ Extract dependencies
    │    └─→ Compute metrics
    │
    ├─→ AgentOrchestrator.analyze()
    │    │
    │    ├─→ ArchitectureAgent.analyze() (parallel)
    │    ├─→ SecurityAgent.analyze() (parallel)
    │    └─→ PerformanceAgent.analyze() (parallel)
    │
    ├─→ Consolidate Results
    │    ├─→ Merge findings
    │    ├─→ Combine recommendations
    │    └─→ Calculate health score
    │
    └─→ Store results in analysis_jobs[job_id]
        └─→ Update status: "completed"
```

### Result Display Flow
```
AnalysisDashboard.tsx
    │
    ├─→ Parse results from API
    │
    ├─→ HealthScore Component
    │    └─→ Display overall score (0-100)
    │
    ├─→ SeveritySummary Component
    │    └─→ Bar chart by severity
    │
    ├─→ Tab Navigation
    │    ├─→ Overview Tab
    │    │    ├─→ Agent status cards
    │    │    └─→ Recommendations
    │    │
    │    ├─→ Architecture Tab
    │    │    └─→ FindingsList (Architecture findings)
    │    │
    │    ├─→ Security Tab
    │    │    └─→ FindingsList (Security findings)
    │    │
    │    └─→ Performance Tab
    │         └─→ FindingsList (Performance findings)
    │
    └─→ Severity Filter
         └─→ Filter findings by critical/high/medium/low
```

## Security Considerations

1. **Input Validation**
   - Repository URLs validated for git protocol
   - File uploads validated by extension
   - Size limits enforced

2. **Credential Management**
   - Azure OpenAI keys in environment variables only
   - No credentials in code or logs
   - CORS enabled but production should restrict origins

3. **Temporary File Handling**
   - Uploaded files stored in temporary directories
   - Cleanup on shutdown or error
   - No persistence of uploaded content

4. **Repository Access**
   - Only public repositories (for URL-based)
   - File-based uploads on local system
   - No authentication to target repositories

## Performance Considerations

1. **Parallel Agent Execution**
   - Agents run concurrently using asyncio
   - No blocking I/O in agents
   - Typical analysis: 2-5 minutes for medium repos

2. **Code Indexing**
   - Single pass through repository
   - AST parsing only for supported languages
   - Skips node_modules, venv, __pycache__, etc.

3. **Memory Management**
   - In-memory job storage (production: database)
   - Temporary directories cleaned up
   - No caching between requests

4. **API Optimization**
   - Background task processing
   - Job polling (2s intervals) instead of WebSocket
   - Compression-ready (configure in production)

## Scalability Roadmap

### Current (MVP - Single Instance)
- ✅ In-memory job storage
- ✅ Single process
- ✅ Local code indexing

### Phase 2
- 📋 Database for job persistence (PostgreSQL/MongoDB)
- 📋 Redis for caching and job queue
- 📋 Celery for distributed task processing

### Phase 3
- 📋 Kubernetes deployment
- 📋 Auto-scaling agent workers
- 📋 Load balancing

### Phase 4
- 📋 Distributed caching
- 📋 Historical analysis tracking
- 📋 Multi-region deployment

## Testing Strategy

### Backend Testing
```python
# tests/test_code_indexer.py
def test_scan_files()
def test_extract_dependencies()
def test_compute_metrics()

# tests/test_agents.py
def test_architecture_agent()
def test_security_agent()
def test_performance_agent()

# tests/test_orchestrator.py
def test_orchestrator_execution()
def test_health_score_calculation()
```

### Frontend Testing
```typescript
// src/__tests__/components.test.tsx
describe('HealthScore', () => {})
describe('FindingsList', () => {})

// src/__tests__/hooks.test.ts
describe('useAnalysisJob', () => {})

// src/__tests__/pages.test.tsx
describe('AnalysisDashboard', () => {})
```

### Integration Testing
```bash
# Full stack test
docker-compose up -d
pytest tests/integration/
npm run test:e2e
```

## Deployment Architecture

### Docker Compose (Development)
```yaml
services:
  backend:
    build: Dockerfile.backend
    ports: [8000:8000]
    volumes: [./backend:/app/backend]
  
  frontend:
    build: frontend/Dockerfile
    ports: [3000:3000]
    volumes: [./frontend/src:/app/src]
  
  redis:
    image: redis:7-alpine
    ports: [6379:6379]
```

### Production Deployment
- Container Registry: Azure Container Registry
- Orchestration: Azure Container Instances or AKS
- Database: Azure Database (PostgreSQL/CosmosDB)
- Storage: Azure Blob Storage (for temporary files)
- Monitoring: Application Insights

## Technology Stack Justification

| Component | Technology | Why |
|-----------|-----------|-----|
| Backend | Python | Data analysis, ML libraries ready |
| Orchestration | Semantic Kernel | Native Azure integration |
| API | FastAPI | Async, modern, fast |
| Frontend | React + TS | Type-safe, component reuse |
| Styling | Tailwind | Utility-first, responsive |
| Code Analysis | AST + tree-sitter | Accurate parsing |
| LLM | Azure OpenAI | Enterprise-grade, reliable |
| Containers | Docker | Reproducible environments |

---

This architecture provides a solid foundation for a scalable, maintainable multi-agent code analysis system.
