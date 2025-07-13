# WareEye

WareEye provides a simple Flask interface that streams video from your local
webcam and logs any barcodes detected in real time.

## Setup

Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

No additional configuration is required; the app uses webcam device `0`. The
requirements include `pyzbar` for decoding barcodes.

## Running the App

Start the services using the provided script:

```bash
./start-services.sh
```

Then open your browser and navigate to `http://localhost:5000/` to view the live stream.

## Project Structure

- `app/routes/` – Flask blueprints with HTTP endpoints
- `app/services/` – business logic modules with no Flask dependencies
- `app/models/` – data class definitions
- `templates/` – Jinja2 templates organized by feature
- `static/` – static assets (Tailwind via CDN)

