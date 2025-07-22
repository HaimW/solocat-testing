"""
Mock prometheus_client module for testing
"""
from unittest.mock import Mock
import time


class Counter:
    """Mock Prometheus Counter metric"""
    
    def __init__(self, name, documentation, labelnames=None, registry=None):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames or []
        self.registry = registry
        self._value = 0
        self._labels = {}
    
    def inc(self, amount=1):
        """Increment counter"""
        self._value += amount
    
    def labels(self, **kwargs):
        """Return labeled metric"""
        label_key = tuple(sorted(kwargs.items()))
        if label_key not in self._labels:
            self._labels[label_key] = Mock()
            self._labels[label_key].inc = Mock()
        return self._labels[label_key]


class Gauge:
    """Mock Prometheus Gauge metric"""
    
    def __init__(self, name, documentation, labelnames=None, registry=None):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames or []
        self.registry = registry
        self._value = 0
        self._labels = {}
    
    def set(self, value):
        """Set gauge value"""
        self._value = value
    
    def inc(self, amount=1):
        """Increment gauge"""
        self._value += amount
    
    def dec(self, amount=1):
        """Decrement gauge"""
        self._value -= amount
    
    def labels(self, **kwargs):
        """Return labeled metric"""
        label_key = tuple(sorted(kwargs.items()))
        if label_key not in self._labels:
            self._labels[label_key] = Mock()
            self._labels[label_key].set = Mock()
            self._labels[label_key].inc = Mock()
            self._labels[label_key].dec = Mock()
        return self._labels[label_key]


class Histogram:
    """Mock Prometheus Histogram metric"""
    
    def __init__(self, name, documentation, labelnames=None, buckets=None, registry=None):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames or []
        self.buckets = buckets or (.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
        self.registry = registry
        self._labels = {}
    
    def time(self):
        """Return timer context manager"""
        return HistogramTimer()
    
    def observe(self, amount):
        """Observe a value"""
        pass
    
    def labels(self, **kwargs):
        """Return labeled metric"""
        label_key = tuple(sorted(kwargs.items()))
        if label_key not in self._labels:
            self._labels[label_key] = Mock()
            self._labels[label_key].time = Mock(return_value=HistogramTimer())
            self._labels[label_key].observe = Mock()
        return self._labels[label_key]


class HistogramTimer:
    """Mock histogram timer context manager"""
    
    def __init__(self):
        self.start_time = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


class CollectorRegistry:
    """Mock Prometheus Collector Registry"""
    
    def __init__(self):
        self.collectors = {}
    
    def register(self, collector):
        """Register a collector"""
        self.collectors[collector.name] = collector
    
    def unregister(self, collector):
        """Unregister a collector"""
        if collector.name in self.collectors:
            del self.collectors[collector.name]


class REGISTRY:
    """Mock default registry"""
    def __init__(self):
        pass


# Default registry instance
REGISTRY = CollectorRegistry()


def generate_latest(registry=None):
    """Generate Prometheus metrics output"""
    return b"# Mock Prometheus metrics\n"


def push_to_gateway(host, job, registry=None, grouping_key=None):
    """Mock push to Prometheus pushgateway"""
    pass


def start_http_server(port, addr=''):
    """Mock start HTTP metrics server"""
    pass 