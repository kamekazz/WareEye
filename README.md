
# WareEye

WareEye is a real-time pallet tracking and validation system built for
warehouse environments. It combines video-based barcode scanning with
centralized logging and a simple dashboard for visibility and control.

## What It Does

WareEye consists of two Python components:

* **Server** – a lightweight Flask app that stores barcode scans and provides a
  simple web interface to review scan records.
* **Client** – a video stream scanner that detects barcodes (e.g. QR, Code128)
  via webcam or RTSP and sends scan results to the server.

## Core Features

### 📦 Pallet Tracking
Detects and tracks barcoded pallets as they move throughout the warehouse using
live camera feeds.

### 🚚 Load Validation
Automatically validates that the correct pallets are being loaded into outbound
trucks—without requiring the driver to leave the vehicle. This is especially
useful when handling expensive or sensitive shipments.

## Running the Server

```bash
cd Server
pip install -r requirements.txt
python app.py
```

By default the server runs on port `5000` and stores scans in `app.db`
(SQLite).

## Running the Client

```bash
cd Client
pip install -r requirements.txt
python client.py
```

The client opens a webcam or RTSP stream and continuously scans video frames
for barcodes. Each detected code is sent to the server with a timestamp.

## How You Can Help

WareEye is a work in progress, and we're looking for collaborators! You can
help us improve:

* 📈 Detection accuracy and frame processing speed
* 🎨 The UI and scan dashboard
* 📦 Packaging for Docker, Windows, and embedded devices (e.g. Raspberry Pi)

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get involved!
