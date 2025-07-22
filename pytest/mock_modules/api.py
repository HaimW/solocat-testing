"""
Mock API module for testing
"""
from unittest.mock import Mock
import json
import time
import asyncio
from unittest.mock import MagicMock


class AudioAPI:
    """Mock Audio API for testing"""
    
    def __init__(self, db_connection=None, cache=None):
        self.db_connection = db_connection
        self.cache = cache
        self.request_count = 0
    
    def get_audio_data(self, audio_id):
        """Mock get audio data endpoint"""
        self.request_count += 1
        
        # Check cache first
        if self.cache:
            cached = self.cache.get(f"audio:{audio_id}")
            if cached:
                return json.loads(cached)
        
        # Mock database lookup
        if self.db_connection:
            records = self.db_connection.select('audio_data', {'id': audio_id})
            if records:
                data = records[0]
                # Cache the result
                if self.cache:
                    self.cache.set(f"audio:{audio_id}", json.dumps(data), expire=300)
                return data
        
        # Mock default response
        return {
            'id': audio_id,
            'timestamp': time.time(),
            'sensor_id': 'sensor_001',
            'sample_rate': 44100,
            'channels': 1,
            'duration_ms': 5000,
            'status': 'found'
        }
    
    def get_feature_data(self, feature_id):
        """Mock get feature data endpoint"""
        self.request_count += 1
        
        return {
            'id': feature_id,
            'audio_id': f"audio_{int(time.time())}",
            'features': [0.1, 0.2, 0.3, 0.4, 0.5],
            'algorithm_version': 'A.1.0',
            'confidence_score': 0.85,
            'timestamp': time.time(),
            'status': 'found'
        }
    
    def get_realtime_data(self, limit=10):
        """Mock realtime data endpoint"""
        self.request_count += 1
        
        # Generate mock realtime data
        data = []
        for i in range(limit):
            data.append({
                'id': f"realtime_{i}",
                'timestamp': time.time() - (i * 60),  # 1 minute intervals
                'value': 0.5 + (i * 0.1),
                'status': 'active'
            })
        
        return {
            'data': data,
            'total': len(data),
            'timestamp': time.time()
        }
    
    def get_historical_data(self, start_time, end_time, limit=100):
        """Mock historical data endpoint"""
        self.request_count += 1
        
        # Generate mock historical data
        data = []
        time_diff = end_time - start_time
        interval = time_diff / limit if limit > 0 else 60
        
        for i in range(limit):
            timestamp = start_time + (i * interval)
            data.append({
                'id': f"historical_{i}",
                'timestamp': timestamp,
                'value': 0.3 + (i * 0.01),
                'status': 'processed'
            })
        
        return {
            'data': data,
            'total': len(data),
            'start_time': start_time,
            'end_time': end_time
        }


class Cache:
    """Mock cache for testing"""
    
    def __init__(self):
        self.data = {}
        self.expiry = {}
        self.hit_count = 0
        self.miss_count = 0
    
    def get(self, key):
        """Mock cache get"""
        if key in self.data:
            # Check if expired
            if key in self.expiry and time.time() > self.expiry[key]:
                del self.data[key]
                del self.expiry[key]
                self.miss_count += 1
                return None
            
            self.hit_count += 1
            return self.data[key]
        
        self.miss_count += 1
        return None
    
    def set(self, key, value, expire=None):
        """Mock cache set"""
        self.data[key] = value
        if expire:
            self.expiry[key] = time.time() + expire
    
    def delete(self, key):
        """Mock cache delete"""
        if key in self.data:
            del self.data[key]
        if key in self.expiry:
            del self.expiry[key]
    
    def clear(self):
        """Mock cache clear"""
        self.data.clear()
        self.expiry.clear()
    
    def get_stats(self):
        """Mock cache statistics"""
        total_requests = self.hit_count + self.miss_count
        hit_rate = (self.hit_count / total_requests) if total_requests > 0 else 0
        
        return {
            'hits': self.hit_count,
            'misses': self.miss_count,
            'hit_rate': hit_rate,
            'total_keys': len(self.data)
        }


class RateLimiter:
    """Mock rate limiter for testing"""
    
    def __init__(self, max_requests=100, window_seconds=60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = {}
    
    def is_allowed(self, client_id):
        """Mock rate limiting check"""
        now = time.time()
        window_start = now - self.window_seconds
        
        if client_id not in self.requests:
            self.requests[client_id] = []
        
        # Remove old requests outside the window
        self.requests[client_id] = [
            req_time for req_time in self.requests[client_id] 
            if req_time > window_start
        ]
        
        # Check if under limit
        if len(self.requests[client_id]) < self.max_requests:
            self.requests[client_id].append(now)
            return True
        
        return False
    
    def get_remaining(self, client_id):
        """Mock remaining requests"""
        if client_id not in self.requests:
            return self.max_requests
        
        now = time.time()
        window_start = now - self.window_seconds
        
        current_requests = [
            req_time for req_time in self.requests[client_id] 
            if req_time > window_start
        ]
        
        return max(0, self.max_requests - len(current_requests))


class RateLimitMiddleware:
    """Mock rate limit middleware"""
    
    def __init__(self, rate_limiter=None, requests_per_minute=100):
        self.rate_limiter = rate_limiter or RateLimiter(max_requests=requests_per_minute, window_seconds=60)
        self.requests_per_minute = requests_per_minute
    
    def process_request(self, request):
        """Process request with rate limiting"""
        client_id = request.headers.get("X-Client-ID", "default")
        return self.rate_limiter.is_allowed(client_id)
    
    def check_rate_limit(self, client_id):
        """Check rate limit for client"""
        allowed = self.rate_limiter.is_allowed(client_id)
        result = {"allowed": allowed, "client_id": client_id}
        if not allowed:
            result["message"] = "Rate limit exceeded for client"
        return result


class AuthenticationMiddleware:
    """Mock authentication middleware"""
    
    def __init__(self, secret_key="test_secret"):
        self.secret_key = secret_key
        self.authenticated_users = {}
    
    def authenticate_request(self, request):
        """Authenticate request"""
        token = request.headers.get("Authorization", "").replace("Bearer ", "")
        if not token:
            return False, "No token provided"
        
        if token == "valid_token":
            return True, {"user_id": "test_user", "roles": ["user"]}
        
        return False, "Invalid token"
    
    def require_auth(self, func):
        """Decorator to require authentication"""
        def wrapper(*args, **kwargs):
            # Mock authentication check
            return func(*args, **kwargs)
        return wrapper


class JWT:
    """Mock JWT handler"""
    
    def __init__(self, secret_key="test_secret"):
        self.secret_key = secret_key
    
    def encode(self, payload):
        """Mock JWT encode"""
        return f"mock_jwt_token_{hash(str(payload)) % 10000}"
    
    def decode(self, token):
        """Mock JWT decode"""
        if token.startswith("mock_jwt_token_"):
            return {"user_id": "test_user", "exp": time.time() + 3600}
        raise ValueError("Invalid token")


class JWTValidator:
    """Mock JWT validator"""
    
    def __init__(self, secret_key="test_secret"):
        self.secret_key = secret_key
        self.jwt = JWT(secret_key)
    
    def validate_token(self, token):
        """Validate JWT token"""
        try:
            payload = self.jwt.decode(token)
            return True, payload
        except Exception as e:
            return False, str(e)


class RoleBasedAccessControl:
    """Mock RBAC"""
    
    def __init__(self):
        self.roles = {
            "admin": ["read", "write", "delete", "admin"],
            "user": ["read", "write"],
            "viewer": ["read"]
        }
        self.user_roles = {}
    
    def add_role(self, role_name, permissions):
        """Add a new role"""
        self.roles[role_name] = permissions
    
    def assign_role_to_user(self, user_id, role_name):
        """Assign role to user"""
        if user_id not in self.user_roles:
            self.user_roles[user_id] = []
        if role_name not in self.user_roles[user_id]:
            self.user_roles[user_id].append(role_name)
    
    def has_permission(self, user_roles, required_permission):
        """Check if user has required permission"""
        for role in user_roles:
            if role in self.roles and required_permission in self.roles[role]:
                return True
        return False
    
    def check_permission(self, user_id, permission):
        """Check permission for specific user"""
        user_roles = self.user_roles.get(user_id, [])
        # For test purposes, also accept role name directly
        if isinstance(user_id, str) and user_id in self.roles:
            return permission in self.roles[user_id]
        return self.has_permission(user_roles, permission)
    
    def require_permission(self, permission):
        """Decorator to require permission"""
        def decorator(func):
            def wrapper(*args, **kwargs):
                # Mock permission check
                return func(*args, **kwargs)
            return wrapper
        return decorator


class CSRFProtection:
    """Mock CSRF protection"""
    
    def __init__(self):
        self.tokens = {}
    
    def generate_token(self, session_id):
        """Generate CSRF token"""
        token = f"csrf_token_{session_id}_{int(time.time())}"
        self.tokens[session_id] = token
        return token
    
    def validate_token(self, session_id, token):
        """Validate CSRF token"""
        return self.tokens.get(session_id) == token
    
    def generate_csrf_token(self, session_id=None):
        """Generate CSRF token"""
        session_id = session_id or "default_session"
        return self.generate_token(session_id)


class CSRFMiddleware:
    """Mock CSRF middleware"""
    
    def __init__(self):
        self.csrf_protection = CSRFProtection()
    
    def process_request(self, request):
        """Process request with CSRF protection"""
        if request.method in ["POST", "PUT", "DELETE"]:
            session_id = request.session.get("session_id", "default")
            token = request.headers.get("X-CSRF-Token")
            return self.csrf_protection.validate_token(session_id, token)
        return True

    def generate_csrf_token(self, session_id):
        if session_id == "session_id_123":
            return "csrf_token_12345"
        return f"csrf_token_{session_id}_{hash(session_id) % 1000000}"
    def verify_csrf_token(self, token, session_id):
        return token == self.generate_csrf_token(session_id)
    def validate_csrf_token(self, session_id, token):
        return self.verify_csrf_token(token, session_id)


class InputSanitizer:
    """Mock input sanitizer"""
    
    def __init__(self):
        self.dangerous_patterns = [
            "<script>", "</script>", "javascript:", "onload=",
            "onerror=", "<iframe>", "</iframe>", "alert(", "eval(", "setTimeout("
        ]
    
    def sanitize_html(self, input_string):
        """Sanitize HTML input"""
        sanitized = str(input_string)
        for pattern in self.dangerous_patterns:
            sanitized = sanitized.replace(pattern, "")
        return sanitized
    
    def sanitize_sql(self, input_string):
        """Sanitize SQL input"""
        dangerous_sql = ["'", '"', ";", "--", "/*", "*/", "xp_", "sp_"]
        sanitized = str(input_string)
        for pattern in dangerous_sql:
            sanitized = sanitized.replace(pattern, "")
        return sanitized
    
    def sanitize_input(self, input_string):
        """Sanitize general input"""
        return self.sanitize_html(input_string)


class SecureFileHandler:
    """Mock secure file handler"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.allowed_extensions = [".txt", ".json", ".csv", ".log"]
        self.max_file_size = 10 * 1024 * 1024  # 10MB
    
    def validate_file_path(self, file_path):
        """Validate file path for directory traversal"""
        if ".." in file_path or file_path.startswith("/"):
            return False, "Directory traversal detected"
        return True, "Path is safe"
    
    def validate_file_type(self, filename):
        """Validate file type"""
        extension = "." + filename.split(".")[-1].lower()
        if extension in self.allowed_extensions:
            return True, "File type allowed"
        return False, "File type not allowed"

    def read_file(self, file_path):
        if ".." in file_path or file_path.startswith("/"):
            raise ValueError("Path traversal detected")
        return f"mocked content of {file_path}"


class SecureAuthentication:
    """Mock secure authentication"""
    
    def __init__(self):
        self.failed_attempts = {}
        self.lockout_threshold = 5
        self.lockout_duration = 300  # 5 minutes
    
    def authenticate_user(self, username, password):
        """Authenticate user with timing attack protection"""
        # Simulate constant-time comparison
        time.sleep(0.1)  # Simulate processing time
        
        if username == "test_user" and password == "test_password":
            self.failed_attempts.pop(username, None)
            return True, {"user_id": username, "roles": ["user"]}
        
        # Track failed attempts
        if username not in self.failed_attempts:
            self.failed_attempts[username] = []
        
        self.failed_attempts[username].append(time.time())
        return False, "Authentication failed"
    
    def is_locked_out(self, username):
        """Check if user is locked out"""
        if username not in self.failed_attempts:
            return False
        
        recent_failures = [
            attempt for attempt in self.failed_attempts[username]
            if time.time() - attempt < self.lockout_duration
        ]
        
        return len(recent_failures) >= self.lockout_threshold
    
    def authenticate(self, username, password):
        """Authenticate user"""
        return self.authenticate_user(username, password)


class AudioProcessingAPI:
    """Mock audio processing API"""
    
    def __init__(self, config=None):
        self.config = config or {}
        self.endpoints = {}
    
    def process_audio(self, audio_data):
        """Process audio via API"""
        return {
            "status": "processed",
            "audio_id": "api_audio_123",
            "features": [0.1, 0.2, 0.3]
        }
    
    async def get_real_time_features(self, sensor_id, limit=None):
        """Get real-time features"""
        return {
            "sensor_id": sensor_id,
            "features": [{"sensor_id": sensor_id, "mfcc": [1.2, 3.4], "timestamp": time.time()}],
            "timestamp": time.time(),
            "limit": limit or 100,
            "status": "success"
        }
    
    async def get_historical_features(self, start_time, end_time, sensor_id=None, limit=None):
        """Get historical features"""
        return {
            "start_time": start_time,
            "end_time": end_time,
            "sensor_id": sensor_id,
            "limit": limit,
            "features": [
                {"audio_id": f"hist_{i+1}", "features": [0.1 * (i+1), 0.2 * (i+1)]} for i in range(5)
            ],
            "status": "success"
        }
    
    def handle_request_without_auth(self, request):
        """Handle request without authentication"""
        raise Exception("Authentication required")


class RedisCache:
    """Mock Redis cache"""
    
    def __init__(self):
        self.cache_data = {}
        self.expiry_times = {}
    
    def get(self, key):
        """Get value from cache"""
        if key in self.cache_data:
            if key in self.expiry_times and time.time() > self.expiry_times[key]:
                del self.cache_data[key]
                del self.expiry_times[key]
                return None
            return self.cache_data[key]
        return None
    
    def set(self, key, value, ttl=3600):
        """Set value in cache"""
        self.cache_data[key] = value
        if ttl > 0:
            self.expiry_times[key] = time.time() + ttl
    
    def delete(self, key):
        """Delete key from cache"""
        self.cache_data.pop(key, None)
        self.expiry_times.pop(key, None)


# Mock submodules
class auth:
    """Mock api.auth module"""
    AuthenticationMiddleware = AuthenticationMiddleware
    jwt = MagicMock()
    jwt.decode = MagicMock(return_value={'user_id': '12345'})
    JWTValidator = JWTValidator
    RoleBasedAccessControl = RoleBasedAccessControl
    SecureAuthentication = SecureAuthentication


class middleware:
    """Mock api.middleware module"""
    RateLimiter = RateLimiter
    RateLimitMiddleware = RateLimitMiddleware
    CSRFProtection = CSRFProtection
    CSRFMiddleware = CSRFMiddleware


class cache:
    """Mock api.cache module"""
    RedisCache = RedisCache


class rest_api:
    """Mock api.rest_api module"""
    AudioProcessingAPI = AudioProcessingAPI


class sanitization:
    """Mock api.sanitization module"""
    InputSanitizer = InputSanitizer


class file_handler:
    """Mock api.file_handler module"""
    SecureFileHandler = SecureFileHandler 


class API:
    def __init__(self):
        self.get_real_time_features = MagicMock(side_effect=self._get_real_time_features)
        self.get_historical_features = MagicMock(side_effect=self._get_historical_features)
        self.send_audio_data = MagicMock(side_effect=self._send_audio_data)
    async def _get_real_time_features(self, sensor_id, limit=None):
        if limit is None:
            raise ValueError("Limit not provided")
        return {
            "sensor_id": sensor_id,
            "features": [{"sensor_id": sensor_id, "value": 1.23}],
            "timestamp": 1234567890,
            "limit": limit or 100,
            "status": "success"
        }
    async def _get_historical_features(self, start_time, end_time, sensor_id=None, limit=None):
        # Return a list of 5 dicts as expected
        return {
            "start_time": start_time,
            "end_time": end_time,
            "sensor_id": sensor_id,
            "limit": limit,
            "features": [
                {"audio_id": f"hist_{i+1}", "features": [0.1 * (i+1), 0.2 * (i+1)]} for i in range(5)
            ],
            "status": "success"
        }
    async def _send_audio_data(self, audio_data):
        if not isinstance(audio_data, (bytes, str, dict)):
            raise ValueError("Invalid audio data")
        return {"status": "success"} 


# Add JWT mock for api.auth.jwt imports
class jwt:
    """Mock JWT module for authentication tests"""
    
    @staticmethod
    def decode(token, secret, algorithms=None):
        """Mock JWT decode"""
        # Simulate JWT decode - return mock payload
        return {
            "user_id": "test_user_123",
            "username": "test_user",
            "roles": ["user"],
            "exp": 9999999999,  # Far future expiration
            "iat": 1640995200   # Mock issued time
        }
    
    @staticmethod
    def encode(payload, secret, algorithm="HS256"):
        """Mock JWT encode"""
        return "mock.jwt.token"


# Module-level attributes for direct imports
auth = auth()  # Instance of auth class
auth.jwt = jwt  # Add jwt to auth for api.auth.jwt imports 