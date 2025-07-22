"""
Mock sensors module for testing
"""
from unittest.mock import Mock
import time
import random


class SensorClient:
    """Mock sensor client"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.is_connected = False
        self.sensor_data = {}
    
    async def connect(self):
        """Connect to sensor"""
        self.is_connected = True
        return True
    
    def disconnect(self):
        """Disconnect from sensor"""
        self.is_connected = False
    
    async def send_audio_data(self, audio_data, metadata=None):
        """Send audio data to processing pipeline"""
        if not self.is_connected:
            raise ConnectionError("Sensor not connected")
        
        # Simulate async network transmission
        import asyncio
        await asyncio.sleep(0.001)
        
        return {
            "sensor_id": metadata.get("sensor_id", "default_sensor") if metadata else "default_sensor",
            "audio_id": f"audio_{int(time.time())}",
            "status": "sent",
            "timestamp": time.time(),
            "data_size": len(audio_data) if audio_data else 0
        }
    
    def get_sensor_status(self):
        """Get sensor status"""
        return {
            "connected": self.is_connected,
            "last_heartbeat": time.time(),
            "sensor_id": "mock_sensor_001",
            "battery_level": random.uniform(20, 100)
        }


# Mock sensor_client module
class sensor_client:
    """Mock sensors.sensor_client module"""
    SensorClient = SensorClient 