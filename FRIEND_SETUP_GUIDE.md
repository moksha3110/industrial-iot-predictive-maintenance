# Setup Guide for the Recipient

## Fastest Windows setup

1. Extract the entire ZIP. Do not run it from inside the ZIP preview.
2. Install Python 3.11 or newer from <https://www.python.org/downloads/>. Select **Add Python to PATH** during installation.
3. Double-click `START_WINDOWS.bat`.
4. On the first run, wait while it creates an isolated environment, installs dependencies and runs seven tests.
5. The dashboard opens automatically at <http://127.0.0.1:8000>.
6. Keep the command window open. Press `Ctrl+C` in that window to stop the server.

No AWS account, database server, email credentials, or Docker installation is required. The default demonstration uses a local SQLite database and writes owner notifications to the application log, database, and dashboard.

## What to demonstrate

1. Confirm that four machines appear on the dashboard.
2. Select a machine and click **Generate normal reading**.
3. Click **Inject high vibration** and observe its reduced health and Critical status.
4. Click **Fail temperature** and observe the Sensor Failure badge and Owner Alert.
5. Click **Restore all sensors**.
6. Open <http://127.0.0.1:8000/docs> to show the REST API.

## Manual Windows setup

Open Command Prompt in the extracted folder:

```bat
python -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements.txt
copy .env.example .env
.venv\Scripts\python.exe -m pytest -v
.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

Then open <http://127.0.0.1:8000>.

## Docker alternative

With Docker Desktop running:

```bash
docker build -t predictive-maintenance-iot:latest .
docker run --rm -p 8000:8000 --name predictive-maintenance-demo predictive-maintenance-iot:latest
```

Or use `docker compose up --build`. Open <http://localhost:8000> and press `Ctrl+C` to stop.

## Troubleshooting

- **Python not found:** reinstall Python and enable **Add Python to PATH**, then reopen Command Prompt.
- **Port 8000 already in use:** stop the other program or run `.venv\Scripts\python.exe -m uvicorn app.main:app --port 8001` and open `http://127.0.0.1:8001`.
- **Chart unavailable:** internet access is needed for Chart.js; the table, controls, alerts and APIs continue working offline.
- **Reset demo data:** stop the server, delete `predictive_maintenance.db`, and start it again. The four machines are reseeded automatically.
- **Do not move individual files:** keep the extracted directory structure unchanged so templates and static files can be found.

For full technical documentation, read `README.md`. The academic submission report is `REPORT.md`.
