"""
Mock API module for testing
"""
from unittest.mock import Mock
import json
import time


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


# Mock routes module
routes = Mock()
routes.AudioAPI = AudioAPI
routes.Cache = Cache
routes.RateLimiter = RateLimiter 