"""
Mock audio processing module for testing
"""
import asyncio
from unittest.mock import MagicMock
import json
import time
import datetime


class AlgorithmA:
    """Mock Algorithm A for testing"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.threshold = self.config.get('threshold', 0.5)
        self.is_initialized = True
        self.model_path = self.config.get('model_path', '/models/algorithm_a.pkl')
        
        # Use MagicMock to track method calls for test assertions
        from unittest.mock import MagicMock
        self._process_mock = MagicMock(side_effect=self._process_message_sync)
        
        # Make process_message directly accessible as MagicMock for test patching
        self.process_message = MagicMock(side_effect=self._async_process_wrapper)
    
    def validate_audio_data(self, audio_data):
        """Mock audio validation"""
        if not audio_data:
            raise ValueError("Audio data is empty")
        
        # Check for required fields
        required_fields = ["audio_data", "sensor_id", "timestamp"]
        for field in required_fields:
            if field not in audio_data:
                return False
        
        # Validate data types
        if not isinstance(audio_data.get("sample_rate"), (int, float)):
            return False
        
        return True
    
    def extract_features(self, audio_data):
        """Mock feature extraction"""
        # Simulate processing time
        time.sleep(0.001)
        
        return {
            'mfcc': [1.2, 3.4, 5.6, 7.8],
            'spectral_centroid': 2500.5,
            'zero_crossing_rate': 0.15,
            'metadata': {
                'algorithm': 'A',
                'version': '1.0',
                'confidence': 0.85,
                'processing_time': 0.001
            }
        }
    
    async def _async_process_wrapper(self, message):
        """Async wrapper for process_message that can be tracked"""
        await asyncio.sleep(0.001)
        return self._process_message_sync(message)
    
    # Note: process_message is set as MagicMock in __init__ for test compatibility
    
    def _process_message_sync(self, message):
        """Synchronous message processing implementation"""
        try:
            if isinstance(message, str):
                message = json.loads(message)
        except json.JSONDecodeError as e:
            # Re-raise the original exception to preserve error details
            raise e
        
        audio_data = message.get('audio_data')
        if not audio_data:
            raise ValueError("No audio data in message")
        
        features = self.extract_features(audio_data)
        
        # Return features in the expected format
        processed_features = [{"mfcc": 1.2, "centroid": 2500.5}]
        
        return {
            'audio_id': message.get('audio_id', 'test_id'),
            'features': processed_features,
            'feature_id': message.get('audio_id', 'test_id') + '_features',
            'sensor_id': message.get('sensor_id', 'default_sensor'),
            'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'status': 'processed',
            'processing_time': 0.001
        }

    async def initialize(self):
        self.is_initialized = True
        return True


class AlgorithmB:
    """Mock Algorithm B for enhanced feature processing"""
    
    def __init__(self, config=None):
        self.algorithm_name = "Algorithm B"
        self.config = config or {}
        self.is_initialized = True
        self.confidence_threshold = self.config.get('confidence_threshold', 0.8)
        self.processing_count = 0
        
        # Use MagicMock to track method calls for test assertions  
        from unittest.mock import MagicMock
        self._process_mock = MagicMock(side_effect=self._process_message_sync)
        
        # Make process_message directly accessible as MagicMock for test patching
        self.process_message = MagicMock(side_effect=self._async_process_wrapper_b)
    
    def validate_feature_data(self, features):
        """Validate feature data for processing"""
        if not features:
            return False
        
        # Handle both dict and list formats
        if isinstance(features, dict):
            # Check for required keys in various formats
            if 'features' in features or 'mfcc' in features or 'enhanced_features' in features or 'classification' in features:
                return True
        elif isinstance(features, list):
            return len(features) > 0
        
        return False
    
    def get_memory_usage(self):
        """Get current memory usage"""
        return {
            'used_mb': 45.2,
            'available_mb': 156.8,
            'percentage': 22.3
        }
    
    def enhance_features(self, features, **kwargs):
        """Enhanced feature processing with classification"""
        if features is None:
            return {
                'enhanced_features': [1.2, 3.4, 5.6, 7.8],
                'classification': 'unknown',
                'confidence': 0.0,
                'emotion': 'neutral',
                'language': 'en'
            }
        # Simulate processing time
        time.sleep(0.002)
        
        # Handle different feature formats safely
        if isinstance(features, dict):
            if 'features' in features:
                feature_list = features['features']
                if isinstance(feature_list, dict) and 'mfcc' in feature_list:
                    enhance_data = feature_list['mfcc'][:5]
                elif isinstance(feature_list, list):
                    # Handle list of dicts or mixed types
                    if feature_list and isinstance(feature_list[0], dict):
                        enhance_data = [1.2, 3.4, 5.6, 7.8]  # Use default for dict lists
                    else:
                        enhance_data = [float(f) if isinstance(f, (int, float)) else 1.0 for f in feature_list[:5]]
                else:
                    enhance_data = [1.2, 3.4, 5.6, 7.8]
            elif 'mfcc' in features:
                mfcc_data = features['mfcc']
                if isinstance(mfcc_data, list):
                    enhance_data = [float(f) if isinstance(f, (int, float)) else 1.0 for f in mfcc_data[:5]]
                else:
                    enhance_data = [1.2, 3.4, 5.6, 7.8]
            else:
                enhance_data = [1.2, 3.4, 5.6, 7.8]
        elif isinstance(features, list):
            # Handle list of dicts or mixed types
            if features and isinstance(features[0], dict):
                enhance_data = [1.2, 3.4, 5.6, 7.8]  # Use default for dict lists
            else:
                enhance_data = [float(f) if isinstance(f, (int, float)) else 1.0 for f in features[:5]]
        else:
            enhance_data = [1.2, 3.4, 5.6, 7.8]
        
        # Ensure all values are numeric before multiplication
        safe_enhance_data = [float(f) if isinstance(f, (int, float)) else 1.0 for f in enhance_data]
        
        return {
            'enhanced_features': [f * 1.5 for f in safe_enhance_data],
            'classification': 'speech',
            'confidence': 0.95,
            'emotion': 'neutral',
            'language': 'en',
            'metadata': {
                'algorithm': 'B',
                'version': '1.0',
                'quality_score': 0.92,
                'processing_time': 0.002
            }
        }
    
    def _process_message_sync(self, message):
        """Synchronous message processing implementation"""
        try:
            if isinstance(message, str):
                message = json.loads(message)
        except json.JSONDecodeError:
            raise json.JSONDecodeError("Invalid JSON", message, 0)
        
        # Handle both 'features' key and direct feature data
        if 'features' in message:
            features = message['features']
        else:
            features = message
        
        enhanced = self.enhance_features(features)
        
        return {
            'feature_id': message.get('feature_id', 'test_feature_id'),
            'enhanced_features': enhanced,
            'source_feature': message.get('feature_id', 'test_feature_id'),
            'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ'),
            'status': 'processed'
        }
    
    async def _async_process_wrapper_b(self, message):
        """Async wrapper for AlgorithmB process_message that can be tracked"""
        await asyncio.sleep(0.001)  # Simulate async processing
        self.processing_count += 1
        return self._process_message_sync(message)
    
    # Note: process_message is set as MagicMock in __init__ for test compatibility
    
    async def _process_message_async(self, message):
        """Asynchronous message processing implementation"""
        await asyncio.sleep(0.001)  # Simulate async processing
        return self._process_message_sync(message)
    
    def process_features(self, features):
        """Process features with confidence filtering"""
        result = self.enhance_features(features)
        
        # Check confidence threshold
        if result.get('confidence', 0) < self.confidence_threshold:
            raise ValueError("Confidence below threshold")
        
        return result


# Mock module-level functions
def extract_mfcc(audio_data):
    """Mock MFCC extraction"""
    return [0.1, 0.2, 0.3, 0.4, 0.5]


def extract_spectral_centroid(audio_data):
    """Mock spectral centroid extraction"""
    return [1000.0, 1500.0, 2000.0]


def extract_zero_crossing_rate(audio_data):
    """Mock zero crossing rate extraction"""
    return [0.05, 0.07, 0.06]


def classify_audio(features):
    """Mock audio classification"""
    return {
        'classification': 'speech',
        'confidence': 0.85,
        'categories': ['speech', 'music', 'noise'],
        'scores': [0.85, 0.10, 0.05]
    }


def detect_emotion(features):
    """Mock emotion detection"""
    return {
        'emotion': 'neutral',
        'confidence': 0.75,
        'emotions': ['happy', 'sad', 'angry', 'neutral'],
        'scores': [0.15, 0.10, 0.05, 0.75]
    }


def detect_language(features):
    """Mock language detection"""
    return {
        'language': 'english',
        'confidence': 0.90,
        'languages': ['english', 'spanish', 'french'],
        'scores': [0.90, 0.05, 0.05]
    }


# Mock utils module
class utils:
    """Mock audio_processing.utils module"""
    
    @staticmethod
    def generate_timestamp():
        """Generate timestamp"""
        now = time.gmtime(time.time())
        return time.strftime('%Y-%m-%dT%H:%M:%SZ', now)


# Mock pipeline classes
class AudioProcessingPipeline:
    """Mock audio processing pipeline"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.algorithm_a = AlgorithmA()
        self.algorithm_b = AlgorithmB()
        self.is_initialized = False
        
        # Use MagicMock to track calls
        from unittest.mock import MagicMock
        self._process_mock = MagicMock(side_effect=self._process_audio_message)
        self._init_mock = MagicMock(side_effect=self._initialize)
        
        # Make methods directly accessible as MagicMock for test patching
        self.process_audio_message = MagicMock(side_effect=self._process_audio_message)
        self.initialize = MagicMock(side_effect=self._initialize)
    
    async def _process_audio_message(self, message):
        """Process audio message through pipeline"""
        result_a = await self.algorithm_a.process_message(message)
        result_b = await self.algorithm_b.process_message(json.dumps(result_a))
        return {
            'pipeline_result': {
                'algorithm_a': result_a,
                'algorithm_b': result_b
            },
            'status': 'completed',
            'timestamp': datetime.datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
        }
    
    async def _initialize(self):
        """Initialize the pipeline"""
        await asyncio.sleep(0)
        self.is_initialized = True
        return True
    
    # Note: process_audio_message and initialize are set as MagicMock in __init__


# Mock pipeline module  
class pipeline:
    """Mock audio_processing.pipeline module"""
    AudioProcessingPipeline = AudioProcessingPipeline


# Mock algorithms module
class algorithms:
    """Mock audio_processing.algorithms module"""
    AlgorithmA = AlgorithmA
    AlgorithmB = AlgorithmB
    extract_mfcc = staticmethod(extract_mfcc)
    extract_spectral_centroid = staticmethod(extract_spectral_centroid)
    extract_zero_crossing_rate = staticmethod(extract_zero_crossing_rate)
    classify_audio = staticmethod(classify_audio)

# Add these after class definition
algorithms.detect_emotion = staticmethod(detect_emotion)
algorithms.detect_language = staticmethod(detect_language) 


# Add module-level functions for imports
def generate_timestamp():
    """Generate timestamp for features"""
    now = time.gmtime(time.time())
    return time.strftime('%Y-%m-%dT%H:%M:%SZ', now) 