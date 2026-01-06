# AWS deployment (ECR → ECS Fargate)

This is a practical runbook-style outline to deploy the Streamlit dashboard.

## 1) Build image locally
```bash
docker build -f docker/Dockerfile -t ibm-hr-analytics:latest .
```

## 2) Push to ECR
- Create an ECR repo: `ibm-hr-analytics`
- Authenticate and push:
```bash
aws ecr get-login-password --region <REGION> | docker login --username AWS --password-stdin <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com
docker tag ibm-hr-analytics:latest <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/ibm-hr-analytics:latest
docker push <ACCOUNT>.dkr.ecr.<REGION>.amazonaws.com/ibm-hr-analytics:latest
```

## 3) ECS Fargate service
- Task definition:
  - container port: `8501`
  - env vars: `PGHOST`, `PGPORT`, `PGDATABASE`, `PGUSER`, `PGPASSWORD`
- Recommended:
  - Put Postgres in RDS (or Aurora Postgres)
  - Run app in private subnets, ALB in public subnets

## 4) Observability
- CloudWatch logs from task
- ALB health check: `/` on port `8501`

## 5) Data loading
- One-time load: run `python -m hr_analytics.db ...` on a short-lived ECS task or CI job.
