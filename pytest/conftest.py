"""
Pytest configuration and shared fixtures for Audio Processing System tests.
"""
import pytest
import json
import asyncio
import time
from unittest.mock import Mock, AsyncMock
from typing import Generator, Dict, Any

# Enable mock modules first (before other imports)
import mock_modules.mock_patch  # This will auto-patch missing modules

# Linux imports with fallbacks for compatibility
try:
    import aioredis
    HAS_REDIS = True
except ImportError:
    aioredis = Mock()
    HAS_REDIS = False

try:
    import aiormq
    HAS_RABBITMQ = True
except ImportError:
    aiormq = Mock()
    HAS_RABBITMQ = False

try:
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    HAS_SQLALCHEMY = True
except ImportError:
    create_engine = Mock()
    sessionmaker = Mock()
    HAS_SQLALCHEMY = False


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def sample_audio_data():
    """Sample audio data in JSON format."""
    return {
        "sensor_id": "sensor_001",
        "timestamp": "2024-01-15T10:30:00Z",
        "audio_data": "base64_encoded_audio_content",
        "sample_rate": 44100,
        "duration": 5.0,
        "format": "wav"
    }


@pytest.fixture
def sample_feature_type_a():
    """Sample Feature Type A data."""
    return {
        "feature_id": "feat_a_001",
        "sensor_id": "sensor_001",
        "timestamp": "2024-01-15T10:30:00Z",
        "features": {
            "mfcc": [1.2, 3.4, 5.6, 7.8],
            "spectral_centroid": 2500.5,
            "zero_crossing_rate": 0.15
        },
        "processing_time": 0.25
    }


@pytest.fixture
def sample_feature_type_b():
    """Sample Feature Type B data."""
    return {
        "feature_id": "feat_b_001",
        "source_feature": "feat_a_001",
        "timestamp": "2024-01-15T10:30:00Z",
        "enhanced_features": {
            "classification": "speech",
            "confidence": 0.95,
            "emotion": "neutral",
            "language": "en"
        },
        "processing_time": 0.18
    }


@pytest.fixture
def mock_rabbitmq_connection():
    """Mock RabbitMQ connection."""
    mock_connection = AsyncMock()
    mock_channel = AsyncMock()
    mock_connection.channel.return_value = mock_channel
    return mock_connection, mock_channel


@pytest.fixture
def mock_database_session():
    """Mock database session."""
    mock_session = Mock()
    mock_session.query.return_value = mock_session
    mock_session.filter.return_value = mock_session
    mock_session.all.return_value = []
    return mock_session


@pytest.fixture
def mock_redis_client():
    """Mock Redis client for caching."""
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = True
    mock_redis.delete.return_value = True
    return mock_redis


@pytest.fixture
def test_config():
    """Test configuration settings."""
    return {
        "rabbitmq": {
            "host": "localhost",
            "port": 5672,
            "username": "test_user",
            "password": "test_pass",
            "queues": {
                "audio_stream": "test_audio_queue",
                "features_stream": "test_features_queue"
            }
        },
        "database": {
            "url": "postgresql://test:test@localhost:5432/test_db"
        },
        "redis": {
            "host": "localhost",
            "port": 6379,
            "db": 1
        },
        "api": {
            "host": "0.0.0.0",
            "port": 8000,
            "cache_duration": 300  # 5 minutes
        }
    }


@pytest.fixture
def performance_metrics():
    """Performance metrics tracking."""
    return {
        "start_time": time.time(),
        "memory_usage": [],
        "cpu_usage": [],
        "processing_times": []
    }


class MockSensor:
    """Mock sensor for testing."""
    
    def __init__(self, sensor_id: str):
        self.sensor_id = sensor_id
        
    async def generate_audio_data(self) -> Dict[str, Any]:
        """Generate mock audio data."""
        return {
            "sensor_id": self.sensor_id,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "audio_data": "mock_audio_base64",
            "sample_rate": 44100,
            "duration": 1.0,
            "format": "wav"
        }


@pytest.fixture
def mock_sensor():
    """Mock sensor fixture."""
    return MockSensor("test_sensor_001")


# Pytest markers for test categorization
def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "functional: mark test as a functional test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as a performance test"
    )
    config.addinivalue_line(
        "markers", "security: mark test as a security test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    ) 