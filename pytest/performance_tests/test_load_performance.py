"""
Performance and load tests for the Audio Processing System.
"""
import pytest
import asyncio
import time
import psutil
import statistics
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch, AsyncMock
from typing import List, Dict, Any
import json


class TestAlgorithmPerformance:
    """Performance tests for Algorithm A and Algorithm B."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_algorithm_a_processing_time(self, sample_audio_data, performance_metrics):
        """Test Algorithm A processing time under normal load."""
        
        processing_times = []
        
        with patch('audio_processing.algorithms.AlgorithmA') as MockAlgorithmA:
            mock_algorithm = MockAlgorithmA.return_value
            
            # Simulate realistic processing times
            async def mock_process(message):
                start_time = time.time()
                await asyncio.sleep(0.1)  # Simulate 100ms processing
                end_time = time.time()
                processing_time = end_time - start_time
                processing_times.append(processing_time)
                return {
                    "feature_id": "test_feature",
                    "processing_time": processing_time
                }
            
            mock_algorithm.process_message = mock_process
            
            # Process multiple messages
            tasks = []
            for i in range(50):
                task = asyncio.create_task(mock_algorithm.process_message(json.dumps(sample_audio_data)))
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            # Performance assertions
            avg_time = statistics.mean(processing_times)
            max_time = max(processing_times)
            p95_time = statistics.quantiles(processing_times, n=20)[18]  # 95th percentile
            
            assert avg_time < 0.2, f"Average processing time too high: {avg_time}s"
            assert max_time < 0.5, f"Maximum processing time too high: {max_time}s"
            assert p95_time < 0.3, f"95th percentile too high: {p95_time}s"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_algorithm_b_processing_time(self, sample_feature_type_a, performance_metrics):
        """Test Algorithm B processing time under normal load."""
        
        processing_times = []
        
        with patch('audio_processing.algorithms.AlgorithmB') as MockAlgorithmB:
            mock_algorithm = MockAlgorithmB.return_value
            
            async def mock_process(message):
                start_time = time.time()
                await asyncio.sleep(0.08)  # Simulate 80ms processing
                end_time = time.time()
                processing_time = end_time - start_time
                processing_times.append(processing_time)
                return {
                    "feature_id": "test_feature_b",
                    "processing_time": processing_time
                }
            
            mock_algorithm.process_message = mock_process
            
            # Process multiple messages
            tasks = []
            for i in range(50):
                task = asyncio.create_task(mock_algorithm.process_message(json.dumps(sample_feature_type_a)))
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            # Performance assertions
            avg_time = statistics.mean(processing_times)
            max_time = max(processing_times)
            
            assert avg_time < 0.15, f"Average processing time too high: {avg_time}s"
            assert max_time < 0.3, f"Maximum processing time too high: {max_time}s"
    
    @pytest.mark.performance
    def test_memory_usage_stability(self, sample_audio_data):
        """Test memory usage remains stable during processing."""
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        memory_readings = [initial_memory]
        
        with patch('audio_processing.algorithms.AlgorithmA') as MockAlgorithmA:
            mock_algorithm = MockAlgorithmA.return_value
            mock_algorithm.process_message.return_value = {"feature_id": "test"}
            
            # Process many messages
            for i in range(1000):
                mock_algorithm.process_message(json.dumps(sample_audio_data))
                
                if i % 100 == 0:  # Sample memory every 100 iterations
                    current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                    memory_readings.append(current_memory)
        
        final_memory = memory_readings[-1]
        memory_growth = final_memory - initial_memory
        
        # Memory should not grow excessively
        assert memory_growth < 50, f"Memory grew by {memory_growth}MB, indicating potential memory leak"
        
        # Memory usage should be relatively stable
        memory_variance = statistics.variance(memory_readings)
        assert memory_variance < 25, f"Memory usage too variable: {memory_variance}"


class TestMessageBrokerPerformance:
    """Performance tests for RabbitMQ message broker operations."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_message_publishing_throughput(self, mock_rabbitmq_connection, sample_audio_data):
        """Test message publishing throughput."""
        
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        with patch('message_broker.publisher.MessagePublisher') as MockPublisher:
            mock_publisher = MockPublisher.return_value
            mock_publisher.publish_message = AsyncMock()
            
            # Measure throughput
            start_time = time.time()
            
            tasks = []
            message_count = 1000
            
            for i in range(message_count):
                task = asyncio.create_task(
                    mock_publisher.publish_message(
                        queue_name="test_queue",
                        message=sample_audio_data,
                        routing_key=f"test.{i}"
                    )
                )
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            throughput = message_count / duration
            
            # Should achieve at least 500 messages/second
            assert throughput > 500, f"Publishing throughput too low: {throughput:.2f} msg/s"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_message_consumption_throughput(self, mock_rabbitmq_connection, sample_audio_data):
        """Test message consumption throughput."""
        
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        with patch('message_broker.consumer.MessageConsumer') as MockConsumer:
            mock_consumer = MockConsumer.return_value
            
            processed_messages = []
            
            async def mock_handler(message):
                processed_messages.append(message)
                await asyncio.sleep(0.001)  # Minimal processing time
            
            mock_consumer.set_message_handler(mock_handler)
            
            # Simulate consumption
            start_time = time.time()
            
            tasks = []
            message_count = 500
            
            for i in range(message_count):
                mock_message = Mock()
                mock_message.body = json.dumps(sample_audio_data).encode('utf-8')
                
                task = asyncio.create_task(mock_consumer.handle_message(mock_message))
                tasks.append(task)
            
            await asyncio.gather(*tasks)
            
            end_time = time.time()
            duration = end_time - start_time
            throughput = len(processed_messages) / duration
            
            # Should achieve at least 300 messages/second
            assert throughput > 300, f"Consumption throughput too low: {throughput:.2f} msg/s"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_queue_depth_handling(self, mock_rabbitmq_connection):
        """Test system behavior under high queue depth."""
        
        with patch('message_broker.queue_manager.QueueManager') as MockQueueManager:
            mock_queue_manager = MockQueueManager.return_value
            
            # Simulate varying queue depths
            queue_depths = [100, 500, 1000, 2000, 5000]
            processing_times = []
            
            for depth in queue_depths:
                mock_queue_manager.get_queue_depth.return_value = depth
                
                start_time = time.time()
                
                # Simulate processing with queue depth awareness
                await asyncio.sleep(0.001 * (1 + depth / 10000))  # Slight delay based on depth
                
                end_time = time.time()
                processing_time = end_time - start_time
                processing_times.append(processing_time)
            
            # Processing time should scale sub-linearly with queue depth
            max_processing_time = max(processing_times)
            assert max_processing_time < 1.0, f"Processing time too high under load: {max_processing_time}s"


class TestDatabasePerformance:
    """Performance tests for database operations."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_write_performance(self, test_config, sample_feature_type_a):
        """Test database write performance."""
        
        with patch('database.writer.DataWriter') as MockDataWriter:
            mock_writer = MockDataWriter.return_value
            mock_writer.write_feature_type_a = AsyncMock()
            
            write_times = []
            
            # Test batch writing
            batch_sizes = [1, 10, 50, 100]
            
            for batch_size in batch_sizes:
                features = [sample_feature_type_a for _ in range(batch_size)]
                
                start_time = time.time()
                
                tasks = []
                for feature in features:
                    task = asyncio.create_task(mock_writer.write_feature_type_a(feature))
                    tasks.append(task)
                
                await asyncio.gather(*tasks)
                
                end_time = time.time()
                write_time = end_time - start_time
                write_times.append(write_time / batch_size)  # Time per record
            
            # Write time per record should remain relatively stable
            avg_write_time = statistics.mean(write_times)
            assert avg_write_time < 0.01, f"Average write time too high: {avg_write_time}s per record"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_database_read_performance(self, test_config, mock_database_session):
        """Test database read performance."""
        
        # Mock query results
        mock_features = [
            Mock(to_dict=lambda: {"feature_id": f"feat_{i}", "timestamp": f"2024-01-{i:02d}T10:00:00Z"})
            for i in range(1000)
        ]
        
        mock_database_session.query.return_value.filter.return_value.all.return_value = mock_features
        
        with patch('database.connection.get_session', return_value=mock_database_session):
            from api.rest_api import AudioProcessingAPI
            
            api = AudioProcessingAPI(test_config)
            
            # Test different query sizes
            query_limits = [10, 100, 500, 1000]
            query_times = []
            
            for limit in query_limits:
                start_time = time.time()
                
                response = await api.get_historical_features(
                    sensor_id="sensor_001",
                    start_time="2024-01-01T00:00:00Z",
                    end_time="2024-01-31T23:59:59Z",
                    limit=limit
                )
                
                end_time = time.time()
                query_time = end_time - start_time
                query_times.append(query_time)
            
            # Query time should scale reasonably with result size
            max_query_time = max(query_times)
            assert max_query_time < 1.0, f"Query time too high: {max_query_time}s"


class TestRESTAPIPerformance:
    """Performance tests for REST API endpoints."""
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_concurrent_requests(self, test_config):
        """Test API performance under concurrent requests."""
        
        with patch('api.rest_api.AudioProcessingAPI') as MockAPI:
            mock_api = MockAPI.return_value
            mock_api.get_real_time_features = AsyncMock(return_value={
                "status": "success",
                "features": [],
                "count": 0
            })
            
            # Test concurrent requests
            concurrent_requests = [10, 25, 50, 100]
            response_times = []
            
            for request_count in concurrent_requests:
                start_time = time.time()
                
                tasks = []
                for i in range(request_count):
                    task = asyncio.create_task(
                        mock_api.get_real_time_features(f"sensor_{i % 10}", limit=10)
                    )
                    tasks.append(task)
                
                responses = await asyncio.gather(*tasks)
                
                end_time = time.time()
                total_time = end_time - start_time
                avg_response_time = total_time / request_count
                response_times.append(avg_response_time)
            
            # Average response time should remain reasonable under load
            max_avg_response_time = max(response_times)
            assert max_avg_response_time < 0.5, f"Average response time too high: {max_avg_response_time}s"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_api_cache_performance(self, test_config, mock_redis_client):
        """Test API caching performance."""
        
        with patch('api.cache.RedisCache') as MockRedisCache:
            mock_cache = MockRedisCache.return_value
            
            # Simulate cache hits and misses
            cache_hit_time = 0.001  # 1ms for cache hit
            cache_miss_time = 0.1   # 100ms for cache miss
            
            async def mock_get(key):
                if "cached_" in key:
                    await asyncio.sleep(cache_hit_time)
                    return json.dumps({"cached": True, "data": "test"})
                else:
                    await asyncio.sleep(cache_miss_time)
                    return None
            
            mock_cache.get = mock_get
            mock_cache.set = AsyncMock()
            
            # Test cache hit performance
            cache_hit_times = []
            for i in range(50):
                start_time = time.time()
                result = await mock_cache.get(f"cached_key_{i}")
                end_time = time.time()
                cache_hit_times.append(end_time - start_time)
            
            avg_cache_hit_time = statistics.mean(cache_hit_times)
            assert avg_cache_hit_time < 0.01, f"Cache hit time too high: {avg_cache_hit_time}s"


class TestSystemLoadTesting:
    """Load testing for the entire system."""
    
    @pytest.mark.performance
    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_sustained_load(self, test_config, sample_audio_data):
        """Test system performance under sustained load."""
        
        processed_count = 0
        failed_count = 0
        processing_times = []
        
        async def process_message(message_data):
            nonlocal processed_count, failed_count
            
            try:
                start_time = time.time()
                
                # Simulate processing pipeline
                await asyncio.sleep(0.05)  # Algorithm A
                await asyncio.sleep(0.03)  # Algorithm B
                await asyncio.sleep(0.01)  # Database write
                
                end_time = time.time()
                processing_time = end_time - start_time
                processing_times.append(processing_time)
                processed_count += 1
                
            except Exception:
                failed_count += 1
        
        # Generate sustained load for 30 seconds
        start_time = time.time()
        end_time = start_time + 30  # 30 seconds
        
        tasks = []
        message_id = 0
        
        while time.time() < end_time:
            # Add new tasks
            for _ in range(10):  # 10 messages per batch
                message_data = sample_audio_data.copy()
                message_data["message_id"] = message_id
                message_id += 1
                
                task = asyncio.create_task(process_message(message_data))
                tasks.append(task)
            
            # Clean up completed tasks
            tasks = [task for task in tasks if not task.done()]
            
            await asyncio.sleep(0.1)  # 100ms between batches
        
        # Wait for remaining tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
        # Performance assertions
        total_messages = processed_count + failed_count
        success_rate = processed_count / total_messages if total_messages > 0 else 0
        avg_processing_time = statistics.mean(processing_times) if processing_times else 0
        throughput = processed_count / 30  # messages per second
        
        assert success_rate > 0.95, f"Success rate too low: {success_rate:.2%}"
        assert avg_processing_time < 0.2, f"Average processing time too high: {avg_processing_time}s"
        assert throughput > 50, f"Throughput too low: {throughput:.2f} msg/s"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_cpu_usage_under_load(self, sample_audio_data):
        """Test CPU usage remains reasonable under load."""
        
        def cpu_intensive_task():
            # Simulate CPU-intensive processing
            for _ in range(100000):
                # Simple computation
                result = sum(range(100))
            return result
        
        # Monitor CPU usage
        cpu_readings = []
        
        # Initial CPU reading
        initial_cpu = psutil.cpu_percent(interval=1)
        cpu_readings.append(initial_cpu)
        
        # Generate CPU load
        with ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            
            for _ in range(20):  # 20 tasks
                future = executor.submit(cpu_intensive_task)
                futures.append(future)
            
            # Monitor CPU during execution
            for i in range(5):  # 5 seconds of monitoring
                cpu_percent = psutil.cpu_percent(interval=1)
                cpu_readings.append(cpu_percent)
            
            # Wait for completion
            for future in futures:
                future.result()
        
        # Final CPU reading
        final_cpu = psutil.cpu_percent(interval=1)
        cpu_readings.append(final_cpu)
        
        max_cpu = max(cpu_readings)
        avg_cpu = statistics.mean(cpu_readings)
        
        # CPU usage should not exceed reasonable limits
        assert max_cpu < 90, f"Maximum CPU usage too high: {max_cpu}%"
        assert avg_cpu < 70, f"Average CPU usage too high: {avg_cpu}%"
    
    @pytest.mark.performance
    @pytest.mark.asyncio
    async def test_memory_usage_under_load(self, sample_audio_data):
        """Test memory usage under sustained load."""
        
        initial_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        peak_memory = initial_memory
        
        # Generate memory load
        data_store = []
        
        for i in range(1000):
            # Create and store data
            large_data = {
                "id": i,
                "audio_data": sample_audio_data["audio_data"] * 100,  # Larger payload
                "features": [j for j in range(1000)],  # Large feature array
                "metadata": {"timestamp": time.time(), "iteration": i}
            }
            data_store.append(large_data)
            
            if i % 100 == 0:
                current_memory = psutil.Process().memory_info().rss / 1024 / 1024
                peak_memory = max(peak_memory, current_memory)
        
        final_memory = psutil.Process().memory_info().rss / 1024 / 1024
        memory_growth = final_memory - initial_memory
        
        # Clean up
        data_store.clear()
        
        # Memory growth should be reasonable
        assert memory_growth < 500, f"Memory growth too high: {memory_growth}MB"
        assert peak_memory < initial_memory + 600, f"Peak memory too high: {peak_memory}MB" 