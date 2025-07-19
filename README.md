# WareEye

Simple client and server utilities for barcode and QR code detection.

## Installation

Install dependencies for the client:

```bash
pip install -r Client/requirements.txt
```

## Usage

Run the camera stream script. By default it looks for a YOLO model named `barcode_yolo.pt` in the current working directory. You can specify a different path either via a command line argument or environment variable.

```bash
# Using a command line argument
python Client/security_camera_stream.py --model-path /path/to/barcode_yolo.pt

# Or via environment variable
export YOLO_MODEL_PATH=/path/to/barcode_yolo.pt
python Client/security_camera_stream.py
```
