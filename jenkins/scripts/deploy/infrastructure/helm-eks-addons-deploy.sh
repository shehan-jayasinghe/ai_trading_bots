#!/bin/bash
# Deploy eks-cluster-addons chart (ALB controller + external-dns).
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CHART_PATH="${CHART_PATH:-deploy/helm/eks-cluster-addons}"
RELEASE="${ADDONS_RELEASE:-eks-cluster-addons}"
NAMESPACE="${ADDONS_NAMESPACE:-kube-system}"

AWS_REGION="${AWS_REGION:-us-west-1}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }
log_section() { echo ""; log "========== $* =========="; }

require_env() {
  [[ -n "${!1:-}" ]] || { log "ERROR: $1 is not set"; exit 1; }
}

main() {
  log_section "Helm eks-cluster-addons"
  require_env VPC_ID
  require_env ALB_CONTROLLER_ROLE_ARN
  require_env EXTERNAL_DNS_ROLE_ARN
  require_env EXTERNAL_DNS_DOMAIN_FILTER
  require_env EXTERNAL_DNS_TXT_OWNER_ID
  require_env EKS_CLUSTER_NAME

  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"

  helm dependency update "${CHART_PATH}"

  helm upgrade --install "${RELEASE}" "${CHART_PATH}" \
    --namespace "${NAMESPACE}" \
    --create-namespace \
    -f "${CHART_PATH}/values.yaml" \
    -f "${CHART_PATH}/values-dev.yaml" \
    --set "aws-load-balancer-controller.clusterName=${EKS_CLUSTER_NAME}" \
    --set "aws-load-balancer-controller.region=${AWS_REGION}" \
    --set "aws-load-balancer-controller.vpcId=${VPC_ID}" \
    --set "aws-load-balancer-controller.serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn=${ALB_CONTROLLER_ROLE_ARN}" \
    --set "external-dns.txtOwnerId=${EXTERNAL_DNS_TXT_OWNER_ID}" \
    --set "external-dns.domainFilters[0]=${EXTERNAL_DNS_DOMAIN_FILTER}" \
    --set "external-dns.serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn=${EXTERNAL_DNS_ROLE_ARN}" \
    --wait \
    --timeout 10m

  "${SCRIPT_DIR}/alb-controller-post-install.sh"

  local deadline=$((SECONDS + 180))
  while (( SECONDS < deadline )); do
    if kubectl get pods -n kube-system -l app.kubernetes.io/name=external-dns --no-headers 2>/dev/null \
        | grep -q Running; then
      log "external-dns OK"
      log_section "eks-cluster-addons ready"
      return 0
    fi
    sleep 10
  done
  log "ERROR: external-dns not Running"
  exit 1
}

main "$@"
