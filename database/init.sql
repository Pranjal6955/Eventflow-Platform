-- Database initialization script for Event Platform
-- This script creates the necessary tables for user analytics and chemical research

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- User Analytics Events table
CREATE TABLE IF NOT EXISTS user_analytics_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id VARCHAR(255) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    metadata JSONB,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Chemical Research Events table
CREATE TABLE IF NOT EXISTS chemical_research_events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    molecule_id VARCHAR(255) NOT NULL,
    researcher VARCHAR(255) NOT NULL,
    data JSONB NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    llm_properties JSONB, -- Extracted properties from LLM
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Event Processing Status table (for tracking processing state)
CREATE TABLE IF NOT EXISTS event_processing_status (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    event_id UUID NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending', -- pending, processing, completed, failed
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Indexes for better performance
CREATE INDEX IF NOT EXISTS idx_user_analytics_user_id ON user_analytics_events(user_id);
CREATE INDEX IF NOT EXISTS idx_user_analytics_event_type ON user_analytics_events(event_type);
CREATE INDEX IF NOT EXISTS idx_user_analytics_timestamp ON user_analytics_events(timestamp);

CREATE INDEX IF NOT EXISTS idx_chemical_research_molecule_id ON chemical_research_events(molecule_id);
CREATE INDEX IF NOT EXISTS idx_chemical_research_researcher ON chemical_research_events(researcher);
CREATE INDEX IF NOT EXISTS idx_chemical_research_timestamp ON chemical_research_events(timestamp);

CREATE INDEX IF NOT EXISTS idx_event_processing_status ON event_processing_status(status);
CREATE INDEX IF NOT EXISTS idx_event_processing_event_id ON event_processing_status(event_id);

-- Create triggers for updating timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_user_analytics_events_updated_at 
    BEFORE UPDATE ON user_analytics_events 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_chemical_research_events_updated_at 
    BEFORE UPDATE ON chemical_research_events 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_event_processing_status_updated_at 
    BEFORE UPDATE ON event_processing_status 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data for testing
INSERT INTO user_analytics_events (user_id, event_type, timestamp, metadata) VALUES
('test_user_1', 'page_view', '2024-01-01T10:00:00Z', '{"page": "/dashboard", "source": "web"}'),
('test_user_2', 'click', '2024-01-01T10:05:00Z', '{"button": "signup", "location": "header"}'),
('test_user_1', 'purchase', '2024-01-01T11:00:00Z', '{"amount": 99.99, "currency": "USD", "product": "premium_plan"}');

INSERT INTO chemical_research_events (molecule_id, researcher, data, timestamp) VALUES
('mol_h2o', 'Dr. Smith', '{"formula": "H2O", "weight": 18.015, "state": "liquid"}', '2024-01-01T09:00:00Z'),
('mol_nacl', 'Dr. Johnson', '{"formula": "NaCl", "weight": 58.44, "state": "solid"}', '2024-01-01T09:30:00Z'),
('mol_co2', 'Dr. Smith', '{"formula": "CO2", "weight": 44.01, "state": "gas"}', '2024-01-01T10:00:00Z');
