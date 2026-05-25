#!/bin/bash
# Deploy deriv-postgres Helm chart (Bitnami PostgreSQL only).
set -euo pipefail

HELM_CHART="${HELM_CHART:-deploy/helm/deriv-postgres}"
HELM_RELEASE="${HELM_RELEASE:-deriv-postgres}"
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
  log_section "Helm deriv-postgres"
  require_env POSTGRES_PASSWORD
  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
  helm dependency update "${HELM_CHART}"
  deploy_helm_unlock

  HELM_PG_PASS_FILE=$(mktemp)
  chmod 600 "${HELM_PG_PASS_FILE}"
  printf '%s' "${POSTGRES_PASSWORD}" > "${HELM_PG_PASS_FILE}"

  helm upgrade --install "${HELM_RELEASE}" "${HELM_CHART}" \
    --namespace "${HELM_NAMESPACE}" \
    -f "${HELM_CHART}/values.yaml" \
    -f "${HELM_CHART}/values-dev.yaml" \
    --set "global.namespaceOverride=${HELM_NAMESPACE}" \
    --set "global.security.allowInsecureImages=true" \
    --set "namespace.name=${HELM_NAMESPACE}" \
    --set "postgresql.auth.existingSecret=${APP_SECRET}" \
    --set "postgresql.image.registry=docker.io" \
    --set "postgresql.image.repository=bitnamilegacy/postgresql" \
    --set "postgresql.image.tag=16.4.0-debian-12-r14" \
    --set-file "global.postgresql.auth.password=${HELM_PG_PASS_FILE}"
  rm -f "${HELM_PG_PASS_FILE}"

  local pod="${HELM_RELEASE}-postgresql-0"
  local img
  img=$(kubectl get pod "${pod}" -n "${HELM_NAMESPACE}" -o jsonpath='{.spec.containers[0].image}' 2>/dev/null || true)
  if [[ "${img}" == *"/bitnami/"* && "${img}" != *bitnamilegacy* ]]; then
    kubectl delete pod "${pod}" -n "${HELM_NAMESPACE}" --wait=false || true
  fi
  kubectl rollout restart "statefulset/${HELM_RELEASE}-postgresql" -n "${HELM_NAMESPACE}" 2>/dev/null || true
  kubectl rollout status "statefulset/${HELM_RELEASE}-postgresql" -n "${HELM_NAMESPACE}" --timeout=10m || true
  log "deriv-postgres deploy OK"
}

main "$@"
