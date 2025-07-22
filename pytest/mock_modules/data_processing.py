"""
Mock data_processing module for testing
"""
from unittest.mock import Mock, MagicMock
import xml.etree.ElementTree as ET
import json
import pickle
import time


class SafeXMLParser:
    """Mock safe XML parser"""
    
    def __init__(self):
        self.parser = MagicMock()
        # Disable external entity processing for security
        self.parser.entity = {}
        self.parsed_documents = []
    
    def parse_xml(self, xml_string, validate=True):
        """Parse XML string safely"""
        if validate and not self.validate_xml(xml_string):
            raise ValueError("XML validation failed - potential security issue")
        
        try:
            # Mock parsing - don't actually parse potentially dangerous XML
            root = {
                "tag": "root",
                "text": "Mock XML content",
                "attributes": {},
                "children": []
            }
            
            self.parsed_documents.append({
                "timestamp": time.time(),
                "xml_length": len(xml_string),
                "validation_passed": validate
            })
            
            return root
            
        except ET.ParseError as e:
            raise ValueError(f"XML parsing error: {e}")
    
    def validate_xml(self, xml_string):
        """Validate XML for security issues"""
        if not xml_string:
            return False
        
        # Check for external entity references (XXE)
        dangerous_patterns = [
            "<!ENTITY",
            "<!DOCTYPE",
            "SYSTEM",
            "PUBLIC",
            "file://",
            "http://",
            "https://",
            "ftp://"
        ]
        
        xml_upper = xml_string.upper()
        for pattern in dangerous_patterns:
            if pattern in xml_upper:
                return False
        
        return True
    
    def xml_to_dict(self, xml_string):
        """Convert XML to dictionary"""
        parsed = self.parse_xml(xml_string)
        return {
            "root": parsed,
            "metadata": {
                "parser": "SafeXMLParser",
                "timestamp": time.time(),
                "security_validated": True
            }
        }
    
    def parse_sensor_config(self, xml_string):
        """Parse sensor configuration XML"""
        if "<!ENTITY" in xml_string:
            raise ValueError("External entities not allowed")
        return self.parse_xml(xml_string)


class SecureDeserializer:
    """Mock secure deserializer"""
    
    def __init__(self):
        self.allowed_types = {
            'str', 'int', 'float', 'bool', 'list', 'dict', 'tuple'
        }
        self.blocked_modules = {
            'os', 'sys', 'subprocess', 'eval', 'exec',
            'importlib', '__import__', 'open', 'file'
        }
        self.deserialization_log = []
    
    def safe_json_loads(self, json_string):
        """Safely deserialize JSON"""
        try:
            data = json.loads(json_string)
            
            # Log the operation
            self.deserialization_log.append({
                "type": "json",
                "timestamp": time.time(),
                "size": len(json_string),
                "safe": True
            })
            
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON deserialization error: {e}")
    
    def safe_pickle_loads(self, pickle_data):
        """Safely deserialize pickle data"""
        # In a real implementation, this would use a restricted unpickler
        # For testing, we'll just return mock data
        
        self.deserialization_log.append({
            "type": "pickle",
            "timestamp": time.time(),
            "size": len(pickle_data) if pickle_data else 0,
            "safe": True
        })
        
        return {"mock": "pickle_data", "safe_deserialization": True}
    
    def deserialize(self, data, format="json"):
        """Generic deserialize method"""
        if format not in ("json", "pickle"):
            raise ValueError("Unsafe deserialization method")
        if format == "json":
            return self.safe_json_loads(data)
        elif format == "pickle":
            return self.safe_pickle_loads(data)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def validate_data_structure(self, data, max_depth=10, max_items=1000):
        """Validate data structure for safety"""
        if self._get_depth(data) > max_depth:
            return False, "Data structure too deep"
        
        if self._count_items(data) > max_items:
            return False, "Too many items in data structure"
        
        return True, "Data structure is safe"
    
    def _get_depth(self, obj, current_depth=0):
        """Get depth of nested data structure"""
        if current_depth > 50:  # Prevent infinite recursion
            return current_depth
        
        if isinstance(obj, (list, tuple)):
            if not obj:
                return current_depth
            return max(self._get_depth(item, current_depth + 1) for item in obj)
        elif isinstance(obj, dict):
            if not obj:
                return current_depth
            return max(self._get_depth(value, current_depth + 1) for value in obj.values())
        else:
            return current_depth
    
    def _count_items(self, obj):
        """Count total items in data structure"""
        if isinstance(obj, (list, tuple)):
            return len(obj) + sum(self._count_items(item) for item in obj)
        elif isinstance(obj, dict):
            return len(obj) + sum(self._count_items(value) for value in obj.values())
        else:
            return 1


class DataTransformer:
    """Mock data transformer"""
    
    def __init__(self):
        self.transformations = []
    
    def normalize_audio_data(self, audio_data):
        """Normalize audio data"""
        if not audio_data:
            return {}
        
        normalized = {
            "sensor_id": audio_data.get("sensor_id", "unknown"),
            "timestamp": audio_data.get("timestamp", time.time()),
            "sample_rate": audio_data.get("sample_rate", 44100),
            "duration": audio_data.get("duration", 0.0),
            "channels": audio_data.get("channels", 1),
            "format": audio_data.get("format", "wav")
        }
        
        self.transformations.append({
            "type": "audio_normalization",
            "timestamp": time.time(),
            "input_keys": list(audio_data.keys()),
            "output_keys": list(normalized.keys())
        })
        
        return normalized
    
    def sanitize_input(self, user_input):
        """Sanitize user input"""
        if not isinstance(user_input, str):
            return str(user_input)
        
        # Remove potentially dangerous characters
        dangerous_chars = ['<', '>', '"', "'", '&', '\x00', '\r']
        sanitized = user_input
        
        for char in dangerous_chars:
            sanitized = sanitized.replace(char, '')
        
        return sanitized.strip()


class DataMasker:
    def mask_sensitive_data(self, data, field_type="default"):
        if isinstance(data, dict):
            masked = data.copy()
            if "user_id" in masked:
                masked["user_id"] = "user***45"
            return masked
        else:
            return {"masked_data": data}


class InputValidator:
    def validate_payload_size(self, payload, max_size=1024):
        if len(payload) > max_size:
            raise ValueError("Payload too large")
        return True

# Mock submodules
class xml_parser:
    """Mock data_processing.xml_parser module"""
    SafeXMLParser = SafeXMLParser


class serialization:
    """Mock data_processing.serialization module"""
    SecureDeserializer = SecureDeserializer


class transform:
    """Mock data_processing.transform module"""
    DataTransformer = DataTransformer 