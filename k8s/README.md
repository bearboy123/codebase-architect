# Kubernetes (k3s) Deployment Guide

Complete guide for deploying Codebase Architect Agent to k3s on WSL2 or any Kubernetes cluster.

## Quick Start (5 minutes)

### Prerequisites

- **k3s installed**: On WSL2 with Docker Desktop
- **kubectl configured**: `kubectl get nodes` should work
- **Azure OpenAI credentials**: API key and deployment name

### Install k3s (WSL2)

```bash
# On WSL2, install k3s
curl -sfL https://get.k3s.io | sh -

# Verify installation
kubectl get nodes
kubectl cluster-info
```

### Deploy Everything at Once

```bash
# 1. Clone and navigate to k8s folder
cd k8s

# 2. Edit secret.yaml with your Azure OpenAI credentials
nano secret.yaml

# 3. Deploy all resources
kubectl apply -k .

# 4. Check deployment status
kubectl get pods -n codebase-architect

# 5. Access the application (see Access Applications section)
```

## Directory Structure

```
k8s/
├── namespace.yaml              # Kubernetes namespace
├── configmap.yaml              # Application configuration
├── secret.yaml                 # Azure OpenAI credentials (edit before deploying)
├── pvc.yaml                    # Persistent volume claim for caching
├── backend-deployment.yaml     # Backend FastAPI deployment
├── frontend-deployment.yaml    # Frontend React deployment
├── backend-service.yaml        # Backend service (port 8000)
├── frontend-service.yaml       # Frontend service (port 5173)
├── ingress.yaml               # Ingress routing (optional)
├── rbac.yaml                  # Service accounts & RBAC
├── hpa.yaml                   # Horizontal Pod Autoscaler
├── kustomization.yaml         # Kustomize configuration (deploy all resources)
└── README.md                  # This file
```

## Step-by-Step Deployment

### 1. Configure Secrets

**Edit `secret.yaml` with your Azure OpenAI credentials:**

```bash
nano secret.yaml
# Or use your favorite editor
```

Update these values:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: codebase-architect-secrets
  namespace: codebase-architect
type: Opaque
stringData:
  AZURE_OPENAI_ENDPOINT: "https://your-resource.openai.azure.com/"
  AZURE_OPENAI_API_KEY: "your-api-key"
  AZURE_OPENAI_MODEL_DEPLOYMENT: "your-model-deployment"
  AZURE_OPENAI_API_VERSION: "2025-01-01-preview"
```

### 2. Deploy Using Kustomize (Recommended)

```bash
# Deploy all resources in correct order
kubectl apply -k .

# Verify deployment
kubectl get pods -n codebase-architect
kubectl get svc -n codebase-architect
```

### 3. Deploy Manually (Alternative)

If you prefer manual deployment:

```bash
# Create namespace first
kubectl apply -f namespace.yaml

# Create ConfigMap and Secrets
kubectl apply -f configmap.yaml
kubectl apply -f secret.yaml

# Create RBAC
kubectl apply -f rbac.yaml

# Create storage
kubectl apply -f pvc.yaml

# Deploy applications
kubectl apply -f backend-deployment.yaml
kubectl apply -f backend-service.yaml
kubectl apply -f frontend-deployment.yaml
kubectl apply -f frontend-service.yaml

# Optional: Set up ingress and autoscaling
kubectl apply -f ingress.yaml
kubectl apply -f hpa.yaml
```

## Verify Deployment

### Check Pod Status

```bash
# View all pods
kubectl get pods -n codebase-architect

# Describe a pod (shows events and status)
kubectl describe pod <pod-name> -n codebase-architect

# Check pod logs
kubectl logs -f deployment/codebase-architect-backend -n codebase-architect
kubectl logs -f deployment/codebase-architect-frontend -n codebase-architect
```

### Check Services

```bash
kubectl get svc -n codebase-architect
```

### Check Ingress Status

```bash
kubectl get ingress -n codebase-architect
```

## Access the Application

### Option A: Port Forwarding (Development/Testing)

**Terminal 1 - Backend:**
```bash
kubectl port-forward -n codebase-architect svc/backend-service 8000:8000

# Test:
curl http://localhost:8000/health
```

**Terminal 2 - Frontend:**
```bash
kubectl port-forward -n codebase-architect svc/frontend-service 5173:5173

# Open: http://localhost:5173
```

### Option B: NodePort Service (Quick Testing)

Edit `backend-service.yaml` and change:
```yaml
type: ClusterIP
```
to:
```yaml
type: NodePort
```

Then:
```bash
kubectl apply -f backend-service.yaml

# Get NodePort
kubectl get svc -n codebase-architect

# Access via: http://k3s-node-ip:node-port
```

### Option C: Ingress (Production)

```bash
# Apply ingress
kubectl apply -f ingress.yaml

# Edit /etc/hosts (on WSL2):
# 127.0.0.1 codebase-architect.local

# Access: http://codebase-architect.local
```

## Monitoring & Troubleshooting

### View Pod Logs

```bash
# Backend logs
kubectl logs -f deployment/codebase-architect-backend -n codebase-architect

# Frontend logs  
kubectl logs -f deployment/codebase-architect-frontend -n codebase-architect

# Specific pod
kubectl logs <pod-name> -n codebase-architect

# With timestamps
kubectl logs -f <pod-name> -n codebase-architect --timestamps=true
```

### Debug Inside a Pod

```bash
# Execute command in pod
kubectl exec -it <pod-name> -n codebase-architect -- /bin/bash

# Test backend from frontend pod
kubectl exec -it <frontend-pod> -n codebase-architect -- curl http://backend-service:8000/health

# Check environment variables
kubectl exec <pod-name> -n codebase-architect -- env | grep AZURE
```

### Check Events

```bash
# All events in namespace
kubectl get events -n codebase-architect --sort-by='.lastTimestamp'

# Describe specific resource
kubectl describe pod <pod-name> -n codebase-architect
```

### Common Issues & Solutions

**Pods stuck in CrashLoopBackOff:**
```bash
# 1. Check logs
kubectl logs <pod-name> -n codebase-architect

# 2. Common causes:
# - Missing/incorrect secrets
# - Wrong Azure OpenAI credentials
# - PVC not bound
# - Insufficient resources

# 3. Solution:
kubectl describe pod <pod-name> -n codebase-architect
```

**ImagePullBackOff:**
```bash
# Check image in deployment manifest
kubectl get deployment codebase-architect-backend -n codebase-architect -o yaml | grep image

# k3s uses containerd - ensure image is available
crictl image ls
```

**Secrets not loading:**
```bash
# Verify secret exists
kubectl get secret -n codebase-architect

# Check secret content (decode)
kubectl get secret codebase-architect-secrets -n codebase-architect -o jsonpath='{.data.AZURE_OPENAI_API_KEY}' | base64 -d
```

**PVC not binding:**
```bash
# Check PVC status
kubectl get pvc -n codebase-architect
kubectl describe pvc codebase-architect-pvc -n codebase-architect

# k3s uses local storage by default
kubectl get storageclass
```

**Ingress not working:**
```bash
# Check ingress controller
kubectl get pods -n kube-system | grep ingress

# If using k3s with built-in traefik:
kubectl get pods -n kube-system | grep traefik

# Check ingress status
kubectl describe ingress codebase-architect-ingress -n codebase-architect
```

## Scaling & Performance

### Horizontal Pod Autoscaling (HPA)

```bash
# HPA configuration in hpa.yaml:
# - Min replicas: 1
# - Max replicas: 5
# - CPU target: 80%
# - Memory target: 80%

# Watch autoscaling in action
kubectl get hpa -n codebase-architect -w

# Check HPA details
kubectl describe hpa codebase-architect-backend -n codebase-architect

# Manual scaling (overrides HPA)
kubectl scale deployment codebase-architect-backend --replicas=3 -n codebase-architect
```

### Resource Monitoring

```bash
# View resource usage
kubectl top nodes
kubectl top pods -n codebase-architect
```

## Updates & Rollouts

### Update Image

```bash
# Update backend image to new version
kubectl set image deployment/codebase-architect-backend \
  backend=localhost:5000/codebase-architect-backend:v1.1.0 \
  -n codebase-architect
```

### Monitor Rollout

```bash
# Watch rollout status
kubectl rollout status deployment/codebase-architect-backend -n codebase-architect

# View rollout history
kubectl rollout history deployment/codebase-architect-backend -n codebase-architect

# Rollback if needed
kubectl rollout undo deployment/codebase-architect-backend -n codebase-architect
```

## Backup & Recovery

### Backup All Resources

```bash
# Export entire namespace
kubectl get all -n codebase-architect -o yaml > backup.yaml

# Export with CRDs
kubectl get all,cm,secret -n codebase-architect -o yaml > backup.yaml
```

### Restore from Backup

```bash
# Restore all resources
kubectl apply -f backup.yaml
```

### Backup Persistent Data

```bash
# Backup PVC data
kubectl exec <backend-pod> -n codebase-architect -- tar czf - /app/cache > cache-backup.tar.gz
```

## Cleanup

### Delete Application

```bash
# Delete specific resources
kubectl delete deployment -n codebase-architect --all

# Delete entire namespace (warning: deletes everything)
kubectl delete namespace codebase-architect
```

## Step 5: Optional - Set Up Ingress Controller

### For k3s (Built-in Traefik)

k3s comes with Traefik ingress controller by default:

```bash
# Check traefik is running
kubectl get pods -n kube-system | grep traefik

# Traefik dashboard (optional)
kubectl port-forward -n kube-system svc/traefik 8080:8080

# Access: http://localhost:8080/dashboard
```

### For NGINX Ingress Controller (Alternative)

```bash
# Add Helm repo
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm repo update

# Install nginx-ingress
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx \
  --create-namespace
```

## Step 6: Optional - Set Up TLS (Let's Encrypt)

### Install cert-manager
```bash
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  -n cert-manager --create-namespace \
  --set installCRDs=true
```

### Create ClusterIssuer for Let's Encrypt
```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: nginx
```

```bash
kubectl apply -f cert-issuer.yaml
```

## Step 7: Configure DNS

Update your DNS provider to point to the Ingress IP:

```bash
# Get Ingress IP
kubectl get ingress -n codebase-architect

# Add DNS records
codebase-architect.example.com    → <INGRESS-IP>
api.codebase-architect.example.com → <INGRESS-IP>
```

### Install cert-manager

```bash
# Add Helm repo
helm repo add jetstack https://charts.jetstack.io
helm repo update

# Install cert-manager
helm install cert-manager jetstack/cert-manager \
  -n cert-manager --create-namespace \
  --set installCRDs=true
```

### Create ClusterIssuer for Let's Encrypt

```yaml
apiVersion: cert-manager.io/v1
kind: ClusterIssuer
metadata:
  name: letsencrypt-prod
spec:
  acme:
    server: https://acme-v02.api.letsencrypt.org/directory
    email: admin@example.com
    privateKeySecretRef:
      name: letsencrypt-prod
    solvers:
    - http01:
        ingress:
          class: traefik  # or 'nginx' if using nginx controller
```

```bash
kubectl apply -f cert-issuer.yaml
```

### Update Ingress to Use TLS

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: codebase-architect-ingress
  annotations:
    cert-manager.io/cluster-issuer: "letsencrypt-prod"
spec:
  tls:
  - hosts:
    - codebase-architect.local
    secretName: codebase-architect-tls
  rules:
  - host: codebase-architect.local
    http:
      paths:
      - path: /
        pathType: Prefix
        backend:
          service:
            name: frontend-service
            port:
              number: 5173
```

## Step 7: Configure DNS (Optional)

For local development:

```bash
# Edit /etc/hosts on Windows WSL2:
127.0.0.1 codebase-architect.local
```

For production:

```bash
# Get ingress IP
kubectl get ingress -n codebase-architect

# Add DNS records via your DNS provider:
codebase-architect.example.com → <INGRESS-IP>
```

## Configuration Files Overview

### backend-deployment.yaml

Key settings:
- **Replicas**: 2 (autoscales 1-5 with HPA)
- **Resource requests**: 250m CPU, 512Mi memory
- **Resource limits**: 1000m CPU, 2Gi memory
- **Health checks**: Liveness and readiness probes
- **Storage**: Mounts PVC at /app/cache for caching

### frontend-deployment.yaml

Key settings:
- **Replicas**: 2 (autoscales 1-5 with HPA)
- **Resource requests**: 100m CPU, 256Mi memory
- **Resource limits**: 500m CPU, 1Gi memory
- **Environment**: VITE_API_URL points to backend service

### configmap.yaml

Non-sensitive configuration:
- `DEBUG`: Enable/disable debug mode
- `LOG_LEVEL`: Logging level
- `MAX_FILE_SIZE_MB`: Max file size for analysis
- `ANALYSIS_TIMEOUT`: Max analysis duration

### secret.yaml

**Important**: Edit before deploying!
- `AZURE_OPENAI_ENDPOINT`: Your Azure OpenAI endpoint
- `AZURE_OPENAI_API_KEY`: Your API key
- `AZURE_OPENAI_MODEL_DEPLOYMENT`: Your model deployment
- `AZURE_OPENAI_API_VERSION`: API version

## Production Checklist

- [ ] Edit secret.yaml with real Azure credentials
- [ ] Use secret management (sealed-secrets, Azure Key Vault)
- [ ] Enable Network Policies for security
- [ ] Set resource quotas per namespace
- [ ] Configure Pod Disruption Budgets
- [ ] Enable monitoring (Prometheus/Grafana)
- [ ] Set up backup strategy
- [ ] Configure TLS with Let's Encrypt
- [ ] Load test the deployment
- [ ] Document disaster recovery procedures
- [ ] Implement RBAC policies
- [ ] Regular security updates for k3s

## Useful kubectl Commands

```bash
# Cluster information
kubectl cluster-info
kubectl get nodes
kubectl describe node <node-name>

# Namespace management
kubectl get ns
kubectl create namespace <name>
kubectl delete namespace <name>

# Deployments
kubectl get deployments -n codebase-architect
kubectl describe deployment <deployment-name> -n codebase-architect
kubectl rollout status deployment/<deployment-name> -n codebase-architect
kubectl scale deployment/<deployment-name> --replicas=3 -n codebase-architect

# Pods
kubectl get pods -n codebase-architect
kubectl describe pod <pod-name> -n codebase-architect
kubectl logs <pod-name> -n codebase-architect
kubectl logs -f <pod-name> -n codebase-architect  # Follow logs

# Services
kubectl get svc -n codebase-architect
kubectl describe svc <service-name> -n codebase-architect
kubectl port-forward svc/<service-name> 8000:8000 -n codebase-architect

# Resources
kubectl get all -n codebase-architect
kubectl get pvc -n codebase-architect
kubectl get configmap -n codebase-architect
kubectl get secret -n codebase-architect

# Debugging
kubectl exec -it <pod-name> -n codebase-architect -- /bin/bash
kubectl cp <pod-name>:/path/to/file ./local-file -n codebase-architect
kubectl describe events -n codebase-architect

# Cleanup
kubectl delete pod <pod-name> -n codebase-architect
kubectl delete deployment <deployment-name> -n codebase-architect
kubectl delete namespace codebase-architect  # Delete everything!
```

## Scaling Configuration

## Additional Resources

- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [k3s Documentation](https://docs.k3s.io/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Helm Documentation](https://helm.sh/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/aks/)

## Support & Troubleshooting

For detailed troubleshooting, see [ERROR_HANDLING.md](../ERROR_HANDLING.md)

**Quick troubleshooting steps:**
1. Check pod logs: `kubectl logs -f <pod-name> -n codebase-architect`
2. Describe pod for events: `kubectl describe pod <pod-name> -n codebase-architect`
3. Check namespace events: `kubectl get events -n codebase-architect --sort-by='.lastTimestamp'`
4. Test connectivity: `kubectl exec -it <pod> -n codebase-architect -- curl http://backend-service:8000/health`

**Common issues:**
- **CrashLoopBackOff**: Check logs and secret configuration
- **ImagePullBackOff**: Verify image in deployment manifest
- **Pending pods**: Check resources: `kubectl describe node`
- **Connection refused**: Check services: `kubectl get svc -n codebase-architect`

---

**Happy deploying! 🚀**
