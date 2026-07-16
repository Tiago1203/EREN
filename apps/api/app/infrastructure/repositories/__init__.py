"""Repository implementations for all bounded contexts.

These implementations satisfy the abstract repository interfaces
defined in the domain layer.
"""

from app.domain.device.repository import SQLAlchemyDeviceRepository as DeviceRepositoryImpl

__all__ = [
    "DeviceRepositoryImpl",
]
