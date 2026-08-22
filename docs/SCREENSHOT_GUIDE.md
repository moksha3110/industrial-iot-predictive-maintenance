# Screenshot Guide

Screenshots must be genuine. Start the app with `uvicorn app.main:app --reload`, then capture up to six images into `docs/screenshots/`:

1. `01-dashboard.png`: open `http://localhost:8000`; include summary cards, machine table, chart and controls. Place in Report section 1.
2. `02-swagger.png`: open `http://localhost:8000/docs`; expand the simulator endpoints. Place in section 1 or 2.
3. `03-sensor-failure.png`: click **Fail temperature** and capture the Sensor Failure badge plus critical Owner Alert. Place in section 5.
4. `04-tests.png`: run `pytest -v` and capture the passing result. Place in section 4.
5. `05-docker.png`: run the Docker build/container and capture `docker ps` plus the `/health` response. Place in section 2.
6. `06-architecture.png`: render the Mermaid AWS diagram from `docs/architecture.md` in GitHub/VS Code and capture it. Place in section 1.

This environment did not provide a browser screenshot facility, so no image was fabricated.
