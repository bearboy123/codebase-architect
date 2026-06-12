# Kubernetes Deployment Guide

This guide walks through deploying the Codebase Architect Agent to a Kubernetes cluster.

## Prerequisites

- Kubernetes cluster 1.20+ (AKS, GKE, EKS, or local minikube)
- `kubectl` configured to access your cluster
- Docker images pushed to a container registry (Azure Container Registry, Docker Hub, etc.)
- Azure OpenAI credentials

## Directory Structure

```
k8s/
├── namespace.yaml              # Kubernetes namespace
├── configmap.yaml              # Configuration
├── secret.yaml                 # Sensitive data (API keys)
├── pvc.yaml                    # Persistent volume claim
├── backend-deployment.yaml     # Backend deployment
├── frontend-deployment.yaml    # Frontend deployment
├── backend-service.yaml        # Backend service
├── frontend-service.yaml       # Frontend service
├── ingress.yaml               # Ingress routing
├── rbac.yaml                  # Role-based access control
├── hpa.yaml                   # Horizontal pod autoscaling
└── README.md                  # This file
```

## Step 1: Build and Push Docker Images

### Build Backend Image
```bash
docker build -f Dockerfile.backend -t your-registry.azurecr.io/codebase-architect-backend:latest .
docker push your-registry.azurecr.io/codebase-architect-backend:latest
```

### Build Frontend Image
```bash
docker build -f frontend/Dockerfile -t your-registry.azurecr.io/codebase-architect-frontend:latest .
docker push your-registry.azurecr.io/codebase-architect-frontend:latest
```

## Step 2: Update Kubernetes Manifests

### Update image references
Edit the deployment files to use your registry:

**backend-deployment.yaml:**
```yaml
image: your-registry.azurecr.io/codebase-architect-backend:latest
```

**frontend-deployment.yaml:**
```yaml
image: your-registry.azurecr.io/codebase-architect-frontend:latest
```

### Update domain names
Edit `ingress.yaml` with your domain:
```yaml
- host: codebase-architect.example.com
- host: api.codebase-architect.example.com
```

### Configure secrets
Edit `secret.yaml` with your Azure OpenAI credentials:
```yaml
AZURE_OPENAI_ENDPOINT: "https://your-resource.openai.azure.com/"
AZURE_OPENAI_API_KEY: "your-api-key-here"
```

## Step 3: Deploy to Kubernetes

### Create namespace
```bash
kubectl apply -f k8s/namespace.yaml
```

### Create ConfigMap and Secrets
```bash
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secret.yaml
```

### Create storage
```bash
kubectl apply -f k8s/pvc.yaml
```

### Create RBAC resources
```bash
kubectl apply -f k8s/rbac.yaml
```

### Deploy applications
```bash
kubectl apply -f k8s/backend-deployment.yaml
kubectl apply -f k8s/frontend-deployment.yaml
```

### Create services
```bash
kubectl apply -f k8s/backend-service.yaml
kubectl apply -f k8s/frontend-service.yaml
```

### Create ingress
```bash
kubectl apply -f k8s/ingress.yaml
```

### Set up autoscaling
```bash
kubectl apply -f k8s/hpa.yaml
```

### Deploy all at once
```bash
kubectl apply -f k8s/
```

## Step 4: Verify Deployment

### Check pod status
```bash
kubectl get pods -n codebase-architect
kubectl describe pod <pod-name> -n codebase-architect
```

### Check services
```bash
kubectl get svc -n codebase-architect
```

### Check ingress
```bash
kubectl get ingress -n codebase-architect
```

### View logs
```bash
# Backend logs
kubectl logs -f deployment/codebase-architect-backend -n codebase-architect

# Frontend logs
kubectl logs -f deployment/codebase-architect-frontend -n codebase-architect
```

### Port forward for testing
```bash
# Backend
kubectl port-forward svc/codebase-architect-backend 8000:8000 -n codebase-architect

# Frontend
kubectl port-forward svc/codebase-architect-frontend 3000:3000 -n codebase-architect

# Access at http://localhost:3000
```

## Step 5: Set Up Ingress Controller

### For NGINX Ingress Controller
```bash
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx --namespace ingress-nginx --create-namespace
```

### For Azure Application Gateway Ingress Controller (AKS)
```bash
helm repo add application-gateway-kubernetes-ingress https://appgwingress.blob.core.windows.net/ingress-azure-helm-package/
helm install ingress-appgw application-gateway-kubernetes-ingress/ingress-azure \
  -n kube-system \
  --set appgw.subscriptionId=<subscription-id> \
  --set appgw.resourceGroup=<resource-group> \
  --set appgw.name=<appgw-name>
```

## Step 6: Set Up TLS Certificates (Optional but Recommended)

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

## Scaling Configuration

### Horizontal Pod Autoscaling (HPA)
The `hpa.yaml` automatically scales pods based on:
- **CPU**: Scales up at 70% utilization, down at lower
- **Memory**: Scales up at 80% utilization, down at lower
- **Min replicas**: 2
- **Max replicas**: 5

Monitor HPA status:
```bash
kubectl get hpa -n codebase-architect
kubectl describe hpa codebase-architect-backend-hpa -n codebase-architect
```

### Manual scaling
```bash
kubectl scale deployment codebase-architect-backend --replicas=3 -n codebase-architect
```

## Monitoring and Logging

### View resource usage
```bash
kubectl top nodes
kubectl top pods -n codebase-architect
```

### Stream logs
```bash
# All pods
kubectl logs -f -l app=codebase-architect -n codebase-architect

# Specific component
kubectl logs -f deployment/codebase-architect-backend -n codebase-architect
```

### Health checks
```bash
# Check backend health
kubectl exec -it <backend-pod> -n codebase-architect -- curl localhost:8000/health

# Check liveness
kubectl describe pod <pod-name> -n codebase-architect | grep -A 5 Liveness
```

## Updates and Rollouts

### Update image
```bash
kubectl set image deployment/codebase-architect-backend \
  backend=your-registry.azurecr.io/codebase-architect-backend:v1.1.0 \
  -n codebase-architect
```

### Monitor rollout
```bash
kubectl rollout status deployment/codebase-architect-backend -n codebase-architect
kubectl rollout history deployment/codebase-architect-backend -n codebase-architect
```

### Rollback if needed
```bash
kubectl rollout undo deployment/codebase-architect-backend -n codebase-architect
```

## Backup and Recovery

### Backup Kubernetes resources
```bash
kubectl get all -n codebase-architect -o yaml > backup.yaml
```

### Backup persistent data
```bash
kubectl exec <backend-pod> -n codebase-architect -- tar czf - /app/cache > cache-backup.tar.gz
```

### Restore from backup
```bash
kubectl apply -f backup.yaml
```

## Troubleshooting

### Pods not starting
```bash
kubectl describe pod <pod-name> -n codebase-architect
kubectl logs <pod-name> -n codebase-architect
```

### ImagePullBackOff
- Verify image exists in registry
- Check registry credentials/access

### CrashLoopBackOff
- Check logs for application errors
- Verify environment variables in ConfigMap/Secret

### Services not accessible
- Check Ingress configuration
- Verify DNS resolution
- Check firewall rules

### Storage issues
```bash
kubectl get pvc -n codebase-architect
kubectl describe pvc codebase-architect-pvc -n codebase-architect
```

## Production Checklist

- [ ] Images pushed to private registry
- [ ] Secrets using Azure Key Vault or sealed-secrets
- [ ] Network policies configured
- [ ] Resource quotas set
- [ ] Pod disruption budgets configured
- [ ] Monitoring and alerting enabled
- [ ] Backup strategy in place
- [ ] TLS certificates configured
- [ ] Load testing completed
- [ ] Disaster recovery plan documented

## Useful Commands

```bash
# Get cluster info
kubectl cluster-info

# Get nodes
kubectl get nodes

# Get all resources in namespace
kubectl get all -n codebase-architect

# Get detailed pod info
kubectl get pod <pod-name> -n codebase-architect -o yaml

# Execute command in pod
kubectl exec -it <pod-name> -n codebase-architect -- /bin/bash

# Port forward
kubectl port-forward pod/<pod-name> 8000:8000 -n codebase-architect

# Delete all resources
kubectl delete namespace codebase-architect
```

## Additional Resources

- [Kubernetes Official Documentation](https://kubernetes.io/docs/)
- [kubectl Cheat Sheet](https://kubernetes.io/docs/reference/kubectl/cheatsheet/)
- [Azure Kubernetes Service (AKS)](https://docs.microsoft.com/en-us/azure/aks/)
- [Google Kubernetes Engine (GKE)](https://cloud.google.com/kubernetes-engine/docs)
- [AWS EKS](https://docs.aws.amazon.com/eks/)

## Support

For issues or questions:
1. Check pod logs: `kubectl logs <pod-name> -n codebase-architect`
2. Check events: `kubectl describe pod <pod-name> -n codebase-architect`
3. Review Kubernetes status: `kubectl get events -n codebase-architect`
4. Consult troubleshooting section above
