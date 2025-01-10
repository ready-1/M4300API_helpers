"""Device info helper module.

This module provides functionality to retrieve device information from an M4300
switch including hardware details, operational status, and sensor readings.
"""

from .device_info import get_device_info, DeviceInfo, TemperatureSensor

__all__ = ['get_device_info', 'DeviceInfo', 'TemperatureSensor']
