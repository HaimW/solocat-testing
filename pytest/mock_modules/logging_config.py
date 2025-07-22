"""
Mock logging_config module for testing
"""
import logging
import time
from unittest.mock import Mock
from unittest.mock import MagicMock


test_config = {"logging": {"level": "INFO"}}


class LoggingConfig:
    """Mock logging configuration"""
    
    def __init__(self):
        self.loggers = {}
        self.handlers = {}
        self.formatters = {}
        self.config_loaded = False
    
    def setup_logging(self, config_file=None, log_level="INFO"):
        """Setup logging configuration"""
        # Mock setup - don't actually configure logging for tests
        self.config_loaded = True
        
        # Create mock logger
        logger = logging.getLogger("mock_logger")
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Mock handler
        handler = Mock()
        handler.emit = Mock()
        
        # Mock formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        self.loggers["main"] = logger
        self.handlers["console"] = handler
        self.formatters["standard"] = formatter
        
        return logger
    
    def get_logger(self, name="main"):
        """Get configured logger"""
        if name in self.loggers:
            return self.loggers[name]
        
        # Create new mock logger
        logger = Mock()
        logger.info = Mock()
        logger.warning = Mock()
        logger.error = Mock()
        logger.debug = Mock()
        logger.critical = Mock()
        
        self.loggers[name] = logger
        return logger
    
    def set_log_level(self, level):
        """Set logging level"""
        for logger in self.loggers.values():
            if hasattr(logger, 'setLevel'):
                logger.setLevel(getattr(logging, level.upper(), logging.INFO))
    
    def add_file_handler(self, filename, level="INFO"):
        """Add file handler"""
        handler = Mock()
        handler.filename = filename
        handler.level = level
        self.handlers[f"file_{filename}"] = handler
        return handler
    
    def add_rotating_file_handler(self, filename, max_bytes=10485760, backup_count=5):
        """Add rotating file handler"""
        handler = Mock()
        handler.filename = filename
        handler.maxBytes = max_bytes
        handler.backupCount = backup_count
        self.handlers[f"rotating_{filename}"] = handler
        return handler


class SecurityLogger:
    """Mock security logger"""
    
    def __init__(self):
        self.security_events = []
        self.audit_events = []
    
    def log_security_event(self, event_type, message, severity="INFO", user_id=None):
        """Log security event"""
        event = {
            "timestamp": time.time(),
            "type": event_type,
            "message": message,
            "severity": severity,
            "user_id": user_id,
            "source": "security_logger"
        }
        self.security_events.append(event)
        return event
    
    def log_audit_event(self, action, resource, user_id, result="success"):
        """Log audit event"""
        event = {
            "timestamp": time.time(),
            "action": action,
            "resource": resource,
            "user_id": user_id,
            "result": result,
            "source": "audit_logger"
        }
        self.audit_events.append(event)
        return event
    
    def get_security_events(self, hours=24):
        """Get recent security events"""
        cutoff_time = time.time() - (hours * 3600)
        return [
            event for event in self.security_events
            if event["timestamp"] > cutoff_time
        ]
    
    def get_audit_events(self, hours=24):
        """Get recent audit events"""
        cutoff_time = time.time() - (hours * 3600)
        return [
            event for event in self.audit_events
            if event["timestamp"] > cutoff_time
        ]


class PerformanceLogger:
    """Mock performance logger"""
    
    def __init__(self):
        self.performance_metrics = []
    
    def log_performance_metric(self, operation, duration, metadata=None):
        """Log performance metric"""
        metric = {
            "timestamp": time.time(),
            "operation": operation,
            "duration": duration,
            "metadata": metadata or {},
            "source": "performance_logger"
        }
        self.performance_metrics.append(metric)
        return metric
    
    def get_average_duration(self, operation, hours=24):
        """Get average duration for operation"""
        cutoff_time = time.time() - (hours * 3600)
        relevant_metrics = [
            metric for metric in self.performance_metrics
            if metric["operation"] == operation and metric["timestamp"] > cutoff_time
        ]
        
        if not relevant_metrics:
            return 0.0
        
        total_duration = sum(metric["duration"] for metric in relevant_metrics)
        return total_duration / len(relevant_metrics)


def setup_logging(config_file=None, log_level="INFO"):
    """Module-level setup_logging function"""
    config = LoggingConfig()
    return config.setup_logging(config_file, log_level)


def get_logger(name="main"):
    """Module-level get_logger function"""
    config = LoggingConfig()
    return config.get_logger(name)


def setup_logging(config):
    logger = MagicMock()
    logger.info = MagicMock()
    logger.error = MagicMock()
    return logger


# Mock setup module
class setup:
    """Mock logging_config.setup module"""
    setup_logging = staticmethod(setup_logging)
    get_logger = staticmethod(get_logger)
    LoggingConfig = LoggingConfig
    SecurityLogger = SecurityLogger
    PerformanceLogger = PerformanceLogger 