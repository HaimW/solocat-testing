"""
Mock system module for testing
"""
from unittest.mock import Mock
import subprocess
import os
import shlex
import time


class SystemOperations:
    """Mock system operations"""
    
    def __init__(self):
        self.command_log = []
        self.allowed_commands = [
            'ls', 'cat', 'echo', 'grep', 'head', 'tail',
            'ps', 'top', 'df', 'free', 'uptime'
        ]
        self.blocked_commands = [
            'rm', 'sudo', 'chmod', 'chown', 'mv', 'cp',
            'wget', 'curl', 'ssh', 'scp', 'dd'
        ]
    
    def execute_command(self, command, validate=True):
        """Execute system command with validation"""
        if validate and not self.validate_command(command):
            raise ValueError("Invalid characters in input")
        
        # Log the command
        self.command_log.append({
            "command": command,
            "timestamp": time.time(),
            "validated": validate
        })
        
        # Mock execution - don't actually run the command
        return {
            "returncode": 0,
            "stdout": f"Mock output for: {command}",
            "stderr": "",
            "command": command
        }
    
    def validate_command(self, command):
        """Validate command against security policies"""
        if not command or not command.strip():
            return False
        
        # Parse command to get the base command
        try:
            parts = shlex.split(command)
            base_command = parts[0] if parts else ""
        except ValueError:
            # Invalid shell syntax
            return False
        
        # Check for blocked commands
        for blocked in self.blocked_commands:
            if blocked in base_command.lower():
                return False
        
        # Check for command injection patterns
        injection_patterns = [
            ';', '&&', '||', '|', '`', '$(',
            '../', '/etc/', '/proc/', '/sys/'
        ]
        
        for pattern in injection_patterns:
            if pattern in command:
                return False
        
        return True
    
    def get_system_info(self):
        """Get system information"""
        return {
            "hostname": "mock-hostname",
            "platform": "Linux",
            "architecture": "x86_64",
            "cpu_count": 4,
            "memory_total": "8GB",
            "disk_usage": {
                "total": "100GB",
                "used": "50GB",
                "free": "50GB"
            }
        }
    
    def check_disk_space(self, path="/"):
        """Check disk space"""
        return {
            "path": path,
            "total": 100 * 1024 * 1024 * 1024,  # 100GB
            "used": 50 * 1024 * 1024 * 1024,   # 50GB
            "free": 50 * 1024 * 1024 * 1024,   # 50GB
            "percent_used": 50.0
        }
    
    def get_process_info(self, pid=None):
        """Get process information"""
        if pid:
            return {
                "pid": pid,
                "name": "mock_process",
                "status": "running",
                "cpu_percent": 5.0,
                "memory_percent": 10.0,
                "create_time": time.time() - 3600
            }
        else:
            return [
                {
                    "pid": 1234,
                    "name": "mock_process_1",
                    "status": "running",
                    "cpu_percent": 2.5,
                    "memory_percent": 5.0
                },
                {
                    "pid": 1235,
                    "name": "mock_process_2",
                    "status": "sleeping",
                    "cpu_percent": 0.1,
                    "memory_percent": 2.0
                }
            ]
    
    def restart_algorithm_pod(self, pod_name):
        """Restart algorithm pod"""
        result = self.execute_command(f"kubectl restart pod {pod_name}", validate=True)
        return {
            "pod_name": pod_name,
            "status": "restarted",
            "timestamp": time.time()
        }


# Mock operations module
class operations:
    """Mock system.operations module"""
    SystemOperations = SystemOperations 