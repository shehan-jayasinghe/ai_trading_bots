#!/bin/bash
# Deploy deriv-apps Helm chart (backend, workers, frontend).
set -euo pipefail

HELM_LOG="${WORKSPACE:-/tmp}/helm-deploy.log"
HELM_CHART="${HELM_CHART:-deploy/helm/deriv-apps}"
HELM_RELEASE="${HELM_RELEASE:-deriv-apps}"
HELM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
APP_SECRET="${APP_SECRET:-deriv-platform-app-secrets}"
AWS_REGION="${AWS_REGION:-us-west-1}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }
log_section() { echo ""; log "========== $* =========="; }

require_env() {
  [[ -n "${!1:-}" ]] || { log "ERROR: $1 is not set"; exit 1; }
}

deploy_helm_unlock() {
  if ! helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" >/dev/null 2>&1; then
    return 0
  fi
  local status
  status=$(helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" -o json | jq -r '.info.status // "unknown"')
  [[ "${status}" != pending-* ]] && return 0
  log "Clearing pending release ${HELM_RELEASE} (status=${status})"
  local last_deployed
  last_deployed=$(helm history "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" -o json \
    | jq -r '[.[] | select(.status == "deployed") | .revision] | last // empty')
  [[ -n "${last_deployed}" ]] && helm rollback "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" "${last_deployed}" --wait --timeout 5m || true
}

main() {
  log_section "Helm deriv-apps"
  require_env IMAGE_TAG
  require_env ECR_REGISTRY
  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
  deploy_helm_unlock

  local -a HELM_SET_API=()
  if [[ -n "${API_DOMAIN:-}" ]]; then
    HELM_SET_API=(--set "frontend.env.NEXT_PUBLIC_BOT_BASE_URL=https://${API_DOMAIN}")
  fi

  local -a HELM_EXTRA=()
  [[ "${HELM_DEBUG:-false}" == "true" ]] && HELM_EXTRA+=(--debug)

  set -o pipefail
  helm upgrade --install "${HELM_RELEASE}" "${HELM_CHART}" \
    --namespace "${HELM_NAMESPACE}" \
    -f "${HELM_CHART}/values.yaml" \
    -f "${HELM_CHART}/values-dev.yaml" \
    --set "image.registry=${ECR_REGISTRY}" \
    --set "image.tag=${IMAGE_TAG}" \
    --set "namespace.name=${HELM_NAMESPACE}" \
    --set "secrets.existingSecret=${APP_SECRET}" \
    "${HELM_SET_API[@]}" \
    "${HELM_EXTRA[@]}" \
    2>&1 | tee -a "${HELM_LOG}"

  log_section "Wait for app pods"
  local deadline=$((SECONDS + 900))
  while (( SECONDS < deadline )); do
    local not_ready
    not_ready=$(kubectl get pods -n "${HELM_NAMESPACE}" \
      -l app.kubernetes.io/instance="${HELM_RELEASE}" \
      --field-selector=status.phase!=Running,status.phase!=Succeeded \
      --no-headers 2>/dev/null | wc -l | tr -d ' ')
    [[ "${not_ready}" -eq 0 ]] && break
    sleep 15
  done
  log "deriv-apps deploy OK"
}

main "$@"
