#!/bin/bash
# Deploy eks-monitoring chart (Loki + Promtail + Grafana).
# Grafana admin: AWS Secrets Manager → K8s secret grafana-admin.
set -euo pipefail

CHART_PATH="${CHART_PATH:-deploy/helm/eks-monitoring}"
RELEASE="${MONITORING_RELEASE:-eks-monitoring}"
NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
HELM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
GRAFANA_SECRET_ID="${GRAFANA_SECRET_ID:-deriv-ai-bot/dev/grafana}"
GRAFANA_DOMAIN="${GRAFANA_DOMAIN:-grafana.testenvlab.shop}"

AWS_REGION="${AWS_REGION:-us-west-1}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }
log_section() { echo ""; log "========== $* =========="; }

require_env() {
  [[ -n "${!1:-}" ]] || { log "ERROR: $1 is not set"; exit 1; }
}

sync_grafana_admin_secret() {
  log_section "Grafana Secrets Manager → Kubernetes"
  require_env GRAFANA_SECRET_ID
  local grafana_json
  grafana_json=$(aws secretsmanager get-secret-value \
    --region "${AWS_REGION}" \
    --secret-id "${GRAFANA_SECRET_ID}" \
    --query SecretString --output text)

  local admin_user admin_password
  admin_user=$(echo "${grafana_json}" | jq -r '.GRAFANA_ADMIN_USER // "admin"')
  admin_password=$(echo "${grafana_json}" | jq -r '.GRAFANA_ADMIN_PASSWORD // empty')

  [[ -n "${admin_password}" ]] || {
    log "ERROR: missing GRAFANA_ADMIN_PASSWORD in ${GRAFANA_SECRET_ID}"
    exit 1
  }

  kubectl create secret generic grafana-admin \
    --namespace "${NAMESPACE}" \
    --from-literal=admin-user="${admin_user}" \
    --from-literal=admin-password="${admin_password}" \
    --dry-run=client -o yaml | kubectl apply -f -
  log "Grafana login user: ${admin_user} (password in Secrets Manager / grafana-admin secret)"
}

main() {
  if [[ "${MONITORING_ENABLED:-true}" == "false" ]]; then
    log "MONITORING_ENABLED=false — skip"
    exit 0
  fi

  log_section "Helm eks-monitoring"
  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
  kubectl create namespace "${NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

  sync_grafana_admin_secret

  helm dependency update "${CHART_PATH}"

  local -a VALUE_FILES=(
    -f "${CHART_PATH}/values.yaml"
    -f "${CHART_PATH}/values-dev.yaml"
  )
  local -a SET_ARGS=(
    --set "platformNamespace=${HELM_NAMESPACE}"
  )

  if [[ -n "${LOKI_S3_BUCKET:-}" && -n "${LOKI_ROLE_ARN:-}" ]]; then
    log "Loki storage: S3 (${LOKI_S3_BUCKET})"
    VALUE_FILES+=(-f "${CHART_PATH}/values-dev-s3.yaml")
    SET_ARGS+=(
      --set "loki.loki.storage.bucketNames.chunks=${LOKI_S3_BUCKET}"
      --set "loki.loki.storage.bucketNames.ruler=${LOKI_S3_BUCKET}"
      --set "loki.loki.storage.bucketNames.admin=${LOKI_S3_BUCKET}"
      --set "loki.loki.storage.s3.region=${AWS_REGION}"
      --set "loki.serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn=${LOKI_ROLE_ARN}"
    )
  else
    log "Loki storage: filesystem PVC (set LOKI_S3_BUCKET + LOKI_ROLE_ARN for S3)"
  fi

  local grafana_ingress_values=""
  if [[ -n "${GRAFANA_ACM_CERTIFICATE_ARN:-}" ]]; then
    # Runtime TLS/host overrides via values file — never --set on dotted annotation keys
    # (Helm treats dots as nesting and breaks the Grafana ingress template).
    grafana_ingress_values=$(mktemp)
    cat > "${grafana_ingress_values}" <<EOF
grafana:
  grafana.ini:
    server:
      root_url: https://${GRAFANA_DOMAIN}/
      domain: ${GRAFANA_DOMAIN}
  ingress:
    enabled: true
    hosts:
      - ${GRAFANA_DOMAIN}
    annotations:
      alb.ingress.kubernetes.io/certificate-arn: ${GRAFANA_ACM_CERTIFICATE_ARN}
      external-dns.alpha.kubernetes.io/hostname: ${GRAFANA_DOMAIN}
EOF
    VALUE_FILES+=(-f "${grafana_ingress_values}")
    log "Grafana Ingress: https://${GRAFANA_DOMAIN}"
  else
    log "WARNING: GRAFANA_ACM_CERTIFICATE_ARN unset — Grafana ingress disabled (run terraform apply)"
    SET_ARGS+=(--set "grafana.ingress.enabled=false")
  fi

  helm upgrade --install "${RELEASE}" "${CHART_PATH}" \
    --namespace "${NAMESPACE}" \
    "${VALUE_FILES[@]}" \
    "${SET_ARGS[@]}" \
    --wait \
    --timeout 15m

  [[ -n "${grafana_ingress_values}" ]] && rm -f "${grafana_ingress_values}"

  if [[ -n "${GRAFANA_ACM_CERTIFICATE_ARN:-}" ]]; then
    log_section "Wait for Grafana Ingress"
    local deadline=$((SECONDS + 600))
    while (( SECONDS < deadline )); do
      local addr
      addr=$(kubectl get ingress grafana -n "${NAMESPACE}" \
        -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)
      [[ -n "${addr}" ]] && { log "Grafana ALB: ${addr}"; break; }
      sleep 15
    done
    log "Open: https://${GRAFANA_DOMAIN}"
  else
    log "Grafana (local): kubectl port-forward -n ${NAMESPACE} svc/grafana 3000:80"
  fi
  log "LogQL: {namespace=\"${HELM_NAMESPACE}\", component=\"backend\"}"
  log_section "eks-monitoring ready"
}

main "$@"
