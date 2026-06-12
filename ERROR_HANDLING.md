# Error Handling & Edge Cases Guide

## Backend Error Handling

### 1. API-Level Errors

**400 Bad Request**
- Missing required fields (repo_url or repo_path)
- Invalid job_id
- Malformed upload file

**404 Not Found**
- Job ID doesn't exist
- Repository path doesn't exist

**500 Internal Server Error**
- Unexpected exceptions in analysis
- Azure OpenAI connection failures
- File system permission issues

### 2. Analysis-Level Errors

**Repository Errors**
```python
# Handled in _run_analysis():
- Git clone timeout → Set 60s timeout with helpful message
- Permission denied → Check repo access
- Network errors → Retry logic with exponential backoff
- Large repos → Implement file size limits and filtering
```

**Indexing Errors**
```python
# CodeIndexer error handling:
- File too large → Skip files > max_file_size_mb
- Binary files → Auto-detect and skip
- Encoding errors → Use fallback encoding (utf-8 with errors='ignore')
- Circular symlinks → Track visited paths to prevent loops
- Permission denied → Skip protected files
```

**Agent Analysis Errors**
```python
# Each agent has try-catch:
- Azure OpenAI timeout → Retry with increased timeout
- Rate limit exceeded → Queue and retry later
- Invalid code syntax → Graceful degradation
- Empty findings → Return default/empty results
```

### 3. Database/Storage Errors

```python
# Handled in app.py:
- Temp directory cleanup failures → Log and continue
- Disk space errors → Check available space
- File lock errors → Retry with backoff
```

## Frontend Error Handling

### 1. API Error Responses

```typescript
// services/api.ts handles:
- Network timeouts → Show "Server unreachable" message
- 4xx errors → Show validation/request errors
- 5xx errors → Show "Server error" with job ID for debugging
- Connection refused → Show "Backend not running" hint
```

### 2. Analysis State Errors

```typescript
// hooks/useAnalysis.ts handles:
- Job not found → Refresh or start new analysis
- Progress stuck → Timeout after 30 minutes
- Results parsing error → Show raw data for inspection
- Missing fields → Graceful defaults
```

### 3. UI Errors

```typescript
// React error boundaries catch:
- Component render errors
- Invalid props
- State corruption
- Re-render with user message: "Something went wrong. Try refreshing."
```

## Edge Cases Handled

### 1. Large Repositories
- **Max file size**: Configurable, defaults to 10MB
- **Max files**: Skip if > 100k files (configurable)
- **Timeout**: 5 minutes per agent analysis
- **Solution**: Stream results, show progress updates

### 2. Empty/Minimal Repositories
- **Empty repo**: Return empty results, not error
- **Single file**: Analyze successfully
- **No supported files**: Return "Unable to analyze" gracefully

### 3. Special Characters in Paths
- **Unicode paths**: Handle UTF-8 properly
- **Spaces in paths**: Properly escape for shell commands
- **Symlinks**: Follow with cycle detection

### 4. Network Issues
- **Clone timeout**: 60-second timeout with retry
- **API rate limits**: Queue requests, retry with exponential backoff
- **Connection loss**: Graceful error message, allow retry

### 5. Concurrent Analysis
- **Multiple jobs**: Each runs independently with own job_id
- **Resource limits**: Monitor CPU/memory, queue if needed
- **Memory leaks**: Cleanup after each analysis completes

## Testing Edge Cases

```bash
# Test empty directory
mkdir test_empty && python -c "from backend.api.app import app; ..."

# Test large file handling
dd if=/dev/zero of=test_large.bin bs=1M count=100

# Test permission denied
chmod 000 test_dir && curl -X POST ...

# Test concurrent requests
for i in {1..10}; do curl -X POST ... & done

# Test invalid inputs
curl -X POST http://localhost:8000/api/analyze -d '{}'
curl -X POST http://localhost:8000/api/analyze -d '{"invalid": "field"}'
```

## Monitoring & Logging

### 1. Backend Logging

```python
# Enabled in main.py:
- INFO: Job start/completion
- WARNING: Skipped files, timeouts
- ERROR: Exceptions with full traceback
- DEBUG: Detailed analysis progress
```

### 2. Frontend Logging

```typescript
// Enabled in services/api.ts:
- API request/response logging
- Error boundaries with stack traces
- Performance timing
- Analysis state transitions
```

### 3. Metrics Collection

```python
# Available via /api/metrics:
- Total jobs: Count of all analyses
- Completed: Successful analyses
- Failed: Failed analyses
- Running: Currently processing
- Pending: Queued for analysis
```

## Recovery Strategies

### If Backend Crashes
1. Restart backend: `python main.py`
2. In-memory jobs are lost (would persist with database in production)
3. User must restart analysis

### If Frontend Crashes
1. Refresh browser page
2. Backend continues analysis in background
3. Query job status with job_id from local storage

### If Azure OpenAI Is Down
1. Agents will timeout after 30 seconds
2. Analysis marks as failed with error message
3. User can retry when service is restored

### If Disk Is Full
1. Temp directory cleanup will fail
2. Subsequent analyses will fail
3. Admin must free disk space

## Configuration for Robustness

```python
# In backend/config/settings.py:
ANALYSIS_TIMEOUT = 300  # 5 minutes total
AGENT_TIMEOUT = 60  # Per agent
GIT_CLONE_TIMEOUT = 60
MAX_FILE_SIZE_MB = 10
MAX_FILES_PER_REPO = 100000
RETRY_ATTEMPTS = 3
RETRY_BACKOFF_FACTOR = 2
```

## Future Improvements

1. **Persistent Storage**: Replace in-memory jobs with database
2. **Message Queue**: Use async queue for scalability
3. **Circuit Breaker**: Fail fast if Azure OpenAI is down
4. **Request Validation**: Stricter schema validation
5. **Rate Limiting**: Per-user rate limits
6. **Health Checks**: Periodic Azure OpenAI connectivity checks
7. **Graceful Degradation**: Partial results if some agents fail
8. **Detailed Audit Trail**: Track all analysis requests and results

---

For questions about specific error cases, check the implementation:
- Backend: `backend/api/app.py` - Lines 255-326 (error handling in _run_analysis)
- Frontend: `frontend/src/services/api.ts` - Error response handling
- Analyzers: `backend/analyzers/code_indexer.py` - File handling edge cases
