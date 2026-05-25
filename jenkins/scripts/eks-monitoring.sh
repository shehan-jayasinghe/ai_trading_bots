#!/bin/bash
# Install Grafana + Loki (S3 or filesystem) + Promtail for platform logs.
# Called from helm-platform-deploy.sh after deriv-platform is up.
set -euo pipefail

MONITORING_NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
PLATFORM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
OBSERVABILITY_DIR="${OBSERVABILITY_DIR:-deploy/helm/observability}"
LOKI_CHART_VERSION="${LOKI_CHART_VERSION:-6.30.1}"
PROMTAIL_CHART_VERSION="${PROMTAIL_CHART_VERSION:-6.17.0}"
GRAFANA_CHART_VERSION="${GRAFANA_CHART_VERSION:-9.2.10}"

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*"
}

log_section() {
  echo ""
  log "========== $* =========="
}

require_env() {
  local name="$1"
  if [[ -z "${!name:-}" ]]; then
    log "ERROR: ${name} is not set (Jenkins global env or jenkins/config/dev.env)"
    exit 1
  fi
}

monitoring_preflight() {
  if [[ "${MONITORING_ENABLED:-true}" == "false" ]]; then
    log "MONITORING_ENABLED=false — skip"
    exit 0
  fi
  require_env AWS_REGION
  require_env EKS_CLUSTER_NAME
}

deploy_helm_repos() {
  if ! helm repo list 2>/dev/null | grep -q '^grafana[[:space:]]'; then
    helm repo add grafana https://grafana.github.io/helm-charts 2>/dev/null || true
  fi
  helm repo update grafana 2>/dev/null || helm repo update
}

ensure_namespace() {
  kubectl create namespace "${MONITORING_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -
}

ensure_grafana_admin_secret() {
  if kubectl get secret grafana-admin -n "${MONITORING_NAMESPACE}" >/dev/null 2>&1; then
    log "  grafana-admin secret exists"
    return 0
  fi

  local password="${GRAFANA_ADMIN_PASSWORD:-}"
  if [[ -z "${password}" ]]; then
    password=$(openssl rand -base64 18 | tr -d '/+=' | head -c 20)
    log "  generated Grafana admin password (retrieve from secret grafana-admin)"
  fi

  kubectl create secret generic grafana-admin \
    --namespace "${MONITORING_NAMESPACE}" \
    --from-literal=admin-user=admin \
    --from-literal=admin-password="${password}" \
    --dry-run=client -o yaml | kubectl apply -f -
}

render_observability_values() {
  local src="$1"
  local dest="$2"
  if command -v envsubst >/dev/null 2>&1; then
    envsubst < "${src}" > "${dest}"
  else
    # macOS envsubst may be missing; use sed for required vars only
    sed \
      -e "s|\${LOKI_S3_BUCKET}|${LOKI_S3_BUCKET:-}|g" \
      -e "s|\${AWS_REGION}|${AWS_REGION}|g" \
      -e "s|\${LOKI_ROLE_ARN}|${LOKI_ROLE_ARN:-}|g" \
      -e "s|\${PLATFORM_NAMESPACE}|${PLATFORM_NAMESPACE}|g" \
      "${src}" > "${dest}"
  fi
}

deploy_loki() {
  log_section "Loki"
  local values_src values_rendered
  if [[ -n "${LOKI_S3_BUCKET:-}" && -n "${LOKI_ROLE_ARN:-}" ]]; then
    log "  storage: S3 bucket=${LOKI_S3_BUCKET}"
    values_src="${OBSERVABILITY_DIR}/loki-values-s3.yaml"
  else
    log "  storage: filesystem PVC (set LOKI_S3_BUCKET + LOKI_ROLE_ARN from terraform output for S3)"
    values_src="${OBSERVABILITY_DIR}/loki-values-filesystem.yaml"
  fi

  values_rendered=$(mktemp)
  if [[ "${values_src}" == *s3* ]]; then
    export LOKI_S3_BUCKET LOKI_ROLE_ARN AWS_REGION
    render_observability_values "${values_src}" "${values_rendered}"
  else
    cp "${values_src}" "${values_rendered}"
  fi

  helm upgrade --install loki grafana/loki \
    --namespace "${MONITORING_NAMESPACE}" \
    --version "${LOKI_CHART_VERSION}" \
    -f "${values_rendered}" \
    --wait \
    --timeout 15m

  rm -f "${values_rendered}"
  log "  Loki OK"
}

deploy_promtail() {
  log_section "Promtail"
  local values_rendered
  values_rendered=$(mktemp)
  export PLATFORM_NAMESPACE
  render_observability_values "${OBSERVABILITY_DIR}/promtail-values.yaml" "${values_rendered}"

  helm upgrade --install promtail grafana/promtail \
    --namespace "${MONITORING_NAMESPACE}" \
    --version "${PROMTAIL_CHART_VERSION}" \
    -f "${values_rendered}" \
    --wait \
    --timeout 10m

  rm -f "${values_rendered}"
  log "  Promtail OK"
}

deploy_grafana() {
  log_section "Grafana"
  helm upgrade --install grafana grafana/grafana \
    --namespace "${MONITORING_NAMESPACE}" \
    --version "${GRAFANA_CHART_VERSION}" \
    -f "${OBSERVABILITY_DIR}/grafana-values.yaml" \
    --wait \
    --timeout 10m

  log "  Grafana OK"
  log "  Access: kubectl port-forward -n ${MONITORING_NAMESPACE} svc/grafana 3000:80"
  log "  LogQL examples:"
  log "    {namespace=\"${PLATFORM_NAMESPACE}\", component=\"backend\"}"
  log "    {namespace=\"${PLATFORM_NAMESPACE}\", component=\"planner\"}"
  log "    {namespace=\"${PLATFORM_NAMESPACE}\", component=\"executor\"}"
}

main() {
  monitoring_preflight
  deploy_helm_repos
  ensure_namespace
  ensure_grafana_admin_secret
  deploy_loki
  deploy_promtail
  deploy_grafana
  log_section "Monitoring stack ready"
}

main "$@"
