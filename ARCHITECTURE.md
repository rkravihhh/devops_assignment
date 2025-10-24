## Assumptions
- EKS runs in 2 AZs, private pods, ALB for ingress, VPC endpoints for all sensitive services
- Dummy SSL ACM cert for HTTPS in dev/stg, valid ACM for prod
- KMS encryption is default everywhere

## Open Questions
- IAM role for VPC flow logs: is created manually for now.
- WAF not attached – future scope.

## Networking
- 2x public, 2x private subnets per AZ (see attached diagram)
- NAT & IGW used for private/public isolation

## Risks
- No WAF in MVP
- ACM certificate is self-signed for demo
