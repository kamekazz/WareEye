
# WareEye

WareEye is a real-time pallet tracking and validation system built for
warehouse environments. It combines video-based barcode scanning with
centralized logging and a simple dashboard for visibility and control.

## What It Does

WareEye is organized into three main folders:

* **Server** – a lightweight Flask app that stores barcode scans and provides a
  simple web interface to review scan records.
* **security-camera-server** – camera client for general surveillance and
  pallet tracking around the warehouse.
* **dock-door-server** – camera client focused on dock door barcode
  validation.

### Setup Video

Prefer a walkthrough? Check out our quick start video:
<https://youtu.be/b42MZwiKGsM?si=vZiyP3EjoFAV4in2>

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
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python app.py
```

By default the server runs on port `5000` and stores scans in `app.db`
(SQLite).

### Building Static Assets with npm

The web interface relies on Tailwind CSS. Inside the `Server` folder you can
install the Node dependencies and build the stylesheet:

```bash
cd Server
npm install
npm run build
```

Run `npm run build` again whenever you modify `tailwind.css`.

## Running the Camera Clients

The project ships with two camera modules:

* `security-camera-server/` – for general warehouse surveillance and pallet tracking.
* `dock-door-server/` – for barcode validation at dock doors.

```bash
# pick one of the camera folders
cd security-camera-server  # or dock-door-server
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python client.py
```

Each camera module opens a webcam or RTSP stream and continuously scans frames
for barcodes. Detected codes are sent to the server with a timestamp.

### Example Data (EX/)

Use the `EX/` folder to try WareEye without a live camera. It contains sample
images and CSVs so you can simulate barcode scans and test the pipeline end to
end.

## How You Can Help

WareEye is a work in progress, and we're looking for collaborators! You can
help us improve:

* 📈 Detection accuracy and frame processing speed
* 🎨 The UI and scan dashboard
* 📦 Packaging for Docker, Windows, and embedded devices (e.g. Raspberry Pi)

See [CONTRIBUTING.md](CONTRIBUTING.md) for how to get involved!
