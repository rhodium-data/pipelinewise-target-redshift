"""
Utilities for mock integration tests using PostgreSQL in Docker.
This allows testing without requiring actual Redshift and S3 infrastructure.
"""
import os
import json


def get_mock_db_config():
    """
    Get configuration for mock PostgreSQL database.
    Uses Docker PostgreSQL instead of Redshift and local files instead of S3.
    """
    config = {}

    # PostgreSQL (mock Redshift) connection
    config['host'] = os.environ.get('MOCK_TARGET_HOST', 'localhost')
    config['port'] = os.environ.get('MOCK_TARGET_PORT', 5439)  # Use 5439 to match Redshift default
    config['user'] = os.environ.get('MOCK_TARGET_USER', 'test_user')
    config['password'] = os.environ.get('MOCK_TARGET_PASSWORD', 'test_password')
    config['dbname'] = os.environ.get('MOCK_TARGET_DBNAME', 'test_db')
    config['default_target_schema'] = os.environ.get('MOCK_TARGET_SCHEMA', 'test_target_schema')

    # Enable local copy mode (no S3)
    config['use_local_copy'] = True

    # These are not used in local mode but kept for compatibility
    config['disable_table_cache'] = None
    config['schema_mapping'] = None
    config['add_metadata_columns'] = None
    config['hard_delete'] = None
    config['flush_all_streams'] = None
    config['validate_records'] = None

    return config


def get_test_tap_lines(filename):
    """
    Load test tap lines from resource files.
    Reuses the same test data as regular integration tests.
    """
    lines = []
    # Try to load from integration test resources first
    integration_path = os.path.join(os.path.dirname(__file__), '..', 'integration', 'resources', filename)
    if os.path.exists(integration_path):
        with open(integration_path) as tap_stdout:
            for line in tap_stdout.readlines():
                lines.append(line)
    else:
        # Fallback to mock_integration resources
        mock_path = os.path.join(os.path.dirname(__file__), 'resources', filename)
        with open(mock_path) as tap_stdout:
            for line in tap_stdout.readlines():
                lines.append(line)

    return lines


def wait_for_postgres(config, max_retries=30, retry_delay=1):
    """
    Wait for PostgreSQL to be ready to accept connections.
    Useful for CI/CD environments where the database starts asynchronously.
    """
    import time
    import psycopg2

    retries = 0
    while retries < max_retries:
        try:
            conn = psycopg2.connect(
                host=config['host'],
                port=config['port'],
                dbname=config['dbname'],
                user=config['user'],
                password=config['password']
            )
            conn.close()
            print(f"PostgreSQL is ready after {retries} retries")
            return True
        except psycopg2.OperationalError as e:
            retries += 1
            if retries >= max_retries:
                print(f"Failed to connect to PostgreSQL after {max_retries} attempts: {e}")
                return False
            time.sleep(retry_delay)

    return False
