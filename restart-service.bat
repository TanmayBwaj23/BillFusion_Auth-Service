@echo off
echo Stopping all containers...
docker-compose down --remove-orphans

echo Removing old images...
docker rmi auth-service-auth-service 2>nul

echo Building fresh image...
docker-compose build --no-cache auth-service

echo Starting services...
docker-compose up -d

echo Waiting for services to be healthy...
timeout /t 10

echo Checking service status...
docker-compose ps

echo.
echo Service logs:
docker-compose logs --tail=20 auth-service

echo.
echo Frontend is running at: http://localhost:5173
echo Backend should be at: http://localhost:8000
echo.
echo If backend is still failing, check logs with: docker-compose logs -f auth-service
