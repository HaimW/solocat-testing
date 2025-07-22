"""
Mock prometheus_client module for testing with enhanced metrics collection
"""
from unittest.mock import Mock
import time
import json
from collections import defaultdict


class Counter:
    """Mock Prometheus Counter metric with realistic tracking"""
    
    def __init__(self, name, documentation, labelnames=None, registry=None):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames or []
        self.registry = registry
        self._value = 0
        self._labels = {}
        self._call_history = []
        
        # Register with monitoring
        if registry:
            registry.register(self)
    
    def inc(self, amount=1):
        """Increment counter with tracking"""
        self._value += amount
        self._call_history.append({
            'timestamp': time.time(),
            'action': 'inc',
            'amount': amount,
            'total': self._value
        })
    
    def get_value(self):
        """Get current counter value"""
        return self._value
    
    def labels(self, **kwargs):
        """Return labeled metric with tracking"""
        label_key = tuple(sorted(kwargs.items()))
        if label_key not in self._labels:
            labeled_counter = LabeledCounter(self.name, kwargs)
            self._labels[label_key] = labeled_counter
        return self._labels[label_key]


class LabeledCounter:
    """Labeled counter with call tracking"""
    
    def __init__(self, name, labels):
        self.name = name
        self.labels_dict = labels
        self._value = 0
        self._call_history = []
    
    def inc(self, amount=1):
        """Increment with tracking"""
        self._value += amount
        self._call_history.append({
            'timestamp': time.time(),
            'labels': self.labels_dict,
            'amount': amount,
            'total': self._value
        })


class Gauge:
    """Mock Prometheus Gauge metric with realistic behavior"""
    
    def __init__(self, name, documentation, labelnames=None, registry=None):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames or []
        self.registry = registry
        self._value = 0
        self._labels = {}
        self._history = []
        
        if registry:
            registry.register(self)
    
    def set(self, value):
        """Set gauge value with history tracking"""
        old_value = self._value
        self._value = value
        self._history.append({
            'timestamp': time.time(),
            'action': 'set',
            'old_value': old_value,
            'new_value': value
        })
    
    def inc(self, amount=1):
        """Increment gauge"""
        self._value += amount
        self._history.append({
            'timestamp': time.time(),
            'action': 'inc',
            'amount': amount,
            'total': self._value
        })
    
    def dec(self, amount=1):
        """Decrement gauge"""
        self._value -= amount
        self._history.append({
            'timestamp': time.time(),
            'action': 'dec',
            'amount': amount,
            'total': self._value
        })
    
    def get_value(self):
        """Get current gauge value"""
        return self._value
    
    def labels(self, **kwargs):
        """Return labeled metric"""
        label_key = tuple(sorted(kwargs.items()))
        if label_key not in self._labels:
            self._labels[label_key] = LabeledGauge(self.name, kwargs)
        return self._labels[label_key]


class LabeledGauge:
    """Labeled gauge with tracking"""
    
    def __init__(self, name, labels):
        self.name = name
        self.labels_dict = labels
        self._value = 0
    
    def set(self, value):
        self._value = value
    
    def inc(self, amount=1):
        self._value += amount
    
    def dec(self, amount=1):
        self._value -= amount


class Histogram:
    """Mock Prometheus Histogram with timing capabilities"""
    
    def __init__(self, name, documentation, labelnames=None, buckets=None, registry=None):
        self.name = name
        self.documentation = documentation
        self.labelnames = labelnames or []
        self.buckets = buckets or (.005, .01, .025, .05, .075, .1, .25, .5, .75, 1.0, 2.5, 5.0, 7.5, 10.0, float('inf'))
        self.registry = registry
        self._observations = []
        self._labels = {}
        
        if registry:
            registry.register(self)
    
    def time(self):
        """Return timer context manager"""
        return HistogramTimer(self)
    
    def observe(self, amount):
        """Observe a value with tracking"""
        self._observations.append({
            'timestamp': time.time(),
            'value': amount
        })
    
    def get_observations(self):
        """Get all observations"""
        return self._observations
    
    def labels(self, **kwargs):
        """Return labeled metric"""
        label_key = tuple(sorted(kwargs.items()))
        if label_key not in self._labels:
            self._labels[label_key] = LabeledHistogram(self.name, kwargs)
        return self._labels[label_key]


class LabeledHistogram:
    """Labeled histogram with tracking"""
    
    def __init__(self, name, labels):
        self.name = name
        self.labels_dict = labels
        self._observations = []
    
    def time(self):
        return HistogramTimer(self)
    
    def observe(self, amount):
        self._observations.append({
            'timestamp': time.time(),
            'labels': self.labels_dict,
            'value': amount
        })


class HistogramTimer:
    """Histogram timer context manager with actual timing"""
    
    def __init__(self, histogram=None):
        self.histogram = histogram
        self.start_time = None
        self.duration = None
    
    def __enter__(self):
        self.start_time = time.time()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.duration = time.time() - self.start_time
        if self.histogram:
            self.histogram.observe(self.duration)


class CollectorRegistry:
    """Enhanced Prometheus Collector Registry with test reporting"""
    
    def __init__(self):
        self.collectors = {}
        self._metrics_data = defaultdict(list)
    
    def register(self, collector):
        """Register a collector"""
        self.collectors[collector.name] = collector
    
    def unregister(self, collector):
        """Unregister a collector"""
        if collector.name in self.collectors:
            del self.collectors[collector.name]
    
    def get_metrics_summary(self):
        """Get summary of all metrics for reporting"""
        summary = {}
        for name, collector in self.collectors.items():
            if hasattr(collector, 'get_value'):
                summary[name] = collector.get_value()
            elif hasattr(collector, 'get_observations'):
                obs = collector.get_observations()
                if obs:
                    summary[name] = {
                        'count': len(obs),
                        'avg': sum(o['value'] for o in obs) / len(obs),
                        'min': min(o['value'] for o in obs),
                        'max': max(o['value'] for o in obs)
                    }
        return summary
    
    def generate_test_report(self):
        """Generate test metrics report"""
        return {
            'timestamp': time.time(),
            'metrics': self.get_metrics_summary(),
            'collectors_count': len(self.collectors)
        }


# Default registry instance
REGISTRY = CollectorRegistry()


# Test-specific metrics for the audio processing system
TEST_METRICS = {
    'test_execution_counter': Counter(
        'test_execution_total',
        'Total number of test executions',
        labelnames=['test_type', 'status'],
        registry=REGISTRY
    ),
    'test_duration_histogram': Histogram(
        'test_duration_seconds',
        'Test execution duration',
        labelnames=['test_category'],
        registry=REGISTRY
    ),
    'algorithm_processing_time': Histogram(
        'algorithm_processing_seconds',
        'Algorithm processing time',
        labelnames=['algorithm_name'],
        registry=REGISTRY
    ),
    'message_broker_operations': Counter(
        'message_broker_operations_total',
        'Message broker operations',
        labelnames=['operation_type', 'status'],
        registry=REGISTRY
    ),
    'database_operations': Counter(
        'database_operations_total',
        'Database operations',
        labelnames=['operation_type', 'table'],
        registry=REGISTRY
    ),
    'security_test_results': Counter(
        'security_test_results_total',
        'Security test results',
        labelnames=['test_name', 'result'],
        registry=REGISTRY
    ),
    'system_health_gauge': Gauge(
        'system_health_status',
        'System health status',
        labelnames=['component'],
        registry=REGISTRY
    )
}


def generate_latest(registry=None):
    """Generate Prometheus metrics output in proper format"""
    reg = registry or REGISTRY
    metrics_output = ["# Audio Processing System Test Metrics\n"]
    
    for name, collector in reg.collectors.items():
        metrics_output.append(f"# HELP {name} {collector.documentation}\n")
        if isinstance(collector, Counter):
            metrics_output.append(f"# TYPE {name} counter\n")
            metrics_output.append(f"{name} {collector.get_value()}\n")
        elif isinstance(collector, Gauge):
            metrics_output.append(f"# TYPE {name} gauge\n")
            metrics_output.append(f"{name} {collector.get_value()}\n")
        elif isinstance(collector, Histogram):
            metrics_output.append(f"# TYPE {name} histogram\n")
            obs = collector.get_observations()
            metrics_output.append(f"{name}_count {len(obs)}\n")
            if obs:
                total = sum(o['value'] for o in obs)
                metrics_output.append(f"{name}_sum {total}\n")
    
    return "".join(metrics_output).encode('utf-8')


def push_to_gateway(host, job, registry=None, grouping_key=None):
    """Mock push to Prometheus pushgateway with logging"""
    reg = registry or REGISTRY
    print(f"[PROMETHEUS] Pushing metrics to {host} for job '{job}'")
    if grouping_key:
        print(f"[PROMETHEUS] Grouping key: {grouping_key}")
    
    # Simulate successful push
    return True


def start_http_server(port, addr=''):
    """Mock start HTTP metrics server"""
    print(f"[PROMETHEUS] Starting metrics server on {addr}:{port}")
    return True


# Utility functions for test integration
def record_test_start(test_category, test_name):
    """Record test start"""
    TEST_METRICS['test_execution_counter'].labels(
        test_type=test_category, 
        status='started'
    ).inc()


def record_test_completion(test_category, test_name, duration, success=True):
    """Record test completion"""
    status = 'passed' if success else 'failed'
    TEST_METRICS['test_execution_counter'].labels(
        test_type=test_category,
        status=status
    ).inc()
    
    TEST_METRICS['test_duration_histogram'].labels(
        test_category=test_category
    ).observe(duration)


def record_algorithm_processing(algorithm_name, processing_time):
    """Record algorithm processing time"""
    TEST_METRICS['algorithm_processing_time'].labels(
        algorithm_name=algorithm_name
    ).observe(processing_time)


def record_security_test_result(test_name, passed=True):
    """Record security test result"""
    result = 'pass' if passed else 'fail'
    TEST_METRICS['security_test_results'].labels(
        test_name=test_name,
        result=result
    ).inc()


def get_test_metrics_summary():
    """Get comprehensive test metrics summary"""
    return REGISTRY.generate_test_report()


def export_metrics_to_file(filename='test_metrics.json'):
    """Export current metrics to JSON file"""
    metrics_data = get_test_metrics_summary()
    with open(filename, 'w') as f:
        json.dump(metrics_data, f, indent=2)
    return filename 