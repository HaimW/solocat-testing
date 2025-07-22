"""
Mock kubernetes module for testing
"""
from unittest.mock import Mock, AsyncMock
import json


def load_incluster_config():
    """Mock kubernetes config loader"""
    return True


def load_kube_config():
    """Mock kubernetes config loader"""
    return True


class V1Pod:
    """Mock Kubernetes V1Pod"""
    def __init__(self, metadata=None, status=None, spec=None):
        self.metadata = metadata or Mock()
        self.status = status or Mock()
        self.spec = spec or Mock()
        
        # Set default values
        self.metadata.name = "test-pod"
        self.metadata.namespace = "default"
        self.status.phase = "Running"


class V1Service:
    """Mock Kubernetes V1Service"""
    def __init__(self, metadata=None, spec=None):
        self.metadata = metadata or Mock()
        self.spec = spec or Mock()
        
        self.metadata.name = "test-service"
        self.metadata.namespace = "default"


class V1Deployment:
    """Mock Kubernetes V1Deployment"""
    def __init__(self, metadata=None, spec=None, status=None):
        self.metadata = metadata or Mock()
        self.spec = spec or Mock()
        self.status = status or Mock()
        
        self.metadata.name = "test-deployment"
        self.spec.replicas = 3
        self.status.ready_replicas = 3


class AppsV1Api:
    """Mock Kubernetes Apps V1 API"""
    
    def __init__(self, api_client=None):
        self.api_client = api_client
    
    def list_namespaced_deployment(self, namespace="default", **kwargs):
        """Mock list deployments"""
        deployment = V1Deployment()
        return Mock(items=[deployment])
    
    def patch_namespaced_deployment_scale(self, name, namespace, body, **kwargs):
        """Mock scale deployment"""
        return Mock(spec=Mock(replicas=body.spec.replicas))
    
    def delete_namespaced_deployment(self, name, namespace, **kwargs):
        """Mock delete deployment"""
        return Mock(status="Success")


class CoreV1Api:
    """Mock Kubernetes Core V1 API"""
    
    def __init__(self, api_client=None):
        self.api_client = api_client
    
    def list_namespaced_pod(self, namespace="default", **kwargs):
        """Mock list pods"""
        pod = V1Pod()
        return Mock(items=[pod])
    
    def list_namespaced_service(self, namespace="default", **kwargs):
        """Mock list services"""
        service = V1Service()
        return Mock(items=[service])
    
    def delete_namespaced_pod(self, name, namespace, **kwargs):
        """Mock delete pod"""
        return Mock(status="Success")
    
    def read_namespaced_pod(self, name, namespace, **kwargs):
        """Mock read pod"""
        return V1Pod()


class ApiClient:
    """Mock Kubernetes API Client"""
    
    def __init__(self, configuration=None):
        self.configuration = configuration


class Configuration:
    """Mock Kubernetes Configuration"""
    
    def __init__(self):
        self.host = "https://localhost:6443"
        self.api_key = {}
        self.verify_ssl = False
    
    @classmethod
    def set_default(cls, configuration):
        """Mock set default configuration"""
        pass


# Mock client module
class client:
    """Mock kubernetes.client module"""
    AppsV1Api = AppsV1Api
    CoreV1Api = CoreV1Api
    ApiClient = ApiClient
    Configuration = Configuration
    V1Pod = V1Pod
    V1Service = V1Service
    V1Deployment = V1Deployment


# Mock config module
class config:
    """Mock kubernetes.config module"""
    
    @staticmethod
    def load_incluster_config():
        """Mock load in-cluster config"""
        return True
    
    @staticmethod
    def load_incluster_config():
        """Mock load in-cluster config"""
        pass
    
    @staticmethod
    def load_kube_config():
        """Mock load kube config"""
        pass


# Module level exports
AppsV1Api = AppsV1Api
CoreV1Api = CoreV1Api 