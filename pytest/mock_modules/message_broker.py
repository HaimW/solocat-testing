"""
Mock message broker module for testing
"""
from unittest.mock import Mock, AsyncMock
import asyncio
import json
import time


class RabbitMQConnection:
    """Mock RabbitMQ connection for testing"""
    
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or "amqp://localhost"
        self.is_connected = False
        self.channels = {}
        self.queues = {}
        
    async def connect(self):
        """Mock connection"""
        await asyncio.sleep(0.01)  # Simulate connection time
        self.is_connected = True
        return True
    
    async def disconnect(self):
        """Mock disconnection"""
        self.is_connected = False
        
    def create_channel(self, channel_id="default"):
        """Mock channel creation"""
        if not self.is_connected:
            raise ConnectionError("Not connected to RabbitMQ")
        
        channel = Mock()
        channel.basic_publish = AsyncMock()
        channel.basic_consume = AsyncMock()
        channel.queue_declare = AsyncMock()
        channel.exchange_declare = AsyncMock()
        
        self.channels[channel_id] = channel
        return channel
    
    async def publish_message(self, queue_name, message, properties=None):
        """Mock message publishing"""
        if not self.is_connected:
            raise ConnectionError("Not connected to RabbitMQ")
        
        if queue_name not in self.queues:
            self.queues[queue_name] = []
        
        message_data = {
            'body': message if isinstance(message, str) else json.dumps(message),
            'properties': properties or {},
            'timestamp': time.time()
        }
        
        self.queues[queue_name].append(message_data)
        return True
    
    async def consume_messages(self, queue_name, callback):
        """Mock message consumption"""
        if not self.is_connected:
            raise ConnectionError("Not connected to RabbitMQ")
        
        messages = self.queues.get(queue_name, [])
        for message in messages:
            await callback(message)
        
        # Clear consumed messages
        if queue_name in self.queues:
            self.queues[queue_name] = []


class MessagePublisher:
    """Mock message publisher for testing"""
    
    def __init__(self, connection):
        self.connection = connection
        self.published_messages = []
    
    async def publish_audio_message(self, audio_data, routing_key="audio.raw"):
        """Mock audio message publishing"""
        message = {
            'audio_id': f"audio_{int(time.time())}",
            'audio_data': audio_data,
            'timestamp': time.time(),
            'routing_key': routing_key
        }
        
        await self.connection.publish_message("audio_queue", message)
        self.published_messages.append(message)
        return message['audio_id']
    
    async def publish_feature_message(self, features, routing_key="features.processed"):
        """Mock feature message publishing"""
        message = {
            'feature_id': f"feature_{int(time.time())}",
            'features': features,
            'timestamp': time.time(),
            'routing_key': routing_key
        }
        
        await self.connection.publish_message("features_queue", message)
        self.published_messages.append(message)
        return message['feature_id']


class MessageConsumer:
    """Mock message consumer for testing"""
    
    def __init__(self, connection):
        self.connection = connection
        self.consumed_messages = []
        self.is_consuming = False
    
    async def start_consuming(self, queue_name, callback):
        """Mock message consumption start"""
        self.is_consuming = True
        
        async def message_handler(message):
            self.consumed_messages.append(message)
            await callback(message)
        
        await self.connection.consume_messages(queue_name, message_handler)
    
    def stop_consuming(self):
        """Mock consumption stop"""
        self.is_consuming = False


# Mock connection module
connection = Mock()
connection.RabbitMQConnection = RabbitMQConnection
connection.MessagePublisher = MessagePublisher
connection.MessageConsumer = MessageConsumer 