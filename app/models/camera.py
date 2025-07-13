from dataclasses import dataclass
from typing import Optional

@dataclass
class Camera:
    id: Optional[int]
    name: str
    zone: str
    ip_address: str
    url: str
    password: str
    scanning: bool = False
