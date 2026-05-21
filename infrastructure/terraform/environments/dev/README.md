# Jenkins infrastructure (dev)

**Terraform** = AWS infra (VPC, EC2, ALB, ACM, Route53)  
**Ansible** = Jenkins install on EC2 (`infrastructure/ansible/`)

## Layout

```text
infrastructure/
├── terraform/          # EC2 + ALB + DNS (minimal user_data bootstrap)
└── ansible/            # Jenkins install + logging
```

## Domain

| Item | Value |
|------|--------|
| Hosted zone | `testenvlab.shop` |
| Jenkins URL | `https://jenkins.testenvlab.shop` |

## Step 1 — Terraform (infra)

```bash
cd infrastructure/terraform/environments/dev
terraform init && terraform apply
```

If `jenkins_public_ip` is empty after apply, replace the instance (picks up `associate_public_ip_address`):

```bash
terraform apply -replace="module.jenkins_host.aws_instance.jenkins"
terraform output -raw jenkins_public_ip
```

## Step 2 — Install Ansible on your Mac (once)

```bash
brew install ansible
ansible --version
```

## Step 3 — Ansible (Jenkins install on EC2)

```bash
cd infrastructure/ansible
ansible-galaxy collection install -r requirements.yml

export JENKINS_SSH_KEY=~/.ssh/jenkins-key
export AWS_PROFILE=default

mkdir -p logs
ansible-playbook playbooks/jenkins-host.yml -vv \
  2>&1 | tee logs/run-$(date +%Y%m%d-%H%M%S).log
```

Full guide: `infrastructure/ansible/README.md`

## Step 4 — First login

1. Open **`https://jenkins.testenvlab.shop`** (after Ansible completes + ALB target healthy).
2. Unlock password:

   ```bash
   ssh -i ~/.ssh/jenkins-key ubuntu@<jenkins_public_ip>
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   ```

3. Setup wizard → **Git**, **Pipeline** (add Docker/build plugins later when needed).
4. Multibranch job → `deriv_ai_bot` → root `Jenkinsfile`.

## EC2 bootstrap (Terraform user_data)

Only installs Python for Ansible — **does not install Jenkins**.

Logs: `/var/log/bootstrap-minimal.log` on the instance.

## Security

- Jenkins **8080** — ALB only
- SSH (22) — open for EC2 Instance Connect
- Do not commit `.aws/credentials` or private keys

## Region

`us-west-1`
