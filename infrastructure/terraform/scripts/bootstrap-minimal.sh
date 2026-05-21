#!/bin/bash
set -euxo pipefail

exec > >(tee /var/log/bootstrap-minimal.log) 2>&1

export DEBIAN_FRONTEND=noninteractive

apt-get update -y
apt-get install -y python3 python3-apt curl ca-certificates

echo "ready-for-ansible" > /var/log/bootstrap.done
echo "Run Ansible: infrastructure/ansible/playbooks/jenkins-host.yml"
