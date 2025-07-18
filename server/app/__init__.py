"""WareEye application package."""

# Re-export commonly used services for convenience
from .services import camera_service, barcode_service  # noqa: F401

__all__ = ["camera_service", "barcode_service"]
