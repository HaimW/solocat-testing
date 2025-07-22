-- Audio Processing System - Database Initialization
-- PostgreSQL setup for testing environment

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS audio_processing;
CREATE SCHEMA IF NOT EXISTS test_data;

-- Set search path
SET search_path TO audio_processing, public;

-- Audio data table
CREATE TABLE IF NOT EXISTS audio_data (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    sensor_id VARCHAR(50) NOT NULL,
    sample_rate INTEGER NOT NULL,
    channels INTEGER NOT NULL DEFAULT 1,
    duration_ms INTEGER NOT NULL,
    format VARCHAR(20) DEFAULT 'PCM',
    data_path TEXT,
    file_size BIGINT,
    checksum VARCHAR(64),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Feature data table (Algorithm A output)
CREATE TABLE IF NOT EXISTS features_type_a (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audio_id UUID REFERENCES audio_data(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    algorithm_version VARCHAR(20) DEFAULT 'A.1.0',
    processing_time_ms INTEGER,
    features JSONB NOT NULL,
    confidence_score FLOAT CHECK (confidence_score >= 0 AND confidence_score <= 1),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enhanced feature data table (Algorithm B output)
CREATE TABLE IF NOT EXISTS features_type_b (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    feature_a_id UUID REFERENCES features_type_a(id) ON DELETE CASCADE,
    audio_id UUID REFERENCES audio_data(id) ON DELETE CASCADE,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    algorithm_version VARCHAR(20) DEFAULT 'B.1.0',
    processing_time_ms INTEGER,
    enhanced_features JSONB NOT NULL,
    quality_score FLOAT CHECK (quality_score >= 0 AND quality_score <= 1),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Processing status table
CREATE TABLE IF NOT EXISTS processing_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    audio_id UUID REFERENCES audio_data(id) ON DELETE CASCADE,
    stage VARCHAR(20) NOT NULL CHECK (stage IN ('received', 'algorithm_a', 'algorithm_b', 'stored', 'failed')),
    status VARCHAR(20) NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- System metrics table
CREATE TABLE IF NOT EXISTS system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    component VARCHAR(50) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    metric_value FLOAT NOT NULL,
    unit VARCHAR(20),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Test data schema tables
SET search_path TO test_data, public;

-- Test runs table
CREATE TABLE IF NOT EXISTS test_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_suite VARCHAR(100) NOT NULL,
    test_name VARCHAR(200) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('passed', 'failed', 'skipped', 'error')),
    duration_ms INTEGER,
    error_message TEXT,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Performance benchmarks table
CREATE TABLE IF NOT EXISTS performance_benchmarks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    test_name VARCHAR(200) NOT NULL,
    metric_name VARCHAR(100) NOT NULL,
    value FLOAT NOT NULL,
    unit VARCHAR(20),
    threshold_min FLOAT,
    threshold_max FLOAT,
    passed BOOLEAN,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    metadata JSONB
);

-- Create indexes for better performance
SET search_path TO audio_processing, public;

-- Audio data indexes
CREATE INDEX IF NOT EXISTS idx_audio_data_timestamp ON audio_data(timestamp);
CREATE INDEX IF NOT EXISTS idx_audio_data_sensor_id ON audio_data(sensor_id);
CREATE INDEX IF NOT EXISTS idx_audio_data_created_at ON audio_data(created_at);

-- Features indexes
CREATE INDEX IF NOT EXISTS idx_features_a_audio_id ON features_type_a(audio_id);
CREATE INDEX IF NOT EXISTS idx_features_a_timestamp ON features_type_a(timestamp);
CREATE INDEX IF NOT EXISTS idx_features_b_audio_id ON features_type_b(audio_id);
CREATE INDEX IF NOT EXISTS idx_features_b_feature_a_id ON features_type_b(feature_a_id);
CREATE INDEX IF NOT EXISTS idx_features_b_timestamp ON features_type_b(timestamp);

-- Processing status indexes
CREATE INDEX IF NOT EXISTS idx_processing_status_audio_id ON processing_status(audio_id);
CREATE INDEX IF NOT EXISTS idx_processing_status_stage_status ON processing_status(stage, status);
CREATE INDEX IF NOT EXISTS idx_processing_status_created_at ON processing_status(created_at);

-- System metrics indexes
CREATE INDEX IF NOT EXISTS idx_system_metrics_timestamp ON system_metrics(timestamp);
CREATE INDEX IF NOT EXISTS idx_system_metrics_component ON system_metrics(component);
CREATE INDEX IF NOT EXISTS idx_system_metrics_metric_name ON system_metrics(metric_name);

-- Test data indexes
SET search_path TO test_data, public;

CREATE INDEX IF NOT EXISTS idx_test_runs_test_suite ON test_runs(test_suite);
CREATE INDEX IF NOT EXISTS idx_test_runs_timestamp ON test_runs(timestamp);
CREATE INDEX IF NOT EXISTS idx_performance_benchmarks_test_name ON performance_benchmarks(test_name);
CREATE INDEX IF NOT EXISTS idx_performance_benchmarks_timestamp ON performance_benchmarks(timestamp);

-- Create functions for updated_at triggers
SET search_path TO audio_processing, public;

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_audio_data_updated_at BEFORE UPDATE ON audio_data FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
CREATE TRIGGER update_processing_status_updated_at BEFORE UPDATE ON processing_status FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Create views for common queries
CREATE OR REPLACE VIEW audio_processing_summary AS
SELECT 
    ad.id,
    ad.timestamp,
    ad.sensor_id,
    ad.duration_ms,
    fa.algorithm_version as algo_a_version,
    fa.confidence_score,
    fb.algorithm_version as algo_b_version,
    fb.quality_score,
    ps.status as processing_status,
    ps.stage as processing_stage
FROM audio_data ad
LEFT JOIN features_type_a fa ON ad.id = fa.audio_id
LEFT JOIN features_type_b fb ON ad.id = fb.audio_id
LEFT JOIN processing_status ps ON ad.id = ps.audio_id
ORDER BY ad.timestamp DESC;

-- Sample test data (for testing purposes)
INSERT INTO audio_data (sensor_id, sample_rate, channels, duration_ms, format, metadata) VALUES
('sensor_001', 44100, 1, 5000, 'PCM', '{"location": "test_lab", "environment": "controlled"}'),
('sensor_002', 44100, 2, 3000, 'PCM', '{"location": "field_test", "environment": "noisy"}'),
('sensor_003', 48000, 1, 7000, 'PCM', '{"location": "test_lab", "environment": "controlled"}');

-- Grant permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA audio_processing TO testuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA audio_processing TO testuser;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA test_data TO testuser;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA test_data TO testuser;

-- Reset search path
SET search_path TO public; 