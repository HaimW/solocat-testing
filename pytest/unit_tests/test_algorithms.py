"""
Unit tests for Algorithm A and Algorithm B audio processing components.
"""
import pytest
import json
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any
import asyncio


class TestAlgorithmA:
    """Unit tests for Algorithm A - Audio to Feature Type A processing."""
    
    @pytest.mark.unit
    def test_algorithm_a_initialization(self):
        """Test Algorithm A proper initialization."""
        from audio_processing.algorithms import AlgorithmA
        
        config = {"model_path": "/models/algorithm_a.pkl", "threshold": 0.5}
        algorithm_a = AlgorithmA(config)
        
        assert algorithm_a.config == config
        assert algorithm_a.threshold == 0.5
        assert algorithm_a.is_initialized is True
    
    @pytest.mark.unit
    def test_audio_validation(self, sample_audio_data):
        """Test audio data validation."""
        from audio_processing.algorithms import AlgorithmA
        
        algorithm_a = AlgorithmA({})
        
        # Valid audio data
        assert algorithm_a.validate_audio_data(sample_audio_data) is True
        
        # Invalid audio data - missing required fields
        invalid_data = sample_audio_data.copy()
        del invalid_data["audio_data"]
        assert algorithm_a.validate_audio_data(invalid_data) is False
        
        # Invalid audio data - wrong format
        invalid_data = sample_audio_data.copy()
        invalid_data["sample_rate"] = "invalid"
        assert algorithm_a.validate_audio_data(invalid_data) is False
    
    @pytest.mark.unit
    def test_feature_extraction(self, sample_audio_data):
        """Test feature extraction from audio data."""
        from audio_processing.algorithms import AlgorithmA
        
        algorithm_a = AlgorithmA({})
        
        with patch('audio_processing.algorithms.extract_mfcc') as mock_mfcc, \
             patch('audio_processing.algorithms.extract_spectral_centroid') as mock_spectral, \
             patch('audio_processing.algorithms.extract_zero_crossing_rate') as mock_zcr:
            
            mock_mfcc.return_value = [1.2, 3.4, 5.6, 7.8]
            mock_spectral.return_value = 2500.5
            mock_zcr.return_value = 0.15
            
            features = algorithm_a.extract_features(sample_audio_data)
            
            assert "mfcc" in features
            assert "spectral_centroid" in features
            assert "zero_crossing_rate" in features
            assert features["mfcc"] == [1.2, 3.4, 5.6, 7.8]
            assert features["spectral_centroid"] == 2500.5
            assert features["zero_crossing_rate"] == 0.15
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_audio_message(self, sample_audio_data, sample_feature_type_a):
        """Test complete audio message processing."""
        from audio_processing.algorithms import AlgorithmA
        
        algorithm_a = AlgorithmA({})
        
        with patch.object(algorithm_a, 'extract_features') as mock_extract:
            mock_extract.return_value = sample_feature_type_a["features"]
            
            result = await algorithm_a.process_message(json.dumps(sample_audio_data))
            
            assert result is not None
            assert "feature_id" in result
            assert "sensor_id" in result
            assert result["sensor_id"] == sample_audio_data["sensor_id"]
            assert "features" in result
            assert "processing_time" in result
    
    @pytest.mark.unit
    def test_error_handling_invalid_json(self):
        """Test error handling for invalid JSON input."""
        from audio_processing.algorithms import AlgorithmA
        
        algorithm_a = AlgorithmA({})
        
        with pytest.raises(json.JSONDecodeError):
            algorithm_a.process_message("invalid json")
    
    @pytest.mark.unit
    def test_performance_metrics_collection(self, sample_audio_data):
        """Test performance metrics are collected during processing."""
        from audio_processing.algorithms import AlgorithmA
        
        algorithm_a = AlgorithmA({})
        
        with patch.object(algorithm_a, 'extract_features') as mock_extract:
            mock_extract.return_value = {"mfcc": [1, 2, 3]}
            
            result = algorithm_a.process_message(json.dumps(sample_audio_data))
            
            assert "processing_time" in result
            assert isinstance(result["processing_time"], float)
            assert result["processing_time"] > 0


class TestAlgorithmB:
    """Unit tests for Algorithm B - Feature Type A to Feature Type B processing."""
    
    @pytest.mark.unit
    def test_algorithm_b_initialization(self):
        """Test Algorithm B proper initialization."""
        from audio_processing.algorithms import AlgorithmB
        
        config = {"model_path": "/models/algorithm_b.pkl", "confidence_threshold": 0.8}
        algorithm_b = AlgorithmB(config)
        
        assert algorithm_b.config == config
        assert algorithm_b.confidence_threshold == 0.8
        assert algorithm_b.is_initialized is True
    
    @pytest.mark.unit
    def test_feature_validation(self, sample_feature_type_a):
        """Test Feature Type A validation."""
        from audio_processing.algorithms import AlgorithmB
        
        algorithm_b = AlgorithmB({})
        
        # Valid feature data
        assert algorithm_b.validate_feature_data(sample_feature_type_a) is True
        
        # Invalid feature data - missing features
        invalid_data = sample_feature_type_a.copy()
        del invalid_data["features"]
        assert algorithm_b.validate_feature_data(invalid_data) is False
    
    @pytest.mark.unit
    def test_classification_processing(self, sample_feature_type_a):
        """Test classification processing."""
        from audio_processing.algorithms import AlgorithmB
        
        algorithm_b = AlgorithmB({})
        
        with patch('audio_processing.algorithms.classify_audio') as mock_classify, \
             patch('audio_processing.algorithms.detect_emotion') as mock_emotion, \
             patch('audio_processing.algorithms.detect_language') as mock_language:
            
            mock_classify.return_value = ("speech", 0.95)
            mock_emotion.return_value = "neutral"
            mock_language.return_value = "en"
            
            enhanced_features = algorithm_b.process_features(sample_feature_type_a["features"])
            
            assert "classification" in enhanced_features
            assert "confidence" in enhanced_features
            assert "emotion" in enhanced_features
            assert "language" in enhanced_features
            assert enhanced_features["classification"] == "speech"
            assert enhanced_features["confidence"] == 0.95
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_process_feature_message(self, sample_feature_type_a, sample_feature_type_b):
        """Test complete feature message processing."""
        from audio_processing.algorithms import AlgorithmB
        
        algorithm_b = AlgorithmB({})
        
        with patch.object(algorithm_b, 'process_features') as mock_process:
            mock_process.return_value = sample_feature_type_b["enhanced_features"]
            
            result = await algorithm_b.process_message(json.dumps(sample_feature_type_a))
            
            assert result is not None
            assert "feature_id" in result
            assert "source_feature" in result
            assert result["source_feature"] == sample_feature_type_a["feature_id"]
            assert "enhanced_features" in result
            assert "processing_time" in result
    
    @pytest.mark.unit
    def test_confidence_filtering(self, sample_feature_type_a):
        """Test confidence threshold filtering."""
        from audio_processing.algorithms import AlgorithmB
        
        algorithm_b = AlgorithmB({"confidence_threshold": 0.9})
        
        with patch('audio_processing.algorithms.classify_audio') as mock_classify:
            # Low confidence result
            mock_classify.return_value = ("speech", 0.7)
            
            with pytest.raises(ValueError, match="Confidence below threshold"):
                algorithm_b.process_features(sample_feature_type_a["features"])
    
    @pytest.mark.unit
    def test_memory_cleanup(self, sample_feature_type_a):
        """Test memory cleanup after processing."""
        from audio_processing.algorithms import AlgorithmB
        
        algorithm_b = AlgorithmB({})
        
        with patch.object(algorithm_b, 'process_features') as mock_process:
            mock_process.return_value = {"classification": "speech"}
            
            # Process multiple messages
            for i in range(10):
                result = algorithm_b.process_message(json.dumps(sample_feature_type_a))
            
            # Verify memory usage doesn't grow indefinitely
            assert algorithm_b.get_memory_usage() < 100  # MB threshold


class TestAlgorithmIntegration:
    """Integration tests between Algorithm A and Algorithm B."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_algorithm_pipeline(self, sample_audio_data):
        """Test complete pipeline from audio to Feature Type B."""
        from audio_processing.algorithms import AlgorithmA, AlgorithmB
        
        algorithm_a = AlgorithmA({})
        algorithm_b = AlgorithmB({})
        
        with patch.object(algorithm_a, 'extract_features') as mock_extract_a, \
             patch.object(algorithm_b, 'process_features') as mock_process_b:
            
            mock_extract_a.return_value = {"mfcc": [1, 2, 3]}
            mock_process_b.return_value = {"classification": "speech", "confidence": 0.95}
            
            # Process through Algorithm A
            feature_a = await algorithm_a.process_message(json.dumps(sample_audio_data))
            
            # Process through Algorithm B
            feature_b = await algorithm_b.process_message(json.dumps(feature_a))
            
            assert feature_b["source_feature"] == feature_a["feature_id"]
            assert "enhanced_features" in feature_b
    
    @pytest.mark.unit
    def test_data_format_compatibility(self, sample_audio_data, sample_feature_type_a):
        """Test data format compatibility between algorithms."""
        from audio_processing.algorithms import AlgorithmA, AlgorithmB
        
        algorithm_a = AlgorithmA({})
        algorithm_b = AlgorithmB({})
        
        # Verify Algorithm A output is valid input for Algorithm B
        assert algorithm_b.validate_feature_data(sample_feature_type_a) is True
        
        # Verify field mapping
        required_fields = ["feature_id", "features", "timestamp"]
        for field in required_fields:
            assert field in sample_feature_type_a 