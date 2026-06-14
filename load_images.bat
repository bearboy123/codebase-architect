@echo off
echo Saving images...
docker save -o codebase.tar codebase-architect-backend:latest codebase-architect-frontend:latest
if %errorlevel% neq 0 exit /b %errorlevel%

echo Copying to desktop-worker...
docker cp codebase.tar desktop-worker:/codebase.tar
docker exec desktop-worker ctr -n k8s.io images import /codebase.tar

echo Copying to desktop-worker2...
docker cp codebase.tar desktop-worker2:/codebase.tar
docker exec desktop-worker2 ctr -n k8s.io images import /codebase.tar

echo Copying to desktop-control-plane...
docker cp codebase.tar desktop-control-plane:/codebase.tar
docker exec desktop-control-plane ctr -n k8s.io images import /codebase.tar

echo Done.
