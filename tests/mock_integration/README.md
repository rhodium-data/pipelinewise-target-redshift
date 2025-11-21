# Mock Integration Tests

This directory contains integration tests that run against PostgreSQL in Docker instead of AWS Redshift.

## Purpose

Mock integration tests provide a fast, local testing environment without requiring AWS credentials or infrastructure. They use PostgreSQL to simulate Redshift behavior and local files instead of S3.

## Structure

```
tests/mock_integration/
├── README.md                 # This file
├── __init__.py              # Python package marker
├── init-db.sql              # PostgreSQL initialization script
├── utils.py                 # Test utilities and configuration
├── test_target_redshift_mock.py  # Mock integration tests
├── data/                    # Directory for local file COPY operations (created by Docker)
└── resources/               # Test data files (optional, can reuse from ../integration/resources/)
```

## Running Tests

### Quick Start

```bash
# Run all mock integration tests (starts Docker automatically)
make test-mock-integration

# Or step by step:
make docker-up              # Start PostgreSQL container
pytest -vv tests/mock_integration  # Run tests
make docker-down            # Stop container
```

### Requirements

- Docker and Docker Compose installed
- Python 3.10+ with test dependencies (`pip install .[test]`)

## How It Works

1. **Docker Setup**: `docker-compose.yml` defines a PostgreSQL 14 Alpine container
2. **Database Initialization**: `init-db.sql` creates schemas and helper functions
3. **Local COPY Mode**: Tests use `use_local_copy=True` configuration
4. **File System**: CSV files are written to local temp directories instead of S3
5. **PostgreSQL COPY FROM STDIN**: Uses PostgreSQL's `COPY FROM STDIN` with `copy_expert()` to stream data from client instead of Redshift's S3 COPY. This avoids needing to mount volumes to share files between host and Docker container.

## Configuration

Mock tests use these environment variables (all optional with defaults):

```bash
MOCK_TARGET_HOST=localhost
MOCK_TARGET_PORT=5439
MOCK_TARGET_USER=test_user
MOCK_TARGET_PASSWORD=test_password
MOCK_TARGET_DBNAME=test_db
MOCK_TARGET_SCHEMA=test_target_schema
```

## Differences from Real Integration Tests

### Supported Features
- Basic data loading and transformations
- Table creation and schema management
- Primary key operations and updates
- Metadata columns
- Unicode characters
- Schema evolution

### Unsupported/Limited Features
- Redshift SUPER type (uses JSONB instead)
- S3 authentication and operations
- Redshift-specific performance features (DISTKEY, SORTKEY)
- Some Redshift-specific SQL syntax
- Compression algorithms (tests without compression)

## Adding New Tests

1. Create test methods in `test_target_redshift_mock.py`
2. Use `test_utils.get_mock_db_config()` for configuration
3. Use `test_utils.get_test_tap_lines()` to load test data
4. Tests automatically get a fresh database via `setup_method()`

Example:

```python
def test_my_feature(self):
    """Test description"""
    tap_lines = test_utils.get_test_tap_lines("my-test-data.json")
    target_redshift.persist_lines(self.config, tap_lines)

    # Verify results
    postgres = DbSync(self.config)
    result = postgres.query("SELECT * FROM my_schema.my_table")
    assert len(result) > 0
```

## Troubleshooting

### Container won't start
```bash
# Check Docker is running
docker ps

# Check logs
make docker-logs

# Clean up and retry
make clean-docker
make docker-up
```

### Connection refused
```bash
# Wait for PostgreSQL to be ready
sleep 10

# Check container health
docker-compose ps
```

### Tests fail with "psycopg2.OperationalError"
The `wait_for_postgres()` function in `utils.py` should handle this, but if it persists:
- Increase wait time in `setup_class()`
- Check PostgreSQL logs: `make docker-logs`
- Verify port 5439 is not in use: `lsof -i :5439`

## CI/CD Integration

These tests are ideal for CI/CD pipelines:

```yaml
# Example GitHub Actions
- name: Run mock integration tests
  run: |
    make install-dev
    make test-mock-integration
```

No AWS credentials or secrets required!
