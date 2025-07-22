"""
Mock schemas module for testing
"""
from unittest.mock import Mock
import json
import jsonschema


# Audio message schema
AUDIO_MESSAGE_SCHEMA = {
    "type": "object",
    "properties": {
        "sensor_id": {"type": "string"},
        "timestamp": {"type": "string"},
        "audio_data": {"type": "string"},
        "sample_rate": {"type": "number"},
        "duration": {"type": "number"},
        "format": {"type": "string"}
    },
    "required": ["sensor_id", "timestamp", "audio_data"]
}

# Feature schemas
FEATURE_A_SCHEMA = {
    "type": "object",
    "properties": {
        "features": {"type": "array", "items": {"type": "number"}},
        "algorithm": {"type": "string"},
        "confidence": {"type": "number", "minimum": 0, "maximum": 1},
        "timestamp": {"type": "string"}
    },
    "required": ["features", "algorithm"]
}

FEATURE_B_SCHEMA = {
    "type": "object",
    "properties": {
        "classification": {"type": "string"},
        "confidence_score": {"type": "number", "minimum": 0, "maximum": 1},
        "metadata": {"type": "object"},
        "timestamp": {"type": "string"}
    },
    "required": ["classification", "confidence_score"]
}


class AudioMessageValidator:
    """Mock audio message validator"""
    
    def __init__(self):
        self.schema = AUDIO_MESSAGE_SCHEMA
    
    def validate(self, message):
        """Validate audio message"""
        # For mock purposes, just check basic structure
        if not message:
            return False
        
        if isinstance(message, str):
            try:
                message = json.loads(message)
            except json.JSONDecodeError:
                return False
        
        # Check payload size (max 1MB for audio data)
        if 'audio_data' in message:
            audio_data_size = len(str(message['audio_data']).encode('utf-8'))
            if audio_data_size > 1024 * 1024:  # 1MB limit
                raise ValueError("Payload too large")
        
        # Basic validation - check for required fields (flexible for different message types)
        required_fields = ['sensor_id', 'timestamp']
        if not all(field in message for field in required_fields):
            return False
        
        return True
    
    def is_valid(self, message):
        """Check if message is valid"""
        return self.validate(message)


def validate_audio_message(message):
    """Validate audio message function"""
    validator = AudioMessageValidator()
    return validator.validate(message)


def validate_feature_a(feature_data):
    """Validate feature A data"""
    # For mock purposes, just check basic structure
    if not feature_data:
        return False
    
    if isinstance(feature_data, str):
        try:
            feature_data = json.loads(feature_data)
        except json.JSONDecodeError:
            return False
    
    # Basic validation - check for basic required fields (flexible schema)
    if 'feature_id' not in feature_data or 'timestamp' not in feature_data:
        return False
    
    # Accept different feature formats (features or enhanced_features)
    has_features = ('features' in feature_data or 
                   'enhanced_features' in feature_data or
                   'classification' in feature_data)
    if not has_features:
        return False
    
    return True


def validate_feature_b(feature_data):
    """Validate feature B data"""
    # For mock purposes, just check basic structure
    if not feature_data:
        return False
    
    if isinstance(feature_data, str):
        try:
            feature_data = json.loads(feature_data)
        except json.JSONDecodeError:
            return False
    
    # Basic validation - check for required fields
    required_fields = ['feature_id', 'sensor_id', 'timestamp', 'features']
    if not all(field in feature_data for field in required_fields):
        return False
    
    return True


# Mock validation module
class validation:
    """Mock schemas.validation module"""
    AudioMessageValidator = AudioMessageValidator
    validate_audio_message = staticmethod(validate_audio_message)
    validate_feature_a = staticmethod(validate_feature_a)
    validate_feature_b = staticmethod(validate_feature_b) 