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

## Capture Pipeline

Frame acquisition now runs in a dedicated thread to minimize latency. The camera
attempts to lock exposure, white balance and focus where supported. Adjust these
parameters in `webcam_service.py` if your hardware requires different values.
Frames are converted to grayscale and passed through CLAHE (adaptive histogram
equalization) before barcode decoding to improve contrast and reliability under
varying lighting conditions. Decoding is handled by a small worker pool so the
capture loop never blocks. Frames are skipped when the decode queue is full,
keeping the system responsive even if decoding is slower than the camera frame
rate.

## Project Structure

- `app/routes/` – Flask blueprints with HTTP endpoints
- `app/services/` – business logic modules with no Flask dependencies
- `app/models/` – data class definitions
- `templates/` – Jinja2 templates organized by feature
- `static/` – static assets (Tailwind via CDN)

