# WareEye

WareEye provides a simple Flask interface for managing IP cameras and logging
any barcodes detected in real time.

## Setup

Install the required dependencies using `pip`:

```bash
pip install -r requirements.txt
```

The requirements include `pyzbar` for decoding barcodes.

## Running the App

Start the services using the provided script:

```bash
./start-services.sh
```

Then open your browser and navigate to `http://localhost:5000/cameras` to manage your cameras.


## Project Structure

- `app/routes/` – Flask blueprints with HTTP endpoints
- `app/services/` – business logic modules with no Flask dependencies
- `app/models/` – data class definitions
- `templates/` – Jinja2 templates organized by feature
- `static/` – static assets (Tailwind via CDN)

