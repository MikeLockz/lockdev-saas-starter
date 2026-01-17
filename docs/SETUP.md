# Cloud Setup Guide

## Infrastructure as Code
We use OpenTofu (Terraform fork) to manage AWS resources.

### Prerequisites
- Install OpenTofu: `brew install opentofu`
- AWS CLI configured with admin credentials.

### Provisioning
```bash
cd infra/aws
tofu init
tofu plan
tofu apply
```

## Deployment
We deploy the backend and worker to Aptible.

### Aptible Setup
1. Create an environment in Aptible.
2. Link your AWS account for log draining (see `docs/05 - Service Integrations/story-05-05-observability.md`).
3. Add the Aptible git remote:
```bash
git remote add aptible <your-aptible-git-url>
```
4. Push to deploy:
```bash
git push aptible main
```
