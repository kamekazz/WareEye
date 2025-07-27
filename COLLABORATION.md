# Collaboration Guide

This document walks new contributors through getting WareEye running locally.

## Running the Server

```bash
cd Server
pip install -r requirements.txt
python app.py
```

## Running a Camera

WareEye provides two camera client folders:

* `security-camera-server/` – for general surveillance and pallet tracking.
* `dock-door-server/` – for barcode validation at dock doors.

Pick one and run:

```bash
cd security-camera-server  # or dock-door-server
pip install -r requirements.txt
python client.py
```

## Sample Data

Use the `EX/` folder to load sample images or CSVs and simulate barcode scans without a live camera.

## Setup Video

Need a quick walkthrough? Watch <https://youtu.be/b42MZwiKGsM?si=vZiyP3EjoFAV4in2>.
