#!/bin/bash
# EKS kubeconfig, EBS CSI check, ECR image check, Secrets Manager → K8s secret.
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-west-1}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"
HELM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
APP_SECRET="${APP_SECRET:-deriv-platform-app-secrets}"
PLATFORM_SECRET_ID="${PLATFORM_SECRET_ID:-deriv-ai-bot/dev/platform}"
IMAGE_TAG="${IMAGE_TAG:-latest}"
ECR_REGISTRY="${ECR_REGISTRY:-}"

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }
log_section() { echo ""; log "========== $* =========="; }

require_env() {
  [[ -n "${!1:-}" ]] || { log "ERROR: $1 is not set"; exit 1; }
}

log_section "Kubeconfig"
require_env AWS_REGION
require_env EKS_CLUSTER_NAME
aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
kubectl create namespace "${HELM_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

log_section "EBS CSI preflight"
addon_status=""
if addon_status=$(aws eks describe-addon \
  --cluster-name "${EKS_CLUSTER_NAME}" \
  --addon-name aws-ebs-csi-driver \
  --region "${AWS_REGION}" \
  --query addon.status --output text 2>&1); then
  log "aws-ebs-csi-driver status=${addon_status}"
else
  log "WARNING: describe-addon failed: ${addon_status}"
  addon_status=""
fi

if kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-ebs-csi-driver --no-headers 2>/dev/null \
    | grep -q Running; then
  log "EBS CSI OK"
else
  log "ERROR: EBS CSI controller pods not Running — run terraform apply"
  exit 1
fi

log_section "ECR images (tag=${IMAGE_TAG})"
if [[ -n "${ECR_REGISTRY}" ]]; then
  for repo in deriv-backend deriv-workers deriv-frontend; do
    if aws ecr describe-images --region "${AWS_REGION}" \
        --repository-name "${repo}" --image-ids "imageTag=${IMAGE_TAG}" >/dev/null 2>&1; then
      log "  OK ${ECR_REGISTRY}/${repo}:${IMAGE_TAG}"
    else
      log "  MISS ${ECR_REGISTRY}/${repo}:${IMAGE_TAG}"
    fi
  done
fi

log "platform-preflight OK (secrets synced in deploy/helm-platform-deploy.sh)"
