#!/bin/bash
# Deploy platform: secrets sync → deriv-postgres → deriv-kafka → deriv-apps → deriv-ingress.
# Prerequisites: deploy/preflight/platform-preflight.sh, deploy/infrastructure/helm-eks-addons-deploy.sh
set -euo pipefail

HELM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
APP_SECRET="${APP_SECRET:-deriv-platform-app-secrets}"
PLATFORM_SECRET_ID="${PLATFORM_SECRET_ID:-deriv-ai-bot/dev/platform}"
AWS_REGION="${AWS_REGION:-us-west-1}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"
SKIP_PREFLIGHT="${SKIP_PREFLIGHT:-false}"
DEPLOY_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }
log_section() { echo ""; log "========== $* =========="; }

require_env() {
  [[ -n "${!1:-}" ]] || { log "ERROR: $1 is not set"; exit 1; }
}

warn_legacy_release() {
  if helm status deriv-platform -n "${HELM_NAMESPACE}" >/dev/null 2>&1; then
    log "WARNING: legacy release 'deriv-platform' exists — uninstall before split charts:"
    log "  helm uninstall deriv-platform -n ${HELM_NAMESPACE}"
  fi
  if kubectl get ingress deriv-apps -n "${HELM_NAMESPACE}" >/dev/null 2>&1 \
      && ! helm status deriv-ingress -n "${HELM_NAMESPACE}" >/dev/null 2>&1; then
    log "WARNING: Ingress 'deriv-apps' exists without deriv-ingress release — delete stale Ingress:"
    log "  kubectl delete ingress deriv-apps -n ${HELM_NAMESPACE}"
  fi
}

sync_platform_secrets() {
  log_section "Secrets Manager → Kubernetes"
  require_env PLATFORM_SECRET_ID
  local app_json
  app_json=$(aws secretsmanager get-secret-value \
    --region "${AWS_REGION}" \
    --secret-id "${PLATFORM_SECRET_ID}" \
    --query SecretString --output text)

  POSTGRES_PASSWORD=$(echo "${app_json}" | jq -r '.POSTGRES_PASSWORD // empty')
  AUTH_SECRET=$(echo "${app_json}" | jq -r '.AUTH_SECRET // empty')
  SAGEMAKER_EMBEDDING_ENDPOINT=$(echo "${app_json}" | jq -r '.SAGEMAKER_EMBEDDING_ENDPOINT // empty')
  S3_VECTORS_BUCKET_NAME=$(echo "${app_json}" | jq -r '.S3_VECTORS_BUCKET_NAME // empty')
  S3_VECTORS_INDEX_NAME=$(echo "${app_json}" | jq -r '.S3_VECTORS_INDEX_NAME // empty')
  BEDROCK_REGION=$(echo "${app_json}" | jq -r '.BEDROCK_REGION // empty')
  BEDROCK_DECISION_MODEL_ID=$(echo "${app_json}" | jq -r '.BEDROCK_DECISION_MODEL_ID // empty')

  for key in POSTGRES_PASSWORD AUTH_SECRET; do
    [[ -n "${!key}" ]] || { log "ERROR: missing ${key} in ${PLATFORM_SECRET_ID}"; exit 1; }
  done

  kubectl create secret generic "${APP_SECRET}" \
    --namespace "${HELM_NAMESPACE}" \
    --from-literal=POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    --from-literal=postgres-password="${POSTGRES_PASSWORD}" \
    --from-literal=AUTH_SECRET="${AUTH_SECRET}" \
    --from-literal=SAGEMAKER_EMBEDDING_ENDPOINT="${SAGEMAKER_EMBEDDING_ENDPOINT}" \
    --from-literal=S3_VECTORS_BUCKET_NAME="${S3_VECTORS_BUCKET_NAME}" \
    --from-literal=S3_VECTORS_INDEX_NAME="${S3_VECTORS_INDEX_NAME}" \
    --from-literal=BEDROCK_REGION="${BEDROCK_REGION:-${AWS_REGION}}" \
    --from-literal=BEDROCK_DECISION_MODEL_ID="${BEDROCK_DECISION_MODEL_ID}" \
    --dry-run=client -o yaml | kubectl apply -f -
  export POSTGRES_PASSWORD
}

main() {
  if [[ "${SKIP_PREFLIGHT}" != "true" ]]; then
    "${DEPLOY_ROOT}/preflight/platform-preflight.sh"
  fi
  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
  warn_legacy_release
  sync_platform_secrets

  export HELM_NAMESPACE APP_SECRET POSTGRES_PASSWORD
  "${DEPLOY_ROOT}/data/helm-postgres-deploy.sh"
  "${DEPLOY_ROOT}/data/helm-kafka-deploy.sh"
  "${DEPLOY_ROOT}/app/helm-apps-deploy.sh"
  "${DEPLOY_ROOT}/app/helm-ingress-deploy.sh"

  log_section "Platform deploy OK (deriv-postgres, deriv-kafka, deriv-apps, deriv-ingress)"
}

main "$@"
