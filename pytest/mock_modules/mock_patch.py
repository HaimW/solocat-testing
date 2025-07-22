"""
Mock patch system for dynamically replacing missing modules with mock implementations.
"""
import sys
import os
import importlib.util
from pathlib import Path

# Define the mapping of module names to mock files
MOCK_MODULES = {
    # Audio processing modules
    'audio_processing': 'audio_processing',
    'audio_processing.algorithms': 'audio_processing',
    'audio_processing.utils': 'audio_processing',
    'audio_processing.pipeline': 'audio_processing',
    
    # API modules
    'api': 'api',
    'api.rest_api': 'api',
    'api.auth': 'api',
    'api.cache': 'api',
    'api.middleware': 'api',
    'api.sanitization': 'api',
    'api.file_handler': 'api',
    
    # Database modules
    'database': 'database',
    'database.models': 'database',
    'database.connection': 'database',
    'database.writer': 'database',
    'database.encryption': 'database',
    'database.queries': 'database',
    
    # Message broker modules
    'message_broker': 'message_broker',
    'message_broker.connection': 'message_broker',
    'message_broker.publisher': 'message_broker',
    'message_broker.consumer': 'message_broker',
    'message_broker.queue_manager': 'message_broker',
    'message_broker.load_balancer': 'message_broker',
    
    # Security modules
    'security': 'security',
    'security.auth': 'security',
    'security.encryption': 'security',
    'security.monitoring': 'security',
    'security.audit': 'security',
    'security.rbac': 'security',
    
    # Network modules
    'network': 'network',
    'network.secure_client': 'network',
    'network.security_filter': 'network',
    'network.security': 'network',
    
    # System modules
    'system': 'system',
    'system.operations': 'system',
    
    # Data processing modules
    'data_processing': 'data_processing',
    'data_processing.xml_parser': 'data_processing',
    'data_processing.serializer': 'data_processing',
    'data_processing.serialization': 'data_processing',
    
    # Schema validation modules
    'schemas': 'schemas',
    'schemas.validation': 'schemas',
    
    # Kubernetes modules
    'kubernetes': 'kubernetes',
    'kubernetes.client': 'kubernetes',
    'kubernetes.config': 'kubernetes',
    'kubernetes_integration': 'kubernetes',
    'kubernetes_integration.service_discovery': 'kubernetes',
    
    # Monitoring modules
    'monitoring': 'monitoring',
    'monitoring.metrics': 'monitoring',
    
    # Logging modules
    'logging_config': 'logging_config',
    'logging_config.setup': 'logging_config',
    
    # Load balancing modules
    'load_balancing': 'load_balancing',
    'load_balancing.pod_manager': 'load_balancing',
    
    # Sensor modules
    'sensors': 'sensors',
    'sensors.sensor_client': 'sensors',
    
    # Additional missing modules
    'algorithms': 'audio_processing',
    'security.data_masking': 'security',
    'security.anomaly_detection': 'security',
    
    # External dependencies
    'prometheus_client': 'prometheus_client',
}


def patch_imports():
    """Dynamically patch missing modules with mock implementations."""
    mock_modules_dir = Path(__file__).parent
    
    for module_name, mock_file in MOCK_MODULES.items():
        if module_name not in sys.modules:
            try:
                # Load the mock module
                mock_file_path = mock_modules_dir / f"{mock_file}.py"
                if mock_file_path.exists():
                    spec = importlib.util.spec_from_file_location(mock_file, mock_file_path)
                    mock_module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(mock_module)
                    
                    # Handle nested modules (e.g., api.auth)
                    if '.' in module_name:
                        parts = module_name.split('.')
                        current_name = parts[0]
                        
                        # Create parent module if it doesn't exist
                        if current_name not in sys.modules:
                            sys.modules[current_name] = mock_module
                        
                        # Set up nested attributes
                        current_module = sys.modules[current_name]
                        for i, part in enumerate(parts[1:], 1):
                            full_name = '.'.join(parts[:i+1])
                            
                            if hasattr(mock_module, part):
                                # Get the attribute from our mock module
                                attr_value = getattr(mock_module, part)
                                setattr(current_module, part, attr_value)
                                
                                # Also register as a full module
                                if hasattr(attr_value, '__name__'):
                                    sys.modules[full_name] = attr_value
                                else:
                                    # Create a module wrapper
                                    import types
                                    wrapper_module = types.ModuleType(full_name)
                                    for attr_name in dir(attr_value):
                                        if not attr_name.startswith('_'):
                                            setattr(wrapper_module, attr_name, getattr(attr_value, attr_name))
                                    sys.modules[full_name] = wrapper_module
                            else:
                                # Create a reference to the main mock module
                                sys.modules[full_name] = mock_module
                                setattr(current_module, part, mock_module)
                    else:
                        # Simple module - register directly
                        sys.modules[module_name] = mock_module
                        
            except Exception as e:
                print(f"Warning: Could not load mock for {module_name}: {e}")
                continue


def is_mock_available(module_name):
    """Check if a mock is available for the given module."""
    return module_name in MOCK_MODULES


# Auto-patch on import
patch_imports()
