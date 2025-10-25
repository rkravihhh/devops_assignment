# Transaction Reconciliation API

A FastAPI-based microservice for B2B fintech card transaction reconciliation with Tier 1 issuers.

## Overview

This API handles transaction reconciliation for card transaction data processing, replacing part of the legacy monolith to improve PCI DSS compliance and system reliability.

## Features

- **Transaction Management**: Create, read, update, and delete card transactions
- **Issuer Management**: Manage Tier 1 card issuer configurations
- **Reconciliation Processing**: Automated transaction reconciliation with background processing
- **Security**: PCI DSS compliant with card number masking and secure data handling
- **Monitoring**: Health checks, metrics, and structured logging
- **Scalability**: Async/await support with database connection pooling

## Technology Stack

- **FastAPI**: Modern, fast web framework for building APIs
- **SQLAlchemy**: SQL toolkit and ORM with async support
- **PostgreSQL**: Primary database
- **Pydantic**: Data validation and serialization
- **Alembic**: Database migrations
- **Docker**: Containerization
- **AWS SDK**: Integration with AWS services (DynamoDB, S3, Secrets Manager)

## API Endpoints

### Health
- `GET /health` - Basic health check
- `GET /api/v1/health/detailed` - Detailed health check with database connectivity

### Transactions
- `POST /api/v1/transactions/` - Create transaction
- `GET /api/v1/transactions/{transaction_id}` - Get transaction
- `PUT /api/v1/transactions/{transaction_id}` - Update transaction
- `DELETE /api/v1/transactions/{transaction_id}` - Delete transaction
- `GET /api/v1/transactions/` - Search transactions with filters

### Issuers
- `POST /api/v1/issuers/` - Create issuer
- `GET /api/v1/issuers/{issuer_id}` - Get issuer
- `PUT /api/v1/issuers/{issuer_id}` - Update issuer
- `DELETE /api/v1/issuers/{issuer_id}` - Delete issuer
- `GET /api/v1/issuers/` - Search issuers with filters

### Reconciliations
- `POST /api/v1/reconciliations/` - Create reconciliation
- `GET /api/v1/reconciliations/{reconciliation_id}` - Get reconciliation
- `PUT /api/v1/reconciliations/{reconciliation_id}` - Update reconciliation
- `DELETE /api/v1/reconciliations/{reconciliation_id}` - Delete reconciliation
- `GET /api/v1/reconciliations/` - Search reconciliations with filters
- `GET /api/v1/reconciliations/stats/overview` - Get reconciliation statistics
- `POST /api/v1/reconciliations/{reconciliation_id}/process` - Trigger reconciliation processing

## Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 13+
- Redis (optional, for caching)

### Installation

1. Clone the repository
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

4. Set up the database:
   ```bash
   # Create database
   createdb txn_reconcile
   
   # Run migrations (when Alembic is configured)
   alembic upgrade head
   ```

5. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

### Docker

```bash
# Build the image
docker build -t txn-reconcile-api .

# Run the container
docker run -p 8000:8000 txn-reconcile-api
```

## Configuration

The application uses environment variables for configuration. See `env.example` for all available options.

### Key Configuration Options

- `DATABASE_URL`: PostgreSQL connection string
- `SECRET_KEY`: Secret key for JWT tokens
- `AWS_REGION`: AWS region for AWS services
- `REDIS_URL`: Redis connection string for caching
- `LOG_LEVEL`: Logging level (DEBUG, INFO, WARNING, ERROR)

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
isort .
```

### Type Checking

```bash
mypy .
```

## API Documentation

Once the application is running, you can access:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## Security Considerations

- Card numbers are automatically masked in responses
- Sensitive data is encrypted at rest
- API endpoints require proper authentication (to be implemented)
- CORS is configured for production environments
- Security headers are automatically added

## Monitoring

The application includes:

- Health check endpoints for load balancers
- Structured logging with request IDs
- Metrics collection (Prometheus compatible)
- Database connection monitoring

## Deployment

The application is designed to run in containerized environments with:

- Health checks for container orchestration
- Graceful shutdown handling
- Environment-based configuration
- Database connection pooling
- Background task processing

## License

This project is proprietary software for internal use only.
