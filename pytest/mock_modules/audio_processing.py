"""
Mock audio processing module for testing
"""
from unittest.mock import Mock
import json
import time


class AlgorithmA:
    """Mock Algorithm A for testing"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.threshold = self.config.get('threshold', 0.5)
        self.is_initialized = True
        self.model_path = self.config.get('model_path', '/models/algorithm_a.pkl')
    
    def validate_audio_data(self, audio_data):
        """Mock audio validation"""
        if not audio_data:
            raise ValueError("Audio data is empty")
        return True
    
    def extract_features(self, audio_data):
        """Mock feature extraction"""
        # Simulate processing time
        time.sleep(0.001)
        
        return {
            'features': [0.1, 0.2, 0.3, 0.4, 0.5],
            'metadata': {
                'algorithm': 'A',
                'version': '1.0',
                'confidence': 0.85,
                'processing_time': 0.001
            }
        }
    
    def process_message(self, message):
        """Mock message processing"""
        if isinstance(message, str):
            message = json.loads(message)
        
        audio_data = message.get('audio_data')
        if not audio_data:
            raise ValueError("No audio data in message")
        
        features = self.extract_features(audio_data)
        
        return {
            'audio_id': message.get('audio_id', 'test_id'),
            'features': features,
            'timestamp': time.time(),
            'status': 'processed'
        }


class AlgorithmB:
    """Mock Algorithm B for testing"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.threshold = self.config.get('threshold', 0.7)
        self.is_initialized = True
        self.model_path = self.config.get('model_path', '/models/algorithm_b.pkl')
    
    def validate_features(self, features):
        """Mock feature validation"""
        if not features or 'features' not in features:
            raise ValueError("Invalid features data")
        return True
    
    def enhance_features(self, features):
        """Mock feature enhancement"""
        # Simulate processing time
        time.sleep(0.002)
        
        return {
            'enhanced_features': [f * 1.5 for f in features['features'][:5]],
            'metadata': {
                'algorithm': 'B',
                'version': '1.0',
                'quality_score': 0.92,
                'processing_time': 0.002
            }
        }
    
    def process_message(self, message):
        """Mock message processing"""
        if isinstance(message, str):
            message = json.loads(message)
        
        features = message.get('features')
        if not features:
            raise ValueError("No features in message")
        
        enhanced = self.enhance_features(features)
        
        return {
            'audio_id': message.get('audio_id', 'test_id'),
            'enhanced_features': enhanced,
            'timestamp': time.time(),
            'status': 'enhanced'
        }


# Mock algorithms module
algorithms = Mock()
algorithms.AlgorithmA = AlgorithmA
algorithms.AlgorithmB = AlgorithmB 