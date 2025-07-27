# -*- coding: utf-8 -*-
"""Entry point for the camera client."""

from __future__ import annotations

import argparse
import os
from typing import Dict

import cv2

import utils
from stream import run_stream


def main() -> None:
    """Start the webcam stream and scan for barcodes or QR codes."""
    parser = argparse.ArgumentParser(
        description="Start the webcam stream and scan for barcodes or QR codes."
    )
    parser.add_argument(
        "--model-path",
        default=os.getenv("YOLO_MODEL_PATH", "barcode_yolo.pt"),
        help="Path to the YOLO model for barcode detection",
    )
    parser.add_argument(
        "--wechat-det-prototxt",
        default=os.getenv("WECHAT_DET_PROTOTXT", "detect.prototxt"),
        help="Path to WeChat QRCode detection prototxt file",
    )
    parser.add_argument(
        "--wechat-det-model",
        default=os.getenv("WECHAT_DET_MODEL", "detect.caffemodel"),
        help="Path to WeChat QRCode detection model file",
    )
    parser.add_argument(
        "--wechat-sr-prototxt",
        default=os.getenv("WECHAT_SR_PROTOTXT", "sr.prototxt"),
        help="Path to WeChat QRCode super resolution prototxt file",
    )
    parser.add_argument(
        "--wechat-sr-model",
        default=os.getenv("WECHAT_SR_MODEL", "sr.caffemodel"),
        help="Path to WeChat QRCode super resolution model file",
    )

    args = parser.parse_args()

    info_path = os.path.join(os.path.dirname(__file__), "camera_info.txt")
    prev_info = utils.parse_camera_info(info_path)

    camera_name = input(
        f"Camera Name [{prev_info.get('Camera Name', '')}]: "
    ) or prev_info.get("Camera Name", "")
    camera_area = input(
        f"Camera Area [{prev_info.get('Camera Area', '')}]: "
    ) or prev_info.get("Camera Area", "")
    camera_type = input(
        f"Camera Type [{prev_info.get('Camera Type', '')}]: "
    ) or prev_info.get("Camera Type", "")
    server_IP = input(
        f"Server IP [{prev_info.get('Server IP', '')}]: "
    ) or prev_info.get("Server IP", "")
    port = input(f"Port [{prev_info.get('Port', '')}]: ") or prev_info.get("Port", "")
    client_ip = input(
        f"Client IP [{prev_info.get('Client IP', '')}]: "
    ) or prev_info.get("Client IP", "")
    camera_url_input = input(
        f"Camera URL [{prev_info.get('Camera URL', '')}]: "
    ) or prev_info.get("Camera URL", "")

    with open(info_path, "w", encoding="utf-8") as f:
        f.write(f"Camera Name: {camera_name}\n")
        f.write(f"Camera Area: {camera_area}\n")
        f.write(f"Camera Type: {camera_type}\n")
        f.write(f"Server IP: {server_IP}\n")
        f.write(f"Port: {port}\n")
        f.write(f"Client IP: {client_ip}\n")
        f.write(f"Camera URL: {camera_url_input}\n")

    print(f"Camera info saved to {info_path}")

    camera_info = utils.parse_camera_info(info_path)

    utils.ensure_wechat_models(
        args.wechat_det_prototxt,
        args.wechat_det_model,
        args.wechat_sr_prototxt,
        args.wechat_sr_model,
    )
    camera_url = camera_info.get("Camera URL", "0")
    cam_source = int(camera_url) if camera_url.isdigit() else camera_url
    cap = cv2.VideoCapture(cam_source)
    if not cap.isOpened():
        print(f"Cannot open camera {camera_url}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)

    run_stream(cap, camera_info, args)


if __name__ == "__main__":
    main()
