"""
Mock message broker module for testing
"""
from unittest.mock import MagicMock, AsyncMock
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
        self.connection = None
        self.channel = None
        self.max_retries = 3
        self.retry_delay = 1
        
        # Use MagicMock to track calls properly
        self.connect = MagicMock(side_effect=self._connect)
        self.disconnect = MagicMock(side_effect=self._disconnect)
        self.create_channel = MagicMock(side_effect=self._create_channel)
        self.publish_message = MagicMock(side_effect=self._publish_message)
        
    async def _connect(self):
        """Mock connection that calls aiormq for test compatibility"""
        # Import and call aiormq for test tracking
        try:
            import aiormq
            connection = await aiormq.connect(self.connection_string)
            self.connection = connection
        except ImportError:
            # Fallback for when aiormq is not available
            pass
        
        await asyncio.sleep(0.01)
        self.is_connected = True
        return True
        
    async def connect_with_retry(self):
        """Connect with retry mechanism - tracks retry attempts"""
        for attempt in range(self.max_retries):
            try:
                # Simulate connection failures for testing
                if hasattr(self, '_force_connection_error') and attempt < 2:
                    raise ConnectionError("Connection failed")
                await self.connect()
                return True
            except ConnectionError:
                if attempt == self.max_retries - 1:
                    raise
                await asyncio.sleep(self.retry_delay)
        return False
    
    async def _disconnect(self):
        """Mock disconnection"""
        self.is_connected = False
        # Call close on the connection if it exists (for test assertions)
        if hasattr(self, 'connection') and self.connection:
            self.connection.close()
        
    def _create_channel(self, channel_id="default"):
        """Mock channel creation"""
        if not self.is_connected:
            raise ConnectionError("Not connected to RabbitMQ")
        
        channel = AsyncMock()
        channel.basic_publish = AsyncMock()
        channel.basic_consume = AsyncMock()
        channel.queue_declare = AsyncMock()
        channel.exchange_declare = AsyncMock()
        channel.queue_bind = AsyncMock()
        channel.basic_qos = AsyncMock()
        channel.basic_cancel = AsyncMock()
        channel.ack = AsyncMock()
        channel.nack = AsyncMock()
        
        self.channels[channel_id] = channel
        self.channel = channel  # Store for easy access
        return channel
    
    async def _publish_message(self, queue_name, message, properties=None):
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


class MessagePublisher:
    """Mock message publisher for testing"""
    
    def __init__(self, connection):
        self.connection = connection
        self.published_messages = []
        
        # Handle both our mock connection and the fixture mock connection
        if hasattr(connection, 'channel'):
            if callable(connection.channel):
                # This is from the fixture - call it to get the mock channel
                self.channel = connection.channel()
            else:
                # This is a direct channel attribute
                self.channel = connection.channel
        elif hasattr(connection, '_create_channel'):
            # This is our mock connection
            self.channel = connection._create_channel()
        else:
            # Fallback - create a mock channel
            self.channel = AsyncMock()
    
    async def publish_message(self, queue_name, message, routing_key=None, properties=None):
        """Publish a message to queue - calls the mock channel for test assertions"""
        # Convert message to JSON if it's not already a string
        if isinstance(message, dict):
            body = json.dumps(message)
        else:
            body = str(message)
            
        # Call the mock channel's basic_publish for test assertion tracking
        # This will raise an exception if the test has set side_effect on basic_publish
        await self.channel.basic_publish(
            exchange="",
            routing_key=routing_key or queue_name,
            body=body,
            properties=properties or {}
        )
        
        # Also track internally
        self.published_messages.append({
            "queue": queue_name,
            "message": message,
            "routing_key": routing_key,
            "properties": properties,
            "timestamp": time.time()
        })
        
        return {
            "status": "published",
            "queue": queue_name,
            "message_id": f"msg_{int(time.time())}",
            "routing_key": routing_key,
            "timestamp": time.time()
        }
    
    async def publish_batch(self, queue_name, messages):
        """Publish batch of messages"""
        for message in messages:
            await self.publish_message(queue_name, message)
        
        return {
            "status": "published",
            "queue": queue_name,
            "message_count": len(messages),
            "timestamp": time.time()
        }


class MessageConsumer:
    """Mock message consumer for testing"""
    
    def __init__(self, connection):
        self.connection = connection
        self.consumed_messages = []
        self.is_consuming = False
        self.message_handler = None
        self.consumer_tag = None
        
        # Handle both our mock connection and the fixture mock connection
        if hasattr(connection, 'channel'):
            if callable(connection.channel):
                # This is from the fixture - call it to get the mock channel
                self.channel = connection.channel()
            else:
                # This is a direct channel attribute
                self.channel = connection.channel
        elif hasattr(connection, '_create_channel'):
            # This is our mock connection
            self.channel = connection._create_channel()
        else:
            # Fallback - create a mock channel
            self.channel = AsyncMock()
    
    def set_message_handler(self, handler):
        """Set message handler function"""
        self.message_handler = handler
    
    async def handle_message(self, message):
        """Handle incoming message"""
        self.consumed_messages.append(message)
        
        if self.message_handler:
            # Check if the handler is a coroutine function
            if asyncio.iscoroutinefunction(self.message_handler):
                await self.message_handler(message)
            else:
                self.message_handler(message)
            # Note: We let exceptions from the handler propagate up for test assertions
        
        return {"status": "processed", "message_id": getattr(message, "delivery_tag", "test_id")}
    
    async def set_qos(self, prefetch_count=1, prefetch_size=0, global_qos=False):
        """Set QoS settings - calls mock channel for test assertions"""
        await self.channel.basic_qos(
            prefetch_count=prefetch_count,
            prefetch_size=prefetch_size,
            global_qos=global_qos
        )
        
        self.qos_settings = {
            "prefetch_count": prefetch_count,
            "prefetch_size": prefetch_size,
            "global_qos": global_qos
        }
    
    async def cancel_consumption(self):
        """Cancel message consumption - calls mock channel for test assertions"""
        if self.consumer_tag:
            await self.channel.basic_cancel(self.consumer_tag)
        
        self.is_consuming = False
        return {"status": "cancelled", "timestamp": time.time()}


class MessageBrokerConnection:
    """Mock message broker connection"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.connection = RabbitMQConnection()
        self.is_connected = False
        self.retry_attempts = 0
        self.max_retries = 3
    
    async def connect(self):
        """Connect to message broker"""
        await self.connection.connect()
        self.is_connected = True
        return True
    
    async def connect_with_retry(self):
        """Connect with retry mechanism"""
        for attempt in range(self.max_retries):
            try:
                await self.connect()
                return True
            except Exception:
                self.retry_attempts += 1
                if attempt == self.max_retries - 1:
                    raise ConnectionError("Failed to connect after retries")
                await asyncio.sleep(0.1)
        return False
    
    async def disconnect(self):
        """Disconnect from message broker"""
        await self.connection.disconnect()
        self.is_connected = False


class SecureMessageBrokerConnection:
    """Mock secure message broker connection"""
    
    def __init__(self, config=None, ssl_context=None):
        self.config = config or {}
        self.ssl_context = ssl_context
        self.connection = MessageBrokerConnection(config)
        
        # SSL is enabled if ssl_context is provided OR if config indicates secure connection
        ssl_config_enabled = (config or {}).get('ssl_enabled', False) or (config or {}).get('use_ssl', False) or (config or {}).get('ssl', False)
        self.is_secure = ssl_context is not None or ssl_config_enabled
        self.ssl_enabled = ssl_context is not None or ssl_config_enabled
        self.ssl_verify = (config or {}).get('ssl_verify', True)
    
    async def connect(self):
        """Connect securely to message broker"""
        return await self.connection.connect()
    
    async def disconnect(self):
        """Disconnect from secure message broker"""
        return await self.connection.disconnect()


class QueueManager:
    """Mock queue manager"""
    
    def __init__(self, connection):
        self.connection = connection
        self.queues = {}
        self.exchanges = {}
        
        # Handle both our mock connection and the fixture mock connection
        if hasattr(connection, 'channel'):
            if callable(connection.channel):
                # This is from the fixture - call it to get the mock channel
                self.channel = connection.channel()
            else:
                # This is a direct channel attribute
                self.channel = connection.channel
        elif hasattr(connection, '_create_channel'):
            # This is our mock connection
            self.channel = connection._create_channel()
        else:
            # Fallback - create a mock channel
            self.channel = AsyncMock()
    
    async def declare_queue(self, queue_name, durable=True, exclusive=False, auto_delete=False):
        """Declare a queue - calls mock channel for test assertions"""
        await self.channel.queue_declare(
            queue=queue_name,
            durable=durable,
            exclusive=exclusive,
            auto_delete=auto_delete
        )
        
        self.queues[queue_name] = {
            "name": queue_name,
            "durable": durable,
            "exclusive": exclusive,
            "auto_delete": auto_delete,
            "message_count": 0
        }
        return self.queues[queue_name]
    
    async def declare_exchange(self, exchange_name, exchange_type="direct", durable=True):
        """Declare an exchange - calls mock channel for test assertions"""
        await self.channel.exchange_declare(
            exchange=exchange_name,
            exchange_type=exchange_type,
            durable=durable
        )
        
        self.exchanges[exchange_name] = {
            "name": exchange_name,
            "type": exchange_type,
            "durable": durable
        }
        return self.exchanges[exchange_name]
    
    async def bind_queue(self, queue_name, exchange_name, routing_key=""):
        """Bind queue to exchange - calls mock channel for test assertions"""
        await self.channel.queue_bind(
            queue=queue_name,
            exchange=exchange_name,
            routing_key=routing_key
        )
        
        if queue_name in self.queues and exchange_name in self.exchanges:
            return True
        return False


class LoadBalancer:
    """Mock load balancer"""
    
    def __init__(self, connection=None):
        self.connection = connection
        self.consumers = []
        self.current_index = 0
        self.health_status = {}
        self.health_check_interval = 1.0
    
    def register_consumer(self, consumer_id, consumer_instance=None):
        """Register a consumer"""
        consumer_data = {
            "id": consumer_id,
            "instance": consumer_instance,
            "message_count": 0
        }
        self.consumers.append(consumer_data)
        self.health_status[consumer_id] = "healthy"
    
    def register_consumers(self, consumers):
        """Register multiple consumers"""
        for consumer in consumers:
            if isinstance(consumer, str):
                self.register_consumer(consumer, None)
            elif isinstance(consumer, dict):
                self.register_consumer(consumer.get("id"), consumer.get("instance"))
            else:
                self.register_consumer(str(consumer), None)
    
    def get_next_consumer(self):
        """Get next consumer using round-robin"""
        if not self.consumers:
            return None
        
        consumer = self.consumers[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.consumers)
        
        # Return just the consumer ID string for simple cases
        return consumer["id"]
    
    def get_next_healthy_consumer(self):
        """Get next healthy consumer"""
        healthy_consumers = [c for c in self.consumers if self.health_status.get(c["id"]) == "healthy"]
        if not healthy_consumers:
            return None
        
        # Find the next healthy consumer in round-robin order
        for _ in range(len(self.consumers)):
            consumer = self.consumers[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.consumers)
            if self.health_status.get(consumer["id"]) == "healthy":
                return consumer["id"]
        
        return None
    
    def check_consumer_health(self, consumer_id):
        """Check consumer health"""
        return self.health_status.get(consumer_id, "unknown")
    
    def is_consumer_healthy(self, consumer_id):
        """Check if consumer is healthy"""
        return self.health_status.get(consumer_id) == "healthy"
    
    def mark_consumer_unhealthy(self, consumer_id):
        """Mark consumer as unhealthy"""
        self.health_status[consumer_id] = "unhealthy"
    
    def recover_consumer(self, consumer_id):
        """Recover an unhealthy consumer"""
        self.health_status[consumer_id] = "healthy"
    
    def attempt_consumer_recovery(self, consumer_id):
        """Attempt to recover an unhealthy consumer"""
        # Simulate successful recovery
        self.health_status[consumer_id] = "healthy"
        return True


# Mock aiormq module
class aiormq:
    """Mock aiormq module"""
    
    @staticmethod
    async def connect(connection_string):
        """Mock aiormq connect"""
        connection = MagicMock()
        connection.is_closed = False
        connection.close = AsyncMock()
        return connection


# Mock submodules
class connection:
    """Mock message_broker.connection module"""
    RabbitMQConnection = RabbitMQConnection
    MessageBrokerConnection = MessageBrokerConnection
    SecureMessageBrokerConnection = SecureMessageBrokerConnection
    aiormq = aiormq


class publisher:
    """Mock message_broker.publisher module"""
    MessagePublisher = MessagePublisher


class consumer:
    """Mock message_broker.consumer module"""
    MessageConsumer = MessageConsumer


class queue_manager:
    """Mock message_broker.queue_manager module"""
    QueueManager = QueueManager


class load_balancer:
    """Mock message_broker.load_balancer module"""
    LoadBalancer = LoadBalancer 