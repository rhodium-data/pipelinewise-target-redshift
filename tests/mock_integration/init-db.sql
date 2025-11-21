-- Initialization script for mock Redshift (PostgreSQL) database
-- This sets up a PostgreSQL database to simulate Redshift behavior for testing

-- Create test schema
CREATE SCHEMA IF NOT EXISTS test_target_schema;

-- Grant permissions to test user
GRANT ALL PRIVILEGES ON SCHEMA test_target_schema TO test_user;
GRANT ALL PRIVILEGES ON DATABASE test_db TO test_user;

-- Set search path
ALTER USER test_user SET search_path TO test_target_schema, public;

-- Enable necessary extensions (if needed)
-- Note: PostgreSQL has most features built-in, unlike Redshift

-- Create a helper function to simulate Redshift's SUPER type behavior
-- In PostgreSQL, we'll use JSONB which is similar
CREATE OR REPLACE FUNCTION parse_json(text_value TEXT)
RETURNS JSONB AS $$
BEGIN
  RETURN text_value::JSONB;
EXCEPTION WHEN OTHERS THEN
  RETURN NULL;
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Make the function available to test_user
GRANT EXECUTE ON FUNCTION parse_json(TEXT) TO test_user;

-- Note: PostgreSQL uses JSONB instead of Redshift's SUPER type
-- The target will need to handle this mapping

COMMENT ON SCHEMA test_target_schema IS 'Mock Redshift schema for integration testing';
