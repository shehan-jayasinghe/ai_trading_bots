# Secrets, Encryption, Decryption

## Purpose
Protect Deriv tokens, API keys, model credentials, DB credentials.

## Storage
- AWS Secrets Manager (preferred)
- SSM Parameter Store for non-sensitive config

## Encryption
- At rest: AWS-managed KMS keys (or customer-managed CMK)
- In transit: HTTPS/TLS everywhere

## Access Pattern
- Runtime role (Lambda/ECS task role) reads required secrets
- No hardcoded secrets in code or .env committed to git

## Rotation
- Rotate broker/API keys on schedule
- Support zero-downtime secret refresh in app startup/reload

## Audit
- Log secret access events via CloudTrail
- Alert on unusual secret-read patterns
