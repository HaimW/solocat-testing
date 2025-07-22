"""
Mock database module for testing
"""
from unittest.mock import Mock
import time
import uuid


class AudioData:
    """Mock AudioData model for testing"""
    
    def __init__(self, audio_id=None, timestamp=None, sensor_id=None, 
                 sample_rate=44100, channels=1, duration_ms=5000):
        self.id = audio_id or str(uuid.uuid4())
        self.timestamp = timestamp or time.time()
        self.sensor_id = sensor_id or "sensor_001"
        self.sample_rate = sample_rate
        self.channels = channels
        self.duration_ms = duration_ms
        self.metadata = {}
    
    def to_dict(self):
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'sensor_id': self.sensor_id,
            'sample_rate': self.sample_rate,
            'channels': self.channels,
            'duration_ms': self.duration_ms,
            'metadata': self.metadata
        }


class FeatureData:
    """Mock FeatureData model for testing"""
    
    def __init__(self, feature_id=None, audio_id=None, features=None, 
                 algorithm_version="A.1.0", confidence_score=0.85):
        self.id = feature_id or str(uuid.uuid4())
        self.audio_id = audio_id or str(uuid.uuid4())
        self.features = features or [0.1, 0.2, 0.3, 0.4, 0.5]
        self.algorithm_version = algorithm_version
        self.confidence_score = confidence_score
        self.timestamp = time.time()
    
    def to_dict(self):
        return {
            'id': self.id,
            'audio_id': self.audio_id,
            'features': self.features,
            'algorithm_version': self.algorithm_version,
            'confidence_score': self.confidence_score,
            'timestamp': self.timestamp
        }


class DatabaseConnection:
    """Mock database connection for testing"""
    
    def __init__(self, connection_string=None):
        self.connection_string = connection_string or "postgresql://localhost"
        self.is_connected = False
        self.tables = {
            'audio_data': {},
            'feature_data': {},
            'processed_data': {}
        }
    
    def connect(self):
        """Mock database connection"""
        self.is_connected = True
        return True
    
    def disconnect(self):
        """Mock database disconnection"""
        self.is_connected = False
    
    def insert(self, table, data):
        """Mock data insertion"""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")
        
        if table not in self.tables:
            self.tables[table] = {}
        
        record_id = data.get('id') or str(uuid.uuid4())
        data['id'] = record_id
        data['created_at'] = time.time()
        
        self.tables[table][record_id] = data
        return record_id
    
    def select(self, table, filters=None):
        """Mock data selection"""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")
        
        if table not in self.tables:
            return []
        
        records = list(self.tables[table].values())
        
        if filters:
            filtered_records = []
            for record in records:
                match = True
                for key, value in filters.items():
                    if record.get(key) != value:
                        match = False
                        break
                if match:
                    filtered_records.append(record)
            return filtered_records
        
        return records
    
    def update(self, table, record_id, data):
        """Mock data update"""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")
        
        if table in self.tables and record_id in self.tables[table]:
            self.tables[table][record_id].update(data)
            self.tables[table][record_id]['updated_at'] = time.time()
            return True
        return False
    
    def delete(self, table, record_id):
        """Mock data deletion"""
        if not self.is_connected:
            raise ConnectionError("Not connected to database")
        
        if table in self.tables and record_id in self.tables[table]:
            del self.tables[table][record_id]
            return True
        return False


class DataWriter:
    """Mock data writer for testing"""
    
    def __init__(self, db_connection):
        self.db_connection = db_connection
        self.write_count = 0
    
    def write_audio_data(self, audio_data):
        """Mock audio data writing"""
        record_id = self.db_connection.insert('audio_data', audio_data)
        self.write_count += 1
        return record_id
    
    def write_feature_data(self, feature_data):
        """Mock feature data writing"""
        record_id = self.db_connection.insert('feature_data', feature_data)
        self.write_count += 1
        return record_id
    
    def batch_write(self, table, data_list):
        """Mock batch writing"""
        record_ids = []
        for data in data_list:
            record_id = self.db_connection.insert(table, data)
            record_ids.append(record_id)
        
        self.write_count += len(data_list)
        return record_ids


# Mock models module
models = Mock()
models.AudioData = AudioData
models.FeatureData = FeatureData
models.DatabaseConnection = DatabaseConnection
models.DataWriter = DataWriter 