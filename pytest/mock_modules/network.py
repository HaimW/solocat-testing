"""
Mock network module for testing
"""
from unittest.mock import Mock, AsyncMock
import ssl
import time


class SecureHTTPClient:
    """Mock secure HTTP client"""
    
    def __init__(self, verify_ssl=True, timeout=30):
        self.verify_ssl = verify_ssl
        self.timeout = timeout
        self.session = Mock()
        self.certificates = {}
    
    def validate_certificate(self, hostname, certificate):
        """Mock certificate validation"""
        if not certificate:
            return False, "No certificate provided"
        
        # Mock validation logic
        if "invalid" in certificate:
            return False, "Certificate validation failed"
        
        return True, "Certificate valid"
    
    async def get(self, url, headers=None):
        """Mock HTTP GET request"""
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"status": "success", "data": {}}
        response.text = '{"status": "success", "data": {}}'
        response.headers = {"Content-Type": "application/json"}
        return response
    
    async def post(self, url, data=None, json=None, headers=None):
        """Mock HTTP POST request"""
        response = Mock()
        response.status_code = 201
        response.json.return_value = {"status": "created", "id": "12345"}
        response.text = '{"status": "created", "id": "12345"}'
        response.headers = {"Content-Type": "application/json"}
        return response
    
    def close(self):
        """Close client connection"""
        pass
    
    async def connect(self, hostname, port=443):
        """Connect to server"""
        self.certificates[hostname] = {
            "valid": True,
            "expiry": time.time() + 86400 * 365  # 1 year
        }
        return True


class NetworkSecurityFilter:
    """Mock network security filter"""
    
    def __init__(self):
        self.blocked_ips = set()
        self.allowed_ips = set()
        self.rate_limits = {}
        self.traffic_log = []
    
    def block_ip(self, ip_address, reason="security_violation"):
        """Block IP address"""
        self.blocked_ips.add(ip_address)
        self.log_traffic_event(ip_address, "blocked", reason)
    
    def allow_ip(self, ip_address):
        """Allow IP address"""
        if ip_address in self.blocked_ips:
            self.blocked_ips.remove(ip_address)
        self.allowed_ips.add(ip_address)
        self.log_traffic_event(ip_address, "allowed", "manually_allowed")
    
    def is_ip_blocked(self, ip_address):
        """Check if IP is blocked"""
        return ip_address in self.blocked_ips
    
    def is_ip_allowed(self, ip_address):
        """Check if IP address is allowed"""
        # Mock implementation - allow typical private network ranges
        allowed_patterns = ['192.168.', '10.0.', '172.16.', '127.0.']
        blocked_ips = ['10.0.0.1', '192.168.1.255']  # Specific blocked IPs
        
        if ip_address in blocked_ips:
            return False
        
        # Allow IPs that match allowed patterns
        for pattern in allowed_patterns:
            if ip_address.startswith(pattern):
                return True
        
        return False  # Block unknown IPs
    
    def check_rate_limit(self, ip_address, max_requests=100, window_seconds=60):
        """Check rate limiting"""
        current_time = time.time()
        
        if ip_address not in self.rate_limits:
            self.rate_limits[ip_address] = []
        
        # Clean old requests
        self.rate_limits[ip_address] = [
            req_time for req_time in self.rate_limits[ip_address]
            if current_time - req_time < window_seconds
        ]
        
        # Add current request
        self.rate_limits[ip_address].append(current_time)
        
        # Check limit
        if len(self.rate_limits[ip_address]) > max_requests:
            self.block_ip(ip_address, "rate_limit_exceeded")
            return False, "Rate limit exceeded"
        
        return True, "Within rate limit"
    
    def log_traffic_event(self, ip_address, action, reason):
        """Log traffic event"""
        event = {
            "timestamp": time.time(),
            "ip_address": ip_address,
            "action": action,
            "reason": reason
        }
        self.traffic_log.append(event)
    
    def get_traffic_stats(self, hours=24):
        """Get traffic statistics"""
        cutoff_time = time.time() - (hours * 3600)
        recent_events = [
            event for event in self.traffic_log
            if event["timestamp"] > cutoff_time
        ]
        
        return {
            "total_events": len(recent_events),
            "blocked_events": len([e for e in recent_events if e["action"] == "blocked"]),
            "allowed_events": len([e for e in recent_events if e["action"] == "allowed"]),
            "unique_ips": len(set(e["ip_address"] for e in recent_events))
        }
    
    def configure_allowed_networks(self, networks):
        """Configure allowed networks"""
        self.allowed_networks = networks
        return {"status": "configured", "networks": len(networks)}


class TLSManager:
    """Mock TLS/SSL manager"""
    
    def __init__(self):
        self.certificates = {}
        self.ssl_context = None
    
    def create_ssl_context(self, certfile=None, keyfile=None, cafile=None):
        """Create SSL context"""
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        self.ssl_context = context
        return context
    
    def validate_certificate_chain(self, certificate_chain):
        """Validate certificate chain"""
        if not certificate_chain:
            return False, "Empty certificate chain"
        
        # Mock validation
        for cert in certificate_chain:
            if "invalid" in cert:
                return False, f"Invalid certificate: {cert}"
        
        return True, "Certificate chain valid"
    
    def get_certificate_info(self, hostname, port=443):
        """Get certificate information"""
        return {
            "subject": {"commonName": hostname},
            "issuer": {"commonName": "Mock CA"},
            "notAfter": "Dec 31 23:59:59 2025 GMT",
            "notBefore": "Jan 1 00:00:00 2024 GMT",
            "serialNumber": "12345678",
            "version": 3
        }


# Mock submodules
class secure_client:
    """Mock network.secure_client module"""
    SecureHTTPClient = SecureHTTPClient


class security:
    """Mock network.security module"""
    NetworkSecurityFilter = NetworkSecurityFilter
    TLSManager = TLSManager 