# WareEye

WareEye now separates the server that stores barcode scans from the client that
performs the actual decoding.  The Flask server only receives scan messages and
provides a web interface for viewing cameras and stored scans.

## Setup

Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

The server no longer performs barcode decoding so only the minimal
dependencies are required.

## Running the App

Start the services using the provided script:

```bash
./start-services.sh
```


Then open your browser and navigate to `http://localhost:5000/cameras` to manage your cameras.

### Client Scanner

The `client/` directory contains a standalone script that connects to a camera,
decodes barcodes and posts them to the server using `/api/scans`. Install its
dependencies with:

```bash
pip install -r client/requirements.txt
```

Run the scanner by providing the camera RTSP URL:

```bash
python client/scanner.py --camera-url rtsp://<ip>/path
```


## Project Structure

- `app/routes/` – Flask blueprints with HTTP endpoints
- `app/services/` – business logic modules with no Flask dependencies
- `app/models/` – data class definitions
- `templates/` – Jinja2 templates organized by feature
- `static/` – static assets (Tailwind via CDN)
- `client/` – standalone barcode scanner that posts results to the server

