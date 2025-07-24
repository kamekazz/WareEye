# WareEye

WareEye is a basic barcode scanning system made up of two Python applications:

* **Server** – a small Flask app that stores scan records and provides a simple
  web interface to browse them.
* **Client** – a webcam utility that detects barcodes or QR codes and sends the
  results to the server.

## Running the server

```bash
cd Server
pip install -r requirements.txt
python app.py
```

The server listens on port `5000` by default and creates an `app.db` SQLite
database in the `Server` directory.

## Running the client

```bash
cd Client
pip install -r requirements.txt
python client.py
```

The client prompts for camera information, opens the webcam or RTSP stream and
continually scans frames for barcodes. Detected values are sent to the server.

## How you can help

WareEye is very much a work in progress. We would love help with:

* improving detection accuracy and performance
* polishing the web UI and dashboard
* packaging the project (e.g. Docker, Windows binaries)

See [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get involved.
