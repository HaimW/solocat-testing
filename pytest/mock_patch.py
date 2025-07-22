"""
Mock patch system to replace missing modules with mocks
"""
import sys
import importlib.util
from pathlib import Path

# Get the path to mock modules
MOCK_MODULES_PATH = Path(__file__).parent / "mock_modules"

# Define mock modules mapping
MOCK_MODULES = {
    'audio_processing': 'audio_processing',
    'audio_processing.algorithms': 'audio_processing',
    'message_broker': 'message_broker', 
    'message_broker.connection': 'message_broker',
    'database': 'database',
    'database.models': 'database',
    'api': 'api',
    'api.routes': 'api',
}

def patch_imports():
    """Patch missing imports with mock modules"""
    for module_name, mock_file in MOCK_MODULES.items():
        if module_name not in sys.modules:
            # Load the mock module
            mock_path = MOCK_MODULES_PATH / f"{mock_file}.py"
            if mock_path.exists():
                spec = importlib.util.spec_from_file_location(module_name, mock_path)
                mock_module = importlib.util.module_from_spec(spec)
                
                # Execute the mock module
                spec.loader.exec_module(mock_module)
                
                # Add to sys.modules
                sys.modules[module_name] = mock_module
                
                # Handle sub-modules
                if '.' in module_name:
                    parent_name = module_name.split('.')[0]
                    if parent_name not in sys.modules:
                        sys.modules[parent_name] = mock_module

def enable_mocks():
    """Enable mock modules for testing"""
    patch_imports()
    print("🎭 Mock modules enabled for testing")

# Auto-enable mocks when this module is imported
enable_mocks() 