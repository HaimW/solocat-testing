"""
Unit tests for RabbitMQ message broker interactions and queue management.
"""
import pytest
import json
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from typing import Dict, Any


class TestRabbitMQConnection:
    """Unit tests for RabbitMQ connection management."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_connection_establishment(self, test_config):
        """Test RabbitMQ connection establishment."""
        # Mock the message broker connection module
        with patch('message_broker.connection.aiormq') as mock_aiormq:
            mock_connection = AsyncMock()
            mock_aiormq.connect.return_value = mock_connection
            
            from message_broker.connection import MessageBrokerConnection
            
            broker = MessageBrokerConnection(test_config["rabbitmq"])
            await broker.connect()
            
            assert broker.is_connected is True
            mock_aiormq.connect.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_connection_failure(self, test_config):
        """Test RabbitMQ connection failure handling."""
        with patch('message_broker.connection.aiormq') as mock_aiormq:
            mock_aiormq.connect.side_effect = ConnectionError("Connection failed")
            
            from message_broker.connection import MessageBrokerConnection
            
            broker = MessageBrokerConnection(test_config["rabbitmq"])
            
            with pytest.raises(ConnectionError):
                await broker.connect()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_connection_retry_mechanism(self, test_config):
        """Test connection retry mechanism."""
        with patch('message_broker.connection.aiormq') as mock_aiormq, \
             patch('asyncio.sleep') as mock_sleep:
            
            # First two attempts fail, third succeeds
            mock_connection = AsyncMock()
            mock_aiormq.connect.side_effect = [
                ConnectionError("Connection failed"),
                ConnectionError("Connection failed"),
                mock_connection
            ]
            
            from message_broker.connection import MessageBrokerConnection
            
            broker = MessageBrokerConnection(test_config["rabbitmq"])
            broker.max_retries = 3
            broker.retry_delay = 1
            
            await broker.connect_with_retry()
            
            assert broker.is_connected is True
            assert mock_aiormq.connect.call_count == 3
            assert mock_sleep.call_count == 2
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_graceful_disconnection(self, mock_rabbitmq_connection):
        """Test graceful connection disconnection."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.connection import MessageBrokerConnection
        
        broker = MessageBrokerConnection({})
        broker.connection = mock_connection
        broker.channel = mock_channel
        broker.is_connected = True
        
        await broker.disconnect()
        
        mock_connection.close.assert_called_once()
        assert broker.is_connected is False


class TestQueueManagement:
    """Unit tests for queue management operations."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_queue_declaration(self, mock_rabbitmq_connection):
        """Test queue declaration with proper parameters."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.queue_manager import QueueManager
        
        queue_manager = QueueManager(mock_connection)
        
        await queue_manager.declare_queue("test_queue", durable=True, exclusive=False)
        
        mock_channel.queue_declare.assert_called_once_with(
            queue="test_queue",
            durable=True,
            exclusive=False,
            auto_delete=False
        )
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_queue_binding(self, mock_rabbitmq_connection):
        """Test queue binding to exchange."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.queue_manager import QueueManager
        
        queue_manager = QueueManager(mock_connection)
        
        await queue_manager.bind_queue("test_queue", "test_exchange", "routing.key")
        
        mock_channel.queue_bind.assert_called_once_with(
            queue="test_queue",
            exchange="test_exchange",
            routing_key="routing.key"
        )
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_exchange_declaration(self, mock_rabbitmq_connection):
        """Test exchange declaration."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.queue_manager import QueueManager
        
        queue_manager = QueueManager(mock_connection)
        
        await queue_manager.declare_exchange("test_exchange", "topic", durable=True)
        
        mock_channel.exchange_declare.assert_called_once_with(
            exchange="test_exchange",
            exchange_type="topic",
            durable=True
        )


class TestMessagePublisher:
    """Unit tests for message publishing functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_publish_audio_message(self, mock_rabbitmq_connection, sample_audio_data):
        """Test publishing audio message to queue."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.publisher import MessagePublisher
        
        publisher = MessagePublisher(mock_connection)
        
        await publisher.publish_message(
            queue_name="audio_queue",
            message=sample_audio_data,
            routing_key="audio.sensor.001"
        )
        
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        
        assert call_args[1]["routing_key"] == "audio.sensor.001"
        assert json.loads(call_args[1]["body"]) == sample_audio_data
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_publish_feature_message(self, mock_rabbitmq_connection, sample_feature_type_a):
        """Test publishing feature message to queue."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.publisher import MessagePublisher
        
        publisher = MessagePublisher(mock_connection)
        
        await publisher.publish_message(
            queue_name="features_queue",
            message=sample_feature_type_a,
            routing_key="features.type_a"
        )
        
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        
        assert call_args[1]["routing_key"] == "features.type_a"
        published_message = json.loads(call_args[1]["body"])
        assert published_message["feature_id"] == sample_feature_type_a["feature_id"]
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_publish_with_message_properties(self, mock_rabbitmq_connection, sample_audio_data):
        """Test publishing message with custom properties."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.publisher import MessagePublisher
        
        publisher = MessagePublisher(mock_connection)
        
        properties = {
            "delivery_mode": 2,  # Persistent
            "priority": 5,
            "timestamp": 1642251000,
            "headers": {"sensor_type": "microphone"}
        }
        
        await publisher.publish_message(
            queue_name="audio_queue",
            message=sample_audio_data,
            properties=properties
        )
        
        mock_channel.basic_publish.assert_called_once()
        call_args = mock_channel.basic_publish.call_args
        
        assert call_args[1]["properties"]["delivery_mode"] == 2
        assert call_args[1]["properties"]["priority"] == 5
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_publish_failure_handling(self, mock_rabbitmq_connection, sample_audio_data):
        """Test handling of publish failures."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        mock_channel.basic_publish.side_effect = Exception("Publish failed")
        
        from message_broker.publisher import MessagePublisher
        
        publisher = MessagePublisher(mock_connection)
        
        with pytest.raises(Exception, match="Publish failed"):
            await publisher.publish_message("audio_queue", sample_audio_data)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_batch_publish(self, mock_rabbitmq_connection, sample_audio_data):
        """Test batch publishing of multiple messages."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.publisher import MessagePublisher
        
        publisher = MessagePublisher(mock_connection)
        
        messages = [sample_audio_data for _ in range(5)]
        
        await publisher.publish_batch("audio_queue", messages)
        
        assert mock_channel.basic_publish.call_count == 5


class TestMessageConsumer:
    """Unit tests for message consumption functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_message_consumption(self, mock_rabbitmq_connection, sample_audio_data):
        """Test basic message consumption."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        # Mock incoming message
        mock_message = Mock()
        mock_message.body = json.dumps(sample_audio_data).encode('utf-8')
        mock_message.delivery_tag = 1
        
        from message_broker.consumer import MessageConsumer
        
        consumer = MessageConsumer(mock_connection)
        processed_messages = []
        
        async def message_handler(message):
            processed_messages.append(json.loads(message.body))
            await message.ack()
        
        consumer.set_message_handler(message_handler)
        
        # Simulate message consumption
        await consumer.handle_message(mock_message)
        
        assert len(processed_messages) == 1
        assert processed_messages[0] == sample_audio_data
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_message_acknowledgment(self, mock_rabbitmq_connection, sample_audio_data):
        """Test message acknowledgment after processing."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        mock_message = Mock()
        mock_message.body = json.dumps(sample_audio_data).encode('utf-8')
        mock_message.delivery_tag = 1
        mock_message.ack = AsyncMock()
        
        from message_broker.consumer import MessageConsumer
        
        consumer = MessageConsumer(mock_connection)
        
        async def message_handler(message):
            # Process message successfully
            await message.ack()
        
        consumer.set_message_handler(message_handler)
        await consumer.handle_message(mock_message)
        
        mock_message.ack.assert_called_once()
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_message_rejection(self, mock_rabbitmq_connection):
        """Test message rejection on processing failure."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        mock_message = Mock()
        mock_message.body = b"invalid json"
        mock_message.delivery_tag = 1
        mock_message.nack = AsyncMock()
        
        from message_broker.consumer import MessageConsumer
        
        consumer = MessageConsumer(mock_connection)
        
        async def failing_handler(message):
            raise ValueError("Processing failed")
        
        consumer.set_message_handler(failing_handler)
        
        with pytest.raises(ValueError):
            await consumer.handle_message(mock_message)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_consumer_prefetch_settings(self, mock_rabbitmq_connection):
        """Test consumer prefetch settings for load balancing."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.consumer import MessageConsumer
        
        consumer = MessageConsumer(mock_connection)
        await consumer.set_qos(prefetch_count=10, prefetch_size=0)
        
        mock_channel.basic_qos.assert_called_once_with(
            prefetch_count=10,
            prefetch_size=0,
            global_qos=False
        )
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_consumer_cancellation(self, mock_rabbitmq_connection):
        """Test consumer cancellation and cleanup."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.consumer import MessageConsumer
        
        consumer = MessageConsumer(mock_connection)
        consumer.consumer_tag = "test_consumer"
        
        await consumer.cancel_consumption()
        
        mock_channel.basic_cancel.assert_called_once_with("test_consumer")


class TestLoadBalancing:
    """Unit tests for load balancing functionality."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_round_robin_message_distribution(self, mock_rabbitmq_connection):
        """Test round-robin message distribution among consumers."""
        mock_connection, mock_channel = mock_rabbitmq_connection
        
        from message_broker.load_balancer import LoadBalancer
        
        load_balancer = LoadBalancer(mock_connection)
        
        # Simulate multiple consumers
        consumers = ["consumer_1", "consumer_2", "consumer_3"]
        load_balancer.register_consumers(consumers)
        
        # Test message distribution
        for i in range(9):  # 3 rounds of 3 consumers
            selected_consumer = load_balancer.get_next_consumer()
            expected_consumer = consumers[i % 3]
            assert selected_consumer == expected_consumer
    
    @pytest.mark.unit
    def test_consumer_health_monitoring(self):
        """Test consumer health monitoring."""
        from message_broker.load_balancer import LoadBalancer
        
        load_balancer = LoadBalancer(None)
        
        # Register consumers
        load_balancer.register_consumer("consumer_1")
        load_balancer.register_consumer("consumer_2")
        
        # Mark one as unhealthy
        load_balancer.mark_consumer_unhealthy("consumer_1")
        
        # Only healthy consumer should be selected
        for _ in range(5):
            selected = load_balancer.get_next_healthy_consumer()
            assert selected == "consumer_2"
    
    @pytest.mark.unit
    def test_auto_recovery_mechanism(self):
        """Test automatic recovery of unhealthy consumers."""
        from message_broker.load_balancer import LoadBalancer
        
        load_balancer = LoadBalancer(None)
        load_balancer.health_check_interval = 0.1  # Fast recovery for testing
        
        load_balancer.register_consumer("consumer_1")
        load_balancer.mark_consumer_unhealthy("consumer_1")
        
        # Simulate health check recovery
        load_balancer.attempt_consumer_recovery("consumer_1")
        
        assert load_balancer.is_consumer_healthy("consumer_1") is True 