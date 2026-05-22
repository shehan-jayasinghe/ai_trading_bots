# Ansible — Jenkins host (dev)

Installs **Jenkins on Ubuntu** (apt) on the EC2 instance created by Terraform.

**Terraform** = VPC, EC2, ALB, DNS  
**Ansible** = Java 21 + Jenkins only

---

## Quick start (after Terraform apply)

```bash
cd infrastructure/ansible
ansible-galaxy collection install -r requirements.yml

export JENKINS_SSH_KEY=~/.ssh/jenkins-key
export AWS_PROFILE=default

ansible jenkins -m ping -vv
ansible-playbook playbooks/jenkins-host.yml -vv \
  2>&1 | tee logs/run-$(date +%Y%m%d-%H%M%S).log
```

SSH user (`ubuntu`) and key path are set in `ansible.cfg` + `inventories/dev/group_vars/jenkins.yml`.

---

## 1 — Install Ansible on your Mac

```bash
brew install ansible
ansible --version
```

---

## 2 — Collections (once)

```bash
cd infrastructure/ansible
ansible-galaxy collection install -r requirements.yml
```

---

## 3 — Environment variables

| Variable | Purpose |
|----------|---------|
| `JENKINS_SSH_KEY` | Private key (default `~/.ssh/jenkins-key`) — must match `public_key` in Terraform |
| `AWS_PROFILE` | Same AWS account as Terraform (for EC2 inventory) |

```bash
export JENKINS_SSH_KEY=~/.ssh/jenkins-key
export AWS_PROFILE=default
```

---

## 4 — Run playbook (install Jenkins)

```bash
cd infrastructure/ansible
mkdir -p logs

ansible-playbook playbooks/jenkins-host.yml -vv \
  2>&1 | tee logs/run-$(date +%Y%m%d-%H%M%S).log
```

Wait until playbook finishes (including **Wait for Jenkins HTTP on port 8080**).

---

## 5 — Get Jenkins unlock password from EC2

Used on first login at **https://jenkins.testenvlab.shop** (one-time unlock code).

### Option A — SSH from Mac (recommended)

```bash
export JENKINS_SSH_KEY=~/.ssh/jenkins-key

ssh -i "$JENKINS_SSH_KEY" ubuntu@$(cd ../terraform/environments/dev && terraform output -raw jenkins_public_ip) \
  "sudo cat /var/lib/jenkins/secrets/initialAdminPassword"
```

Copy the single line printed (no spaces).

### Option B — SSH then run command

```bash
ssh -i "$JENKINS_SSH_KEY" ubuntu@50.18.77.183
sudo cat /var/lib/jenkins/secrets/initialAdminPassword
exit
```

Replace IP with `terraform output -raw jenkins_public_ip` if it changed.

### Option C — Ansible playbook (from Mac)

```bash
cd infrastructure/ansible
export JENKINS_SSH_KEY=~/.ssh/jenkins-key
export AWS_PROFILE=default

ansible-playbook playbooks/get-jenkins-password.yml
```

### Option D — Ansible ad-hoc

```bash
ansible jenkins -m shell -a "sudo cat /var/lib/jenkins/secrets/initialAdminPassword" -b
```

### Option E — AWS Console (no SSH key)

1. EC2 → Instances → `deriv-ai-bot-jenkins-dev`
2. **Connect** → **EC2 Instance Connect** → **Connect**
3. Run:

   ```bash
   sudo cat /var/lib/jenkins/secrets/initialAdminPassword
   ```

### If file is missing

Jenkins not installed yet — run the playbook first (section 4).

```bash
sudo systemctl status jenkins
```

---

## 6 — First login in browser

1. Open **https://jenkins.testenvlab.shop**
2. Paste **unlock password** (section 5)
3. **Install suggested plugins** or select **Git** + **Pipeline**
4. Create **admin user** (your username/password — not stored in Terraform/Ansible)

---

## 7 — Verify Jenkins is running

```bash
# From Mac
curl -sI "https://jenkins.testenvlab.shop/login" | head -1
# expect HTTP/2 200 or 403

# On EC2
ssh -i "$JENKINS_SSH_KEY" ubuntu@$(cd ../terraform/environments/dev && terraform output -raw jenkins_public_ip)
sudo systemctl status jenkins
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:8080/login
```

ALB target group must be **healthy** (port 8080). Check EC2 → Target groups → `deriv-jenkins-dev-tg`.

---

## Re-run playbook

```bash
export JENKINS_SSH_KEY=~/.ssh/jenkins-key
export AWS_PROFILE=default
ansible-playbook playbooks/jenkins-host.yml -vv
```

---

## Inventory

- Plugin: `inventories/dev/aws_ec2.yml`
- Region: `us-west-1`
- Tag: `Name=deriv-ai-bot-jenkins-dev`
- `ansible_host` = public IP from AWS (no manual IP in config)

---

## EKS platform (Postgres, Kafka, apps)

After Terraform EKS apply and ECR image push:

```bash
cp inventories/dev/group_vars/eks_secrets.yml.example inventories/dev/group_vars/eks_secrets.yml
# Edit secrets; set image_registry in group_vars/eks.yml

ansible-playbook playbooks/eks-platform.yml -vv
```

Full guide: `deploy/README.md`

## Config files

| File | Sets |
|------|------|
| `ansible.cfg` | `remote_user = ubuntu` |
| `group_vars/jenkins.yml` | `ansible_user`, SSH key path |
| `group_vars/eks.yml` | Helm release, ECR registry, cluster name |
| `group_vars/eks_secrets.yml` | Postgres password, AUTH_SECRET (gitignored) |
| `aws_ec2.yml` | EC2 lookup + `ansible_host: public_ip_address` |
