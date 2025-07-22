"""
Mock load_balancing module for testing
"""
from unittest.mock import Mock
import time
import random


class AlgorithmLoadBalancer:
    """Mock algorithm load balancer"""
    
    def __init__(self, algorithms=None):
        self.algorithms = algorithms or ["algorithm_a", "algorithm_b"]
        self.algorithm_instances = {}
        self.load_metrics = {}
        self.current_index = 0
        self.consumers = {}
    
    def register_algorithm(self, algorithm_name, instance):
        """Register an algorithm instance"""
        self.algorithm_instances[algorithm_name] = instance
        self.load_metrics[algorithm_name] = {
            "requests": 0,
            "avg_response_time": 0.0,
            "cpu_usage": 0.0,
            "memory_usage": 0.0
        }
    
    def register_consumer(self, consumer_id, consumer_instance=None):
        """Register a consumer"""
        if consumer_id not in self.consumers:
            self.consumers[consumer_id] = {
                'id': consumer_id,
                'health': 'healthy',
                'last_seen': time.time(),
                'message_count': 0,
                'instance': consumer_instance
            }
        return True
    
    def register_consumers(self, consumer_list):
        """Register multiple consumers"""
        for consumer in consumer_list:
            if isinstance(consumer, str):
                self.register_consumer(consumer)
            else:
                self.register_consumer(consumer['id'], consumer)
    
    def get_next_algorithm(self):
        """Get next algorithm using round-robin"""
        if not self.algorithms:
            return None
        
        algorithm = self.algorithms[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.algorithms)
        return algorithm
    
    def get_optimal_algorithm(self):
        """Get optimal algorithm based on load"""
        if not self.load_metrics:
            return self.get_next_algorithm()
        
        # Find algorithm with lowest load
        min_load = float('inf')
        optimal_algorithm = None
        
        for algorithm, metrics in self.load_metrics.items():
            load = metrics["cpu_usage"] + metrics["memory_usage"]
            if load < min_load:
                min_load = load
                optimal_algorithm = algorithm
        
        return optimal_algorithm or self.get_next_algorithm()
    
    def update_metrics(self, algorithm_name, response_time, cpu_usage=None, memory_usage=None):
        """Update algorithm metrics"""
        if algorithm_name in self.load_metrics:
            metrics = self.load_metrics[algorithm_name]
            metrics["requests"] += 1
            metrics["avg_response_time"] = (
                (metrics["avg_response_time"] * (metrics["requests"] - 1) + response_time) / 
                metrics["requests"]
            )
            if cpu_usage is not None:
                metrics["cpu_usage"] = cpu_usage
            if memory_usage is not None:
                metrics["memory_usage"] = memory_usage
    
    def scale_algorithm(self, algorithm_name, instances):
        """Scale algorithm instances"""
        return {
            "algorithm": algorithm_name,
            "instances": instances,
            "status": "scaled",
            "timestamp": time.time()
        }


class PodManager:
    """Mock pod manager"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.pods = {}
        self.failed_pods = []
    
    def restart_pod(self, pod_name):
        """Restart a pod"""
        self.failed_pods.append(pod_name)
        return {
            "pod_name": pod_name,
            "status": "restarted",
            "timestamp": time.time()
        }
    
    def get_pod_status(self, pod_name):
        """Get pod status"""
        return {
            "name": pod_name,
            "status": "running" if pod_name not in self.failed_pods else "failed",
            "ready": pod_name not in self.failed_pods,
            "restart_count": 1 if pod_name in self.failed_pods else 0
        }
    
    def simulate_pod_failure(self, pod_name):
        """Simulate pod failure"""
        self.failed_pods.append(pod_name)
        return {"pod_name": pod_name, "status": "failed"}
    
    def get_next_healthy_pod(self):
        """Get next healthy pod"""
        healthy_pods = [name for name in self.pods.keys() if name not in self.failed_pods]
        if healthy_pods:
            return healthy_pods[0]
        return None


# Mock pod_manager module
class pod_manager:
    """Mock load_balancing.pod_manager module"""
    PodManager = PodManager 