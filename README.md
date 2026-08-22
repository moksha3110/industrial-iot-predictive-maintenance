# Industrial IoT Predictive Maintenance

## One-click recipient setup

After extracting the ZIP on Windows, install Python 3.11+ and double-click **`START_WINDOWS.bat`**. It creates the virtual environment, installs dependencies, runs tests, starts the server, and opens the dashboard. See `FRIEND_SETUP_GUIDE.md` for complete recipient instructions.

A complete academic FastAPI platform that monitors four simulated industrial machines using temperature, vibration and pressure telemetry. It persists readings and alerts, calculates explainable health scores, detects sensor failures, provides a responsive dashboard and falls back safely to local owner notifications when Amazon SNS is not configured.

> Academic prototype: demonstration thresholds are not certified industrial safety limits.

## Features

- Four seeded machines, live readings, trends, health/risk and recommendations
- Abnormal temperature, vibration and pressure detection
- Missing, invalid and injected sensor-failure detection with persisted critical alerts
- Local log/dashboard notifications and optional Amazon SNS
- REST API and Swagger, SQLite locally and configurable PostgreSQL production URL
- Docker/Compose, EKS-ready Kubernetes manifests and GitHub Actions CI/CD

## Structure

`app/` contains API, analytics, persistence, notifications, templates and static UI; `tests/` automated tests; `k8s/` deployment resources; `docs/` Mermaid architecture and screenshot guide; `.github/workflows/` CI/CD; `REPORT.md` the exact-order assignment report.

## Local installation and run

Prerequisites: Python 3.11+ (3.12 recommended), optional Docker.

```powershell
cd C:\Users\surya\Downloads\industrial-iot-predictive-maintenance
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
uvicorn app.main:app --reload
```

- Dashboard: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Tests: `pytest -v`

Configuration comes from environment variables listed in `.env.example`. Set a PostgreSQL SQLAlchemy URL in `DATABASE_URL` for production. For SNS, create a topic and confirmed Email subscription, then set `AWS_REGION` and `SNS_TOPIC_ARN`; use IAM roles/IRSA in AWS rather than access keys.

## Docker and Docker Hub

```bash
docker build -t predictive-maintenance-iot:latest .
docker run --rm -p 8000:8000 predictive-maintenance-iot:latest
# or
docker compose up --build

docker login
docker tag predictive-maintenance-iot:latest <DOCKERHUB_USERNAME>/predictive-maintenance-iot:latest
docker push <DOCKERHUB_USERNAME>/predictive-maintenance-iot:latest
```

No Docker Hub credentials are assumed or stored. Replace the image placeholder in `k8s/deployment.yaml`, securely create a Secret from `secret.example.yaml`, then run `kubectl apply -f k8s/`. The manifests demonstrate two replicas, probes, rolling updates, resources, ClusterIP, ALB Ingress and HPA.

GitHub Actions tests and builds every PR. On main, it pushes only when repository secrets `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` exist. AWS production flow is sensors → IoT gateway → AWS IoT Core → EKS/FastAPI → RDS, with SNS owner alerts, CloudWatch monitoring and S3 archives. See `docs/architecture.md`.

## Lecturer demo walkthrough

1. Run `uvicorn app.main:app --reload` and open the dashboard.
2. Show the four machines, summary, trend chart and `/docs`.
3. Select a machine and generate a normal reading.
4. Inject high vibration; show reduced health and the incident.
5. Fail its temperature sensor; show Sensor Failure and owner alert.
6. Restore all sensors and show Healthy status.
7. Run `pytest -v`.
8. Show the running Docker container, `k8s/`, the AWS Mermaid diagram and `.github/workflows/ci-cd.yml`.

## REST examples

```bash
curl http://localhost:8000/api/machines
curl -X POST http://localhost:8000/api/simulator/readings -H "Content-Type: application/json" -d '{"machine_id":1,"scenario":"high_vibration"}'
curl -X POST http://localhost:8000/api/simulator/machines/1/failure/temperature
curl -X POST http://localhost:8000/api/simulator/machines/1/restore/temperature
curl http://localhost:8000/api/alerts
```

## Troubleshooting

- Run commands from the project root so templates/static files resolve.
- Delete only the demo `predictive_maintenance.db` if a clean local seed is required.
- If Chart.js cannot load, the table and APIs remain functional and the UI displays a fallback.
- SQLite is for one-instance demos; use RDS PostgreSQL for multiple Kubernetes replicas.
- SNS errors never crash ingestion; inspect logs and the persisted alert list.

The full graded submission is in `REPORT.md`; genuine screenshot instructions are in `docs/SCREENSHOT_GUIDE.md`.
