# WareEye

## Requirements

- Python 3.12 or later.
- Dependencies listed in `Client/requirements.txt` and `Server/requirements.txt`.

## Installation

Create a virtual environment and install the required packages:

```bash
pip install -r Client/requirements.txt
pip install -r Server/requirements.txt
```

## YOLO Barcode Model

The client optionally uses a YOLO model to improve barcode detection.
Download or train a model named `barcode_yolo.pt` and place it in the
repository root. You can train your own model using [Ultralytics YOLO](https://docs.ultralytics.com/) on a dataset of barcode images or use a pre-trained model from the project's release page.

## Running

Start the Flask server:

```bash
python Server/app.py
```

Then run the webcam client:

```bash
python Client/security_camera_stream.py
```

The client will attempt to load `barcode_yolo.pt` if it exists and use
it to detect barcodes in the video stream.
