"""
Test utility functions and helper classes for the Audio Processing System tests.
"""
import asyncio
import json
import time
import uuid
from typing import Dict, Any, List, Optional
from unittest.mock import Mock, AsyncMock
import random
import string


class AudioDataGenerator:
    """Generate test audio data with various characteristics."""
    
    @staticmethod
    def generate_audio_message(
        sensor_id: Optional[str] = None,
        duration: float = 1.0,
        sample_rate: int = 44100,
        format: str = "wav"
    ) -> Dict[str, Any]:
        """Generate a realistic audio message."""
        return {
            "sensor_id": sensor_id or f"sensor_{random.randint(1, 100):03d}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "audio_data": AudioDataGenerator._generate_base64_audio(duration, sample_rate),
            "sample_rate": sample_rate,
            "duration": duration,
            "format": format,
            "checksum": AudioDataGenerator._generate_checksum()
        }
    
    @staticmethod
    def generate_feature_type_a(
        sensor_id: Optional[str] = None,
        feature_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate Feature Type A data."""
        return {
            "feature_id": feature_id or f"feat_a_{uuid.uuid4().hex[:8]}",
            "sensor_id": sensor_id or f"sensor_{random.randint(1, 100):03d}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "features": {
                "mfcc": [round(random.uniform(-10, 10), 2) for _ in range(13)],
                "spectral_centroid": round(random.uniform(1000, 5000), 2),
                "zero_crossing_rate": round(random.uniform(0, 1), 3),
                "spectral_rolloff": round(random.uniform(2000, 8000), 2),
                "chroma": [round(random.uniform(0, 1), 3) for _ in range(12)]
            },
            "processing_time": round(random.uniform(0.1, 0.5), 3)
        }
    
    @staticmethod
    def generate_feature_type_b(
        source_feature_id: Optional[str] = None,
        feature_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Generate Feature Type B data."""
        classifications = ["speech", "music", "noise", "silence"]
        emotions = ["neutral", "happy", "sad", "angry", "surprised"]
        languages = ["en", "es", "fr", "de", "it", "pt"]
        
        return {
            "feature_id": feature_id or f"feat_b_{uuid.uuid4().hex[:8]}",
            "source_feature": source_feature_id or f"feat_a_{uuid.uuid4().hex[:8]}",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "enhanced_features": {
                "classification": random.choice(classifications),
                "confidence": round(random.uniform(0.7, 0.99), 3),
                "emotion": random.choice(emotions),
                "language": random.choice(languages),
                "speaker_id": f"speaker_{random.randint(1, 50)}",
                "energy_level": round(random.uniform(0, 1), 3)
            },
            "processing_time": round(random.uniform(0.05, 0.3), 3)
        }
    
    @staticmethod
    def _generate_base64_audio(duration: float, sample_rate: int) -> str:
        """Generate mock base64 encoded audio data."""
        # Simulate audio data size calculation
        data_points = int(duration * sample_rate)
        # Create mock data (in reality this would be actual audio)
        mock_data = ''.join(random.choices(string.ascii_letters + string.digits, k=data_points // 1000))
        return mock_data
    
    @staticmethod
    def _generate_checksum() -> str:
        """Generate a mock checksum."""
        return ''.join(random.choices(string.hexdigits.lower(), k=32))


class PerformanceTracker:
    """Track performance metrics during tests."""
    
    def __init__(self):
        self.metrics = {
            "start_time": None,
            "end_time": None,
            "processing_times": [],
            "memory_usage": [],
            "cpu_usage": [],
            "throughput": 0
        }
    
    def start_tracking(self):
        """Start performance tracking."""
        self.metrics["start_time"] = time.time()
    
    def stop_tracking(self):
        """Stop performance tracking."""
        self.metrics["end_time"] = time.time()
    
    def record_processing_time(self, processing_time: float):
        """Record a processing time measurement."""
        self.metrics["processing_times"].append(processing_time)
    
    def record_memory_usage(self, memory_mb: float):
        """Record memory usage measurement."""
        self.metrics["memory_usage"].append(memory_mb)
    
    def record_cpu_usage(self, cpu_percent: float):
        """Record CPU usage measurement."""
        self.metrics["cpu_usage"].append(cpu_percent)
    
    def calculate_throughput(self, message_count: int) -> float:
        """Calculate throughput based on tracked time and message count."""
        if self.metrics["start_time"] and self.metrics["end_time"]:
            duration = self.metrics["end_time"] - self.metrics["start_time"]
            self.metrics["throughput"] = message_count / duration if duration > 0 else 0
        return self.metrics["throughput"]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get a summary of all tracked metrics."""
        summary = {
            "duration": self.metrics["end_time"] - self.metrics["start_time"] if self.metrics["start_time"] and self.metrics["end_time"] else 0,
            "throughput": self.metrics["throughput"]
        }
        
        if self.metrics["processing_times"]:
            summary["processing_time"] = {
                "avg": sum(self.metrics["processing_times"]) / len(self.metrics["processing_times"]),
                "min": min(self.metrics["processing_times"]),
                "max": max(self.metrics["processing_times"]),
                "count": len(self.metrics["processing_times"])
            }
        
        if self.metrics["memory_usage"]:
            summary["memory_usage"] = {
                "avg": sum(self.metrics["memory_usage"]) / len(self.metrics["memory_usage"]),
                "peak": max(self.metrics["memory_usage"]),
                "min": min(self.metrics["memory_usage"])
            }
        
        if self.metrics["cpu_usage"]:
            summary["cpu_usage"] = {
                "avg": sum(self.metrics["cpu_usage"]) / len(self.metrics["cpu_usage"]),
                "peak": max(self.metrics["cpu_usage"]),
                "min": min(self.metrics["cpu_usage"])
            }
        
        return summary


class MockServices:
    """Factory for creating mock services."""
    
    @staticmethod
    def create_mock_rabbitmq_connection():
        """Create a mock RabbitMQ connection."""
        mock_connection = AsyncMock()
        mock_channel = AsyncMock()
        mock_connection.channel.return_value = mock_channel
        
        # Configure common channel methods
        mock_channel.queue_declare = AsyncMock()
        mock_channel.exchange_declare = AsyncMock()
        mock_channel.queue_bind = AsyncMock()
        mock_channel.basic_publish = AsyncMock()
        mock_channel.basic_consume = AsyncMock()
        mock_channel.basic_qos = AsyncMock()
        mock_channel.basic_cancel = AsyncMock()
        
        return mock_connection, mock_channel
    
    @staticmethod
    def create_mock_database_session():
        """Create a mock database session."""
        mock_session = Mock()
        mock_query = Mock()
        
        # Configure query chain
        mock_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        mock_query.first.return_value = None
        mock_query.count.return_value = 0
        
        # Configure session methods
        mock_session.add = Mock()
        mock_session.commit = Mock()
        mock_session.rollback = Mock()
        mock_session.close = Mock()
        mock_session.flush = Mock()
        
        return mock_session
    
    @staticmethod
    def create_mock_redis_client():
        """Create a mock Redis client."""
        mock_redis = AsyncMock()
        
        # Configure Redis methods
        mock_redis.get = AsyncMock(return_value=None)
        mock_redis.set = AsyncMock(return_value=True)
        mock_redis.delete = AsyncMock(return_value=True)
        mock_redis.exists = AsyncMock(return_value=False)
        mock_redis.expire = AsyncMock(return_value=True)
        mock_redis.ttl = AsyncMock(return_value=-1)
        mock_redis.keys = AsyncMock(return_value=[])
        mock_redis.flushdb = AsyncMock(return_value=True)
        
        return mock_redis
    
    @staticmethod
    def create_mock_kubernetes_client():
        """Create a mock Kubernetes client."""
        mock_k8s = Mock()
        
        # Mock pods
        mock_pod = Mock()
        mock_pod.metadata.name = "test-pod"
        mock_pod.status.phase = "Running"
        mock_pod.status.pod_ip = "10.0.1.100"
        
        # Mock services
        mock_service = Mock()
        mock_service.metadata.name = "test-service"
        mock_service.spec.cluster_ip = "10.0.1.1"
        
        # Configure client methods
        mock_k8s.list_namespaced_pod.return_value.items = [mock_pod]
        mock_k8s.list_namespaced_service.return_value.items = [mock_service]
        mock_k8s.read_namespaced_pod.return_value = mock_pod
        
        return mock_k8s


class TestDataValidator:
    """Validate test data and results."""
    
    @staticmethod
    def validate_audio_message(message: Dict[str, Any]) -> bool:
        """Validate audio message structure."""
        required_fields = ["sensor_id", "timestamp", "audio_data", "sample_rate", "duration", "format"]
        return all(field in message for field in required_fields)
    
    @staticmethod
    def validate_feature_type_a(feature: Dict[str, Any]) -> bool:
        """Validate Feature Type A structure."""
        required_fields = ["feature_id", "sensor_id", "timestamp", "features", "processing_time"]
        if not all(field in feature for field in required_fields):
            return False
        
        # Validate features structure
        features = feature["features"]
        required_feature_fields = ["mfcc", "spectral_centroid", "zero_crossing_rate"]
        return all(field in features for field in required_feature_fields)
    
    @staticmethod
    def validate_feature_type_b(feature: Dict[str, Any]) -> bool:
        """Validate Feature Type B structure."""
        required_fields = ["feature_id", "source_feature", "timestamp", "enhanced_features", "processing_time"]
        if not all(field in feature for field in required_fields):
            return False
        
        # Validate enhanced features structure
        enhanced = feature["enhanced_features"]
        required_enhanced_fields = ["classification", "confidence"]
        return all(field in enhanced for field in required_enhanced_fields)
    
    @staticmethod
    def validate_performance_metrics(metrics: Dict[str, Any], thresholds: Dict[str, float]) -> List[str]:
        """Validate performance metrics against thresholds."""
        violations = []
        
        for metric, threshold in thresholds.items():
            if metric in metrics:
                if isinstance(metrics[metric], dict) and "avg" in metrics[metric]:
                    value = metrics[metric]["avg"]
                else:
                    value = metrics[metric]
                
                if value > threshold:
                    violations.append(f"{metric}: {value} exceeds threshold {threshold}")
        
        return violations


class AsyncTestHelpers:
    """Helper functions for async testing."""
    
    @staticmethod
    async def wait_for_condition(condition_func, timeout: float = 5.0, interval: float = 0.1) -> bool:
        """Wait for a condition to become true."""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if await condition_func() if asyncio.iscoroutinefunction(condition_func) else condition_func():
                return True
            await asyncio.sleep(interval)
        
        return False
    
    @staticmethod
    async def simulate_processing_delay(min_delay: float = 0.01, max_delay: float = 0.1):
        """Simulate realistic processing delay."""
        delay = random.uniform(min_delay, max_delay)
        await asyncio.sleep(delay)
    
    @staticmethod
    async def run_concurrent_tasks(tasks: List, max_concurrency: int = 10) -> List:
        """Run tasks with controlled concurrency."""
        semaphore = asyncio.Semaphore(max_concurrency)
        
        async def run_with_semaphore(task):
            async with semaphore:
                return await task
        
        return await asyncio.gather(*[run_with_semaphore(task) for task in tasks])


def assert_timing(func, max_duration: float):
    """Decorator to assert function execution time."""
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time
        
        assert duration <= max_duration, f"Function took {duration}s, expected <= {max_duration}s"
        return result
    return wrapper


async def assert_async_timing(func, max_duration: float):
    """Async version of timing assertion."""
    start_time = time.time()
    result = await func
    duration = time.time() - start_time
    
    assert duration <= max_duration, f"Function took {duration}s, expected <= {max_duration}s"
    return result 