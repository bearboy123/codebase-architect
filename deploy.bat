@echo off
echo Building backend image...
docker build -f Dockerfile.backend -t codebase-architect-backend:latest .
if %errorlevel% neq 0 exit /b %errorlevel%

echo Building frontend image...
docker build -f frontend/Dockerfile -t codebase-architect-frontend:latest ./frontend
if %errorlevel% neq 0 exit /b %errorlevel%

echo Deploying to Kubernetes...
kubectl apply -k k8s/
if %errorlevel% neq 0 exit /b %errorlevel%

echo.
echo ========================================================
echo Deployment successful! 
echo The frontend image now includes the necessary tailwind configuration.
echo.
echo To test the application locally, simply open your browser and navigate to:
echo http://localhost:3000
echo.
echo (It may take a minute for the LoadBalancer to become available.)
echo ========================================================
pause
