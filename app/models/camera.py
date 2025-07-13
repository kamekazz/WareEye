from dataclasses import dataclass
from typing import Optional


def build_url(ip: str, password: str) -> str:
    """Construct the RTSP URL for the camera."""
    return f"rtsp://admin:{password}@{ip}:554/h264Preview_01_main"

@dataclass
class Camera:
    id: Optional[int]
    name: str
    zone: str
    ip_address: str
    password: str
    scanning: bool = False
    url: str = ""

    def __post_init__(self) -> None:
        # Automatically build the stream URL based on IP and password
        self.url = build_url(self.ip_address, self.password)
