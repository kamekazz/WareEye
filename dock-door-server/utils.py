# -*- coding: utf-8 -*-
"""Utility helpers for the camera client."""

from __future__ import annotations

import os
import time
import urllib.request
from typing import Dict, Optional

import requests


BASE_WECHAT_URL = (
    "https://raw.githubusercontent.com/WeChatCV/opencv_3rdparty/wechat_qrcode/"
)


def ensure_wechat_models(det_proto: str, det_model: str, sr_proto: str, sr_model: str) -> None:
    """Download WeChatQRCode models if missing."""
    for path in [det_proto, det_model, sr_proto, sr_model]:
        if not os.path.exists(path):
            url = BASE_WECHAT_URL + os.path.basename(path)
            try:
                print(f"Downloading {url} ...")
                urllib.request.urlretrieve(url, path)
            except Exception as exc:  # pragma: no cover - network issues
                print(f"Failed to download {url}: {exc}")


def parse_camera_info(info_path: str) -> Dict[str, str]:
    """Parse camera metadata from ``info_path``."""
    info: Dict[str, str] = {}
    if os.path.exists(info_path):
        with open(info_path, "r", encoding="utf-8") as f:
            for line in f:
                if ":" in line:
                    key, value = line.strip().split(":", 1)
                    info[key.strip()] = value.strip()
    return info


def send_barcode(data: str, info: Dict[str, str], last: Dict[str, float]) -> Optional[bool]:
    """Send scanned ``data`` to the server with rate limiting.

    Returns the validation result if provided by the server.
    """
    if not data:
        return None

    now = time.time()
    if now - last.get(data, 0) < 2:
        return None

    payload = {
        "barcode": data,
        "camera_name": info.get("Camera Name", ""),
        "area": info.get("Camera Area", ""),
        "camera_type": info.get("Camera Type", ""),
        "client_ip": info.get("Client IP", ""),
        "camera_url": info.get("Camera URL", ""),
    }
    url = f"http://{info.get('Server IP', 'localhost')}:{info.get('Port', '5000')}/api/scan"

    try:
        resp = requests.post(url, json=payload, timeout=2)
        if resp.ok:
            try:
                result = resp.json()
                if "valid" in result:
                    last[data] = now
                    return bool(result["valid"])
            except Exception:
                pass
    except Exception as exc:  # pragma: no cover - network or server errors
        print(f"Failed to send barcode data: {exc}")

    last[data] = now
    return None
