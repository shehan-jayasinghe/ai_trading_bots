#!/bin/bash
# Deploy deriv-ingress Helm chart (ALB Ingress → deriv-apps Services).
set -euo pipefail

HELM_CHART="${HELM_CHART:-deploy/helm/deriv-ingress}"
HELM_RELEASE="${HELM_RELEASE:-deriv-ingress}"
HELM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
AWS_REGION="${AWS_REGION:-us-west-1}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }
log_section() { echo ""; log "========== $* =========="; }

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
  if [[ "${INGRESS_ENABLED:-true}" == "false" ]]; then
    log "INGRESS_ENABLED=false — skip"
    exit 0
  fi

  log_section "Helm deriv-ingress"
  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
  deploy_helm_unlock

  local -a HELM_SET=()
  if [[ -n "${APP_ACM_CERTIFICATE_ARN:-}" && -n "${API_ACM_CERTIFICATE_ARN:-}" ]]; then
    HELM_SET=(
      --set-literal "ingress.certificateArns=${APP_ACM_CERTIFICATE_ARN},${API_ACM_CERTIFICATE_ARN}"
      --set "ingress.hosts.app=${APP_DOMAIN}"
      --set "ingress.hosts.api=${API_DOMAIN}"
    )
  fi

  local -a HELM_EXTRA=()
  [[ "${HELM_DEBUG:-false}" == "true" ]] && HELM_EXTRA+=(--debug)

  helm upgrade --install "${HELM_RELEASE}" "${HELM_CHART}" \
    --namespace "${HELM_NAMESPACE}" \
    -f "${HELM_CHART}/values.yaml" \
    -f "${HELM_CHART}/values-dev.yaml" \
    --set "namespace.name=${HELM_NAMESPACE}" \
    "${HELM_SET[@]}" \
    "${HELM_EXTRA[@]}"

  log_section "Wait for Ingress"
  local deadline=$((SECONDS + 600))
  while (( SECONDS < deadline )); do
    local addr
    addr=$(kubectl get ingress "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" \
      -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)
    [[ -n "${addr}" ]] && { log "Ingress: ${addr}"; break; }
    sleep 15
  done
  log "deriv-ingress deploy OK"
}

main "$@"
