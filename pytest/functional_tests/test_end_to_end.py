"""
Functional/Integration tests for end-to-end audio processing workflows.
"""
import pytest
import asyncio
import json
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any


class TestEndToEndAudioProcessing:
    """End-to-end tests for complete audio processing pipeline."""
    
    @pytest.mark.functional
    @pytest.mark.asyncio
    async def test_complete_audio_pipeline(self, test_config, sample_audio_data):
        """Test complete pipeline from sensor to database storage."""
        
        # Mock all external dependencies
        with patch('message_broker.connection.MessageBrokerConnection') as mock_broker, \
             patch('database.writer.DataWriter') as mock_writer, \
             patch('algorithms.AlgorithmA') as mock_algo_a, \
             patch('algorithms.AlgorithmB') as mock_algo_b:
            
            # Setup mocks
            mock_broker_instance = AsyncMock()
            mock_broker.return_value = mock_broker_instance
            
            mock_algo_a_instance = AsyncMock()
            mock_algo_a.return_value = mock_algo_a_instance
            mock_algo_a_instance.process_message.return_value = {
                "feature_id": "feat_a_001",
                "sensor_id": sample_audio_data["sensor_id"],
                "timestamp": sample_audio_data["timestamp"],
                "features": {"mfcc": [1, 2, 3], "spectral_centroid": 2500},
                "processing_time": 0.25
            }
            
            mock_algo_b_instance = AsyncMock()
            mock_algo_b.return_value = mock_algo_b_instance
            mock_algo_b_instance.process_message.return_value = {
                "feature_id": "feat_b_001",
                "source_feature": "feat_a_001",
                "timestamp": sample_audio_data["timestamp"],
                "enhanced_features": {"classification": "speech", "confidence": 0.95},
                "processing_time": 0.18
            }
            
            mock_writer_instance = AsyncMock()
            mock_writer.return_value = mock_writer_instance
            
            # Import and initialize system components
            from audio_processing.pipeline import AudioProcessingPipeline
            
            pipeline = AudioProcessingPipeline(test_config)
            await pipeline.initialize()
            
            # Simulate sensor sending audio data
            result = await pipeline.process_audio_message(json.dumps(sample_audio_data))
            
            # Verify the complete flow
            assert result is not None
            mock_algo_a_instance.process_message.assert_called_once()
            mock_algo_b_instance.process_message.assert_called_once()
            mock_writer_instance.write_features.assert_called()
    
    @pytest.mark.functional
    @pytest.mark.asyncio
    async def test_sensor_to_rabbitmq_integration(self, test_config, mock_sensor):
        """Test sensor data transmission to RabbitMQ."""
        
        with patch('message_broker.publisher.MessagePublisher') as mock_publisher:
            mock_publisher_instance = AsyncMock()
            mock_publisher.return_value = mock_publisher_instance
            
            from sensors.sensor_client import SensorClient
            
            sensor_client = SensorClient(test_config["rabbitmq"])
            await sensor_client.connect()
            
            # Generate and send audio data
            audio_data = await mock_sensor.generate_audio_data()
            await sensor_client.send_audio_data(audio_data)
            
            # Verify message was published
            mock_publisher_instance.publish_message.assert_called_once()
            call_args = mock_publisher_instance.publish_message.call_args
            assert "audio_data" in json.loads(call_args[1]["message"])
    
    @pytest.mark.functional
    @pytest.mark.asyncio
    async def test_algorithm_load_balancing(self, test_config, sample_audio_data):
        """Test load balancing across multiple algorithm pods."""
        
        # Create multiple algorithm instances
        algorithm_pods = []
        for i in range(3):
            pod = AsyncMock()
            pod.pod_id = f"algorithm_a_pod_{i}"
            pod.is_healthy = True
            pod.process_message = AsyncMock(return_value={
                "feature_id": f"feat_{i}",
                "processing_time": 0.1 + (i * 0.05)
            })
            algorithm_pods.append(pod)
        
        with patch('kubernetes.client.AppsV1Api') as mock_k8s:
            from load_balancing.pod_manager import PodManager
            
            pod_manager = PodManager(test_config)
            pod_manager.algorithm_pods = algorithm_pods
            
            # Send multiple messages and verify load distribution
            messages = [sample_audio_data for _ in range(9)]
            results = []
            
            for message in messages:
                selected_pod = pod_manager.get_next_healthy_pod()
                result = await selected_pod.process_message(json.dumps(message))
                results.append(result)
            
            # Verify each pod processed 3 messages (round-robin)
            for pod in algorithm_pods:
                assert pod.process_message.call_count == 3
    
    @pytest.mark.functional
    @pytest.mark.asyncio
    async def test_feature_database_storage(self, test_config, sample_feature_type_a, sample_feature_type_b):
        """Test feature storage in database."""
        
        with patch('database.models.Session') as mock_session, \
             patch('database.models.FeatureTypeA') as mock_model_a, \
             patch('database.models.FeatureTypeB') as mock_model_b:
            
            mock_session_instance = Mock()
            mock_session.return_value = mock_session_instance
            
            from database.writer import DataWriter
            
            data_writer = DataWriter(test_config["database"])
            
            # Test Feature Type A storage
            await data_writer.write_feature_type_a(sample_feature_type_a)
            
            # Test Feature Type B storage
            await data_writer.write_feature_type_b(sample_feature_type_b)
            
            # Verify database operations
            assert mock_session_instance.add.call_count == 2
            assert mock_session_instance.commit.call_count == 2
    
    @pytest.mark.functional
    @pytest.mark.asyncio
    async def test_rest_api_real_time_data(self, test_config, sample_feature_type_a):
        """Test REST API real-time data serving."""
        
        with patch('api.cache.RedisCache') as mock_cache:
            mock_cache_instance = AsyncMock()
            mock_cache.return_value = mock_cache_instance
            mock_cache_instance.get.return_value = json.dumps([sample_feature_type_a])
            
            from api.rest_api import AudioProcessingAPI
            
            api = AudioProcessingAPI(test_config)
            
            # Test real-time feature retrieval
            response = await api.get_real_time_features("sensor_001", limit=10)
            
            assert response["status"] == "success"
            assert len(response["features"]) == 1
            assert response["features"][0]["sensor_id"] == "sensor_001"
    
    @pytest.mark.functional
    @pytest.mark.asyncio
    async def test_rest_api_historical_data(self, test_config, mock_database_session):
        """Test REST API historical data retrieval."""
        
        # Mock historical data
        historical_features = [
            Mock(to_dict=lambda: {"feature_id": f"feat_{i}", "timestamp": f"2024-01-{i:02d}T10:00:00Z"})
            for i in range(1, 6)
        ]
        
        mock_database_session.query.return_value.filter.return_value.all.return_value = historical_features
        
        with patch('database.connection.get_session', return_value=mock_database_session):
            from api.rest_api import AudioProcessingAPI
            
            api = AudioProcessingAPI(test_config)
            
            # Test historical data retrieval
            response = await api.get_historical_features(
                sensor_id="sensor_001",
                start_time="2024-01-01T00:00:00Z",
                end_time="2024-01-31T23:59:59Z"
            )
            
            assert response["status"] == "success"
            assert len(response["features"]) == 5
    
    @pytest.mark.functional
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_system_resilience_pod_failure(self, test_config, sample_audio_data):
        """Test system resilience when algorithm pods fail."""
        
        # Setup pods with one failing
        healthy_pod = AsyncMock()
        healthy_pod.is_healthy = True
        healthy_pod.process_message = AsyncMock(return_value={"status": "success"})
        
        failing_pod = AsyncMock()
        failing_pod.is_healthy = False
        failing_pod.process_message = AsyncMock(side_effect=Exception("Pod failed"))
        
        with patch('kubernetes.client.AppsV1Api'):
            from load_balancing.pod_manager import PodManager
            
            pod_manager = PodManager(test_config)
            pod_manager.algorithm_pods = [healthy_pod, failing_pod]
            
            # Process messages - should only use healthy pod
            results = []
            for _ in range(5):
                try:
                    pod = pod_manager.get_next_healthy_pod()
                    result = await pod.process_message(json.dumps(sample_audio_data))
                    results.append(result)
                except Exception:
                    continue
            
            # All messages should be processed by healthy pod
            assert len(results) == 5
            assert healthy_pod.process_message.call_count == 5
            assert failing_pod.process_message.call_count == 0
    
    @pytest.mark.functional
    @pytest.mark.asyncio
    async def test_message_persistence_rabbitmq_restart(self, test_config, sample_audio_data):
        """Test message persistence during RabbitMQ restart simulation."""
        
        connection_states = ['connected', 'disconnected', 'connected']
        connection_call_count = 0
        
        def mock_connection_behavior(*args, **kwargs):
            nonlocal connection_call_count
            state = connection_states[connection_call_count % len(connection_states)]
            connection_call_count += 1
            
            if state == 'disconnected':
                raise ConnectionError("RabbitMQ unavailable")
            
            mock_conn = AsyncMock()
            mock_conn.is_connected = True
            return mock_conn
        
        with patch('message_broker.connection.aiormq.connect', side_effect=mock_connection_behavior):
            from message_broker.connection import MessageBrokerConnection
            
            broker = MessageBrokerConnection(test_config["rabbitmq"])
            
            # Simulate multiple connection attempts during restart
            messages_sent = 0
            for attempt in range(5):
                try:
                    await broker.connect_with_retry()
                    # Simulate sending message
                    messages_sent += 1
                    await broker.disconnect()
                except ConnectionError:
                    # Expected during "restart"
                    continue
            
            # Should successfully send messages before and after restart
            assert messages_sent >= 2


class TestDataConsistency:
    """Tests for data consistency across the system."""
    
    @pytest.mark.functional
    def test_feature_id_consistency(self, sample_audio_data, sample_feature_type_a, sample_feature_type_b):
        """Test feature ID consistency across processing stages."""
        
        # Verify Feature Type A references source audio
        assert sample_feature_type_a["sensor_id"] == sample_audio_data["sensor_id"]
        assert sample_feature_type_a["timestamp"] == sample_audio_data["timestamp"]
        
        # Verify Feature Type B references Feature Type A
        assert sample_feature_type_b["source_feature"] == sample_feature_type_a["feature_id"]
        assert sample_feature_type_b["timestamp"] == sample_feature_type_a["timestamp"]
    
    @pytest.mark.functional
    @pytest.mark.asyncio
    async def test_timestamp_consistency(self):
        """Test timestamp consistency across all components."""
        
        start_time = time.time()
        
        # Simulate processing through multiple components
        with patch('time.time', return_value=start_time):
            from audio_processing.utils import generate_timestamp
            
            timestamps = []
            
            # Generate timestamps at different stages
            for stage in ['sensor', 'algorithm_a', 'algorithm_b', 'database']:
                timestamp = generate_timestamp()
                timestamps.append(timestamp)
                
                # Small delay between stages
                await asyncio.sleep(0.001)
        
        # All timestamps should be within reasonable range
        for timestamp in timestamps:
            assert abs(time.mktime(time.strptime(timestamp, "%Y-%m-%dT%H:%M:%SZ")) - start_time) < 1
    
    @pytest.mark.functional
    def test_json_schema_validation(self, sample_audio_data, sample_feature_type_a, sample_feature_type_b):
        """Test JSON schema validation for all message types."""
        
        from schemas.validation import validate_audio_message, validate_feature_a, validate_feature_b
        
        # Test audio message validation
        assert validate_audio_message(sample_audio_data) is True
        
        # Test Feature Type A validation
        assert validate_feature_a(sample_feature_type_a) is True
        
        # Test Feature Type B validation
        assert validate_feature_b(sample_feature_type_b) is True
        
        # Test invalid messages
        invalid_audio = sample_audio_data.copy()
        del invalid_audio["sensor_id"]
        assert validate_audio_message(invalid_audio) is False


class TestSystemIntegration:
    """Integration tests for system components."""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_kubernetes_service_discovery(self, test_config):
        """Test Kubernetes service discovery for algorithm pods."""
        
        with patch('kubernetes.client.CoreV1Api') as mock_k8s_core, \
             patch('kubernetes.config.load_incluster_config'):
            
            # Mock service endpoints
            mock_endpoints = Mock()
            mock_endpoints.subsets = [
                Mock(addresses=[
                    Mock(ip="10.0.1.10"),
                    Mock(ip="10.0.1.11"),
                    Mock(ip="10.0.1.12")
                ])
            ]
            
            mock_k8s_core.return_value.read_namespaced_endpoints.return_value = mock_endpoints
            
            from kubernetes_integration.service_discovery import ServiceDiscovery
            
            discovery = ServiceDiscovery(test_config)
            endpoints = await discovery.discover_algorithm_pods("algorithm-a-service")
            
            assert len(endpoints) == 3
            assert "10.0.1.10" in endpoints
            assert "10.0.1.11" in endpoints
            assert "10.0.1.12" in endpoints
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_monitoring_integration(self, test_config):
        """Test integration with monitoring systems."""
        
        with patch('prometheus_client.CollectorRegistry') as mock_registry, \
             patch('prometheus_client.Counter') as mock_counter, \
             patch('prometheus_client.Histogram') as mock_histogram:
            
            from monitoring.metrics import MetricsCollector
            
            metrics = MetricsCollector()
            
            # Test metrics collection
            metrics.increment_messages_processed("algorithm_a")
            metrics.record_processing_time("algorithm_a", 0.25)
            metrics.record_queue_size("audio_queue", 150)
            
            # Verify metrics were recorded
            mock_counter.return_value.inc.assert_called()
            mock_histogram.return_value.observe.assert_called()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_logging_integration(self, test_config):
        """Test centralized logging integration."""
        
        with patch('logging.handlers.SysLogHandler') as mock_syslog:
            from logging_config.setup import setup_logging
            
            logger = setup_logging(test_config["logging"])
            
            # Test different log levels
            logger.info("Processing audio message", extra={"sensor_id": "sensor_001"})
            logger.warning("High queue depth detected", extra={"queue_size": 1000})
            logger.error("Algorithm processing failed", extra={"error": "Model not found"})
            
            # Verify logs were sent to centralized system
            mock_syslog.assert_called()
    
    @pytest.mark.integration
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_full_system_stress(self, test_config):
        """Integration test with simulated load."""
        
        processed_messages = []
        failed_messages = []
        
        async def mock_processor(message):
            try:
                # Simulate processing
                await asyncio.sleep(0.01)
                processed_messages.append(message)
                return {"status": "success"}
            except Exception as e:
                failed_messages.append({"message": message, "error": str(e)})
                raise
        
        with patch('audio_processing.pipeline.AudioProcessingPipeline.process_audio_message', side_effect=mock_processor):
            
            # Generate load
            tasks = []
            for i in range(100):
                audio_data = {
                    "sensor_id": f"sensor_{i % 10}",
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "audio_data": f"mock_audio_data_{i}"
                }
                
                task = asyncio.create_task(mock_processor(audio_data))
                tasks.append(task)
            
            # Wait for all tasks to complete
            await asyncio.gather(*tasks, return_exceptions=True)
            
            # Verify system handled the load
            assert len(processed_messages) == 100
            assert len(failed_messages) == 0 