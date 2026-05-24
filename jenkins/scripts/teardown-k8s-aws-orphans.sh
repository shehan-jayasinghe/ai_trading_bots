#!/bin/bash
# Remove AWS resources created by EKS / AWS Load Balancer Controller that Terraform does not manage.
# Run before terraform destroy (or when recycling the dev environment).
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-west-1}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"
VPC_ID="${VPC_ID:-}"
HELM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
HELM_RELEASE="${HELM_RELEASE:-deriv-platform}"
WAIT_ALB_AFTER_HELM_SECS="${WAIT_ALB_AFTER_HELM_SECS:-120}"
WAIT_ENI_SECS="${WAIT_ENI_SECS:-600}"

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

cluster_exists() {
  aws eks describe-cluster --name "${EKS_CLUSTER_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1
}

teardown_helm_if_cluster_up() {
  log_section "Helm / Ingress teardown (if cluster reachable)"

  if ! command -v kubectl >/dev/null 2>&1 || ! command -v helm >/dev/null 2>&1; then
    log "kubectl or helm missing — skip Helm uninstall"
    return 0
  fi
  if ! cluster_exists; then
    log "EKS cluster ${EKS_CLUSTER_NAME} not found — skip Helm uninstall"
    return 0
  fi

  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"

  if helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" >/dev/null 2>&1; then
    log "helm uninstall ${HELM_RELEASE} -n ${HELM_NAMESPACE}"
    helm uninstall "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" --wait --timeout 10m || true
  fi

  for rel in aws-load-balancer-controller external-dns; do
    if helm status "${rel}" -n kube-system >/dev/null 2>&1; then
      log "helm uninstall ${rel} -n kube-system"
      helm uninstall "${rel}" -n kube-system --wait --timeout 10m || true
    fi
  done

  kubectl delete ingress "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" --ignore-not-found=true --wait=true 2>/dev/null || true

  if (( WAIT_ALB_AFTER_HELM_SECS > 0 )); then
    log "waiting ${WAIT_ALB_AFTER_HELM_SECS}s for controller to reconcile ALB deletion"
    sleep "${WAIT_ALB_AFTER_HELM_SECS}"
  fi
}

k8s_load_balancer_arns() {
  aws elbv2 describe-load-balancers --region "${AWS_REGION}" \
    --query "LoadBalancers[?VpcId=='${VPC_ID}' && contains(LoadBalancerName, 'k8s-')].LoadBalancerArn" \
    --output text 2>/dev/null || true
}

delete_k8s_load_balancers() {
  log_section "Delete k8s ELBv2 load balancers in VPC ${VPC_ID}"

  local arns
  arns=$(k8s_load_balancer_arns)
  if [[ -z "${arns}" || "${arns}" == "None" ]]; then
    log "  no k8s-* load balancers in VPC"
    return 0
  fi

  for arn in ${arns}; do
    log "  delete-load-balancer ${arn}"
    aws elbv2 delete-load-balancer --region "${AWS_REGION}" --load-balancer-arn "${arn}" || true
  done
}

delete_orphan_k8s_target_groups() {
  log_section "Delete orphaned k8s-* target groups in VPC ${VPC_ID}"

  local tg_arns
  tg_arns=$(aws elbv2 describe-target-groups --region "${AWS_REGION}" \
    --query "TargetGroups[?VpcId=='${VPC_ID}' && contains(TargetGroupName, 'k8s-')].TargetGroupArn" \
    --output text 2>/dev/null || true)

  if [[ -z "${tg_arns}" || "${tg_arns}" == "None" ]]; then
    log "  no k8s-* target groups in VPC"
    return 0
  fi

  for arn in ${tg_arns}; do
    log "  delete-target-group ${arn}"
    aws elbv2 delete-target-group --region "${AWS_REGION}" --target-group-arn "${arn}" 2>/dev/null || true
  done
}

wait_for_no_elb_enis_in_vpc() {
  log_section "Wait for ELB ENIs to leave VPC ${VPC_ID}"

  local deadline=$((SECONDS + WAIT_ENI_SECS))
  while (( SECONDS < deadline )); do
    local count
    count=$(aws ec2 describe-network-interfaces --region "${AWS_REGION}" \
      --filters "Name=vpc-id,Values=${VPC_ID}" \
      --query "length(NetworkInterfaces[?contains(Description, 'ELB ')])" \
      --output text 2>/dev/null || echo 0)
    if [[ "${count}" == "0" || "${count}" == "None" ]]; then
      log "  no ELB ENIs in VPC"
      return 0
    fi
    log "  ${count} ELB ENI(s) still present..."
    sleep 15
  done

  log "WARNING: ELB ENIs may still exist — check manually"
  aws ec2 describe-network-interfaces --region "${AWS_REGION}" \
    --filters "Name=vpc-id,Values=${VPC_ID}" \
    --query 'NetworkInterfaces[?contains(Description, `ELB `)].{Desc:Description,Subnet:SubnetId,Status:Status}' \
    --output table || true
  return 1
}

k8s_security_group_ids() {
  aws ec2 describe-security-groups --region "${AWS_REGION}" \
    --filters "Name=vpc-id,Values=${VPC_ID}" \
    --query "SecurityGroups[?GroupName!='default' && (contains(GroupName, 'k8s') || contains(Description, '[k8s]'))].GroupId" \
    --output text 2>/dev/null || true
}

revoke_all_security_group_rules() {
  local sg="$1"
  local perms egress

  perms=$(aws ec2 describe-security-groups --region "${AWS_REGION}" --group-ids "${sg}" \
    --query 'SecurityGroups[0].IpPermissions' --output json 2>/dev/null || echo '[]')
  if [[ "${perms}" != "[]" && -n "${perms}" ]]; then
    aws ec2 revoke-security-group-ingress --region "${AWS_REGION}" \
      --group-id "${sg}" --ip-permissions "${perms}" 2>/dev/null || true
  fi

  egress=$(aws ec2 describe-security-groups --region "${AWS_REGION}" --group-ids "${sg}" \
    --query 'SecurityGroups[0].IpPermissionsEgress' --output json 2>/dev/null || echo '[]')
  if [[ "${egress}" != "[]" && -n "${egress}" ]]; then
    aws ec2 revoke-security-group-egress --region "${AWS_REGION}" \
      --group-id "${sg}" --ip-permissions "${egress}" 2>/dev/null || true
  fi
}

delete_k8s_security_groups() {
  log_section "Delete k8s ALB controller security groups in VPC ${VPC_ID}"

  local sg_ids pass sg
  sg_ids=$(k8s_security_group_ids)
  if [[ -z "${sg_ids}" || "${sg_ids}" == "None" ]]; then
    log "  no k8s security groups in VPC"
    return 0
  fi

  for pass in 1 2 3; do
    for sg in ${sg_ids}; do
      revoke_all_security_group_rules "${sg}"
    done
  done

  for sg in ${sg_ids}; do
    if aws ec2 delete-security-group --region "${AWS_REGION}" --group-id "${sg}" 2>/dev/null; then
      log "  deleted ${sg}"
    else
      log "  could not delete ${sg} (may need another pass or manual delete)"
    fi
  done
}

release_unattached_eips() {
  log_section "Release unassociated Elastic IPs (safe mode)"

  local allocs
  allocs=$(aws ec2 describe-addresses --region "${AWS_REGION}" \
    --filters "Name=domain,Values=vpc" \
    --query 'Addresses[].AllocationId' \
    --output text 2>/dev/null || true)

  if [[ -z "${allocs}" || "${allocs}" == "None" ]]; then
    log "  no VPC Elastic IPs"
    return 0
  fi

  for alloc in ${allocs}; do
    local inst eni
    inst=$(aws ec2 describe-addresses --region "${AWS_REGION}" \
      --allocation-ids "${alloc}" \
      --query 'Addresses[0].InstanceId' --output text 2>/dev/null || true)
    eni=$(aws ec2 describe-addresses --region "${AWS_REGION}" \
      --allocation-ids "${alloc}" \
      --query 'Addresses[0].NetworkInterfaceId' --output text 2>/dev/null || true)

    if [[ -n "${inst}" && "${inst}" != "None" ]]; then
      log "  skip ${alloc} (instance ${inst})"
      continue
    fi
    if [[ -n "${eni}" && "${eni}" != "None" ]]; then
      log "  skip ${alloc} (ENI ${eni})"
      continue
    fi
    log "  release-address ${alloc}"
    aws ec2 release-address --region "${AWS_REGION}" --allocation-id "${alloc}" || true
  done
}

main() {
  log_section "Teardown K8s AWS orphans"
  require_env VPC_ID
  require_env EKS_CLUSTER_NAME
  log "  AWS_REGION=${AWS_REGION}"
  log "  EKS_CLUSTER_NAME=${EKS_CLUSTER_NAME}"
  log "  VPC_ID=${VPC_ID}"
  log "  HELM_RELEASE=${HELM_RELEASE} HELM_NAMESPACE=${HELM_NAMESPACE}"

  teardown_helm_if_cluster_up
  delete_k8s_load_balancers
  delete_orphan_k8s_target_groups
  wait_for_no_elb_enis_in_vpc || true
  delete_k8s_security_groups
  release_unattached_eips

  log_section "Done"
  log "Safe to run: cd infrastructure/terraform/environments/dev && terraform destroy"
}

main "$@"
