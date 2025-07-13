# WareEye

WareEye provides a Flask interface that connects to a Reolink camera and performs
real-time pallet barcode detection and tracking.

## Setup

Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

Create a `.env` file with your camera credentials:

```ini
CAMERA_IP=192.168.1.163
CAMERA_PASS=your_password
# Optional: tweak RTSP parameters passed to OpenCV
RTSP_OPTIONS=rtsp_transport=tcp
```

## Running the App

Start the services using the provided script:

```bash
./start-services.sh
```

Then open your browser and navigate to `http://localhost:5000/` to view the live stream.

The `/healthz` endpoint exposes a basic health check for the Flask application and detection thread.

## Project Structure

- `app/routes/` – Flask blueprints with HTTP endpoints
- `app/services/` – business logic modules with no Flask dependencies
- `app/models/` – data class definitions
- `templates/` – Jinja2 templates organized by feature
- `static/` – static assets (Tailwind via CDN)

