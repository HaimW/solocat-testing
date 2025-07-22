"""
Mock monitoring module for testing
"""
from unittest.mock import Mock
import time
import random


class SystemMonitor:
    """Mock system monitor"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = []
        self.is_monitoring = False
    
    def start_monitoring(self):
        """Start system monitoring"""
        self.is_monitoring = True
        return True
    
    def stop_monitoring(self):
        """Stop system monitoring"""
        self.is_monitoring = False
    
    def collect_metrics(self):
        """Collect system metrics"""
        metrics = {
            "timestamp": time.time(),
            "cpu_usage": random.uniform(10, 80),
            "memory_usage": random.uniform(20, 90),
            "disk_usage": random.uniform(30, 85),
            "network_io": {
                "bytes_sent": random.randint(1000, 10000),
                "bytes_received": random.randint(1000, 10000)
            },
            "application_metrics": {
                "active_connections": random.randint(10, 100),
                "request_rate": random.uniform(50, 200),
                "error_rate": random.uniform(0, 5)
            }
        }
        
        self.metrics[metrics["timestamp"]] = metrics
        return metrics
    
    def check_thresholds(self, metrics):
        """Check if metrics exceed thresholds"""
        alerts = []
        
        if metrics["cpu_usage"] > 80:
            alerts.append({
                "type": "cpu_high",
                "value": metrics["cpu_usage"],
                "threshold": 80,
                "severity": "warning"
            })
        
        if metrics["memory_usage"] > 85:
            alerts.append({
                "type": "memory_high", 
                "value": metrics["memory_usage"],
                "threshold": 85,
                "severity": "critical"
            })
        
        self.alerts.extend(alerts)
        return alerts
    
    def get_health_status(self):
        """Get overall system health status"""
        if not self.metrics:
            return "unknown"
        
        latest_metrics = list(self.metrics.values())[-1]
        
        if latest_metrics["cpu_usage"] > 90 or latest_metrics["memory_usage"] > 95:
            return "critical"
        elif latest_metrics["cpu_usage"] > 70 or latest_metrics["memory_usage"] > 80:
            return "warning"
        else:
            return "healthy"


class MetricsCollector:
    """Mock metrics collector"""
    
    def __init__(self):
        self.metrics_store = {}
        self.collection_interval = 30  # seconds
    
    def collect_application_metrics(self):
        """Collect application-specific metrics"""
        return {
            "audio_processing": {
                "messages_processed": random.randint(100, 1000),
                "average_processing_time": random.uniform(0.1, 2.0),
                "failed_processes": random.randint(0, 10)
            },
            "message_broker": {
                "messages_published": random.randint(500, 2000),
                "messages_consumed": random.randint(480, 1980),
                "queue_depth": random.randint(0, 50)
            },
            "database": {
                "queries_executed": random.randint(200, 800),
                "average_query_time": random.uniform(0.05, 0.5),
                "connection_pool_usage": random.uniform(10, 80)
            }
        }
    
    def store_metrics(self, metrics):
        """Store metrics for later analysis"""
        timestamp = time.time()
        self.metrics_store[timestamp] = metrics
        return timestamp
    
    def increment_messages_processed(self, algorithm_name):
        """Increment messages processed counter"""
        if algorithm_name not in self.metrics_store:
            self.metrics_store[algorithm_name] = {"messages_processed": 0}
        self.metrics_store[algorithm_name]["messages_processed"] += 1

    def record_processing_time(self, *args, **kwargs):
        self.last_processing_time = args[0] if args else None
        return True

    def record_queue_size(self, queue_name, size):
        self.last_queue_size = (queue_name, size)
        return True


class MetricsClient:
    """Mock metrics client"""
    
    def __init__(self):
        self.metrics = {}
    
    def get_system_metrics(self):
        """Get system metrics"""
        return {
            "cpu_usage": random.uniform(10, 80),
            "memory_usage": random.uniform(20, 90),
            "disk_usage": random.uniform(30, 85)
        }


# Mock metrics module
class metrics:
    """Mock monitoring.metrics module"""
    MetricsCollector = MetricsCollector
    MetricsClient = MetricsClient 