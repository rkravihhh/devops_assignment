# Transaction Reconciliation API

A PCI DSS Level 1 compliant microservice for transaction reconciliation with blue-green deployment support.

## Quick Start

```bash
# Run locally with mock data
cd backend
python run_mock.py

# API available at http://localhost:8000
# Docs at http://localhost:8000/docs
```

## Deployment

- **Dev**: Automatic on push to `main`
- **Staging**: Automatic on push to `develop` 
- **Production**: Manual approval required

## Infrastructure

- **AWS EKS** with blue-green deployment
- **Application Load Balancer** with SSL termination
- **RDS PostgreSQL** with encryption
- **ECR** for container registry
- **Secrets Manager** for credentials

## Security

- PCI DSS Level 1 compliance
- HTTPS enforcement
- JWT authentication
- Rate limiting
- Audit logging

## API Endpoints

- `GET /health` - Health check
- `POST /api/v1/auth/login` - Authentication
- `GET /api/v1/transactions/` - List transactions
- `POST /api/v1/transactions/` - Create transaction
