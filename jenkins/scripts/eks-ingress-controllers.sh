#!/bin/bash
# Install AWS Load Balancer Controller + external-dns (idempotent). Called from helm-platform-deploy.sh.
set -euo pipefail

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

deploy_ingress_preflight() {
  log_section "Ingress controllers preflight"
  require_env VPC_ID
  require_env ALB_CONTROLLER_ROLE_ARN
  require_env EXTERNAL_DNS_ROLE_ARN
  require_env EXTERNAL_DNS_DOMAIN_FILTER
  require_env EXTERNAL_DNS_TXT_OWNER_ID
  log "  VPC_ID=${VPC_ID}"
  log "  ALB_CONTROLLER_ROLE_ARN=${ALB_CONTROLLER_ROLE_ARN}"
  log "  EXTERNAL_DNS_ROLE_ARN=${EXTERNAL_DNS_ROLE_ARN}"
}

deploy_helm_repos() {
  if ! helm repo list 2>/dev/null | grep -q '^eks[[:space:]]'; then
    helm repo add eks https://aws.github.io/eks-charts 2>/dev/null || true
  fi
  if ! helm repo list 2>/dev/null | grep -q '^external-dns[[:space:]]'; then
    helm repo add external-dns https://kubernetes-sigs.github.io/external-dns/ 2>/dev/null || true
  fi
  helm repo update eks external-dns 2>/dev/null || helm repo update
}

deploy_alb_controller() {
  log_section "AWS Load Balancer Controller"
  if kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller --no-headers 2>/dev/null \
      | grep -q Running; then
    log "  controller pods already present — running helm upgrade --install"
  fi

  helm upgrade --install aws-load-balancer-controller eks/aws-load-balancer-controller \
    --namespace kube-system \
    --set replicaCount=1 \
    --set clusterName="${EKS_CLUSTER_NAME}" \
    --set region="${AWS_REGION}" \
    --set vpcId="${VPC_ID}" \
    --set serviceAccount.create=true \
    --set serviceAccount.name=aws-load-balancer-controller \
    --set "serviceAccount.annotations.eks\.amazonaws\.com/role-arn=${ALB_CONTROLLER_ROLE_ARN}" \
    --wait \
    --timeout 10m

  # Helm may rotate webhook TLS (secret + caBundle) without restarting pods; reload certs before
  # any Service/Ingress admission (e.g. external-dns) hits the mutating webhook.
  log "  restarting ALB controller to sync webhook TLS with caBundle"
  kubectl rollout restart deployment/aws-load-balancer-controller -n kube-system
  kubectl rollout status deployment/aws-load-balancer-controller -n kube-system --timeout=5m

  local deadline=$((SECONDS + 120))
  while (( SECONDS < deadline )); do
    if kubectl get endpoints aws-load-balancer-webhook-service -n kube-system \
        -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null | grep -q .; then
      log "  ALB webhook endpoints ready"
      log "  ALB controller OK"
      return 0
    fi
    sleep 5
  done
  log "ERROR: aws-load-balancer-webhook-service has no endpoints after rollout"
  kubectl get endpoints aws-load-balancer-webhook-service -n kube-system || true
  kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller || true
  exit 1
}

deploy_external_dns() {
  log_section "external-dns"
  helm upgrade --install external-dns external-dns/external-dns \
    --namespace kube-system \
    --set provider.name=aws \
    --set policy=sync \
    --set "txtOwnerId=${EXTERNAL_DNS_TXT_OWNER_ID}" \
    --set "domainFilters[0]=${EXTERNAL_DNS_DOMAIN_FILTER}" \
    --set serviceAccount.create=true \
    --set serviceAccount.name=external-dns \
    --set "serviceAccount.annotations.eks\.amazonaws\.com/role-arn=${EXTERNAL_DNS_ROLE_ARN}" \
    --wait \
    --timeout 10m

  local deadline=$((SECONDS + 180))
  while (( SECONDS < deadline )); do
    if kubectl get pods -n kube-system -l app.kubernetes.io/name=external-dns --no-headers 2>/dev/null \
        | grep -q Running; then
      log "  external-dns OK"
      return 0
    fi
    sleep 10
  done
  log "ERROR: external-dns not Running within 3m"
  kubectl get pods -n kube-system -l app.kubernetes.io/name=external-dns || true
  exit 1
}

main() {
  deploy_ingress_preflight
  deploy_helm_repos
  deploy_alb_controller
  deploy_external_dns
}

main "$@"
