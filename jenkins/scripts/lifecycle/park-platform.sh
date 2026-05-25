#!/bin/bash
# Park dev platform: scale workloads and EKS nodes to 0, drop k8s ALB, optionally stop Jenkins EC2.
# Does NOT terraform destroy — wake with wake-platform.sh or deriv-deploy-platform.
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-west-1}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"
VPC_ID="${VPC_ID:-}"
HELM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
HELM_INGRESS_RELEASE="${HELM_INGRESS_RELEASE:-deriv-ingress}"
LEGACY_INGRESS_NAMES="${LEGACY_INGRESS_NAMES:-deriv-apps deriv-platform}"
MONITORING_NAMESPACE="${MONITORING_NAMESPACE:-monitoring}"
PARK_STOP_JENKINS="${PARK_STOP_JENKINS:-true}"
PARK_DELETE_ALB="${PARK_DELETE_ALB:-true}"
PARK_SCALE_NODES_ZERO="${PARK_SCALE_NODES_ZERO:-true}"
JENKINS_INSTANCE_NAME_TAG="${JENKINS_INSTANCE_NAME_TAG:-deriv-ai-bot-jenkins-dev}"
WAIT_ALB_SECS="${WAIT_ALB_SECS:-90}"

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
    log "ERROR: ${name} is not set (Jenkins global environment variable — see jenkins/global-env.example)"
    exit 1
  fi
}

cluster_exists() {
  aws eks describe-cluster --name "${EKS_CLUSTER_NAME}" --region "${AWS_REGION}" >/dev/null 2>&1
}

eks_nodegroup_name() {
  aws eks list-nodegroups --cluster-name "${EKS_CLUSTER_NAME}" --region "${AWS_REGION}" \
    --query 'nodegroups[0]' --output text 2>/dev/null || true
}

scale_namespace_workloads_to_zero() {
  local ns="$1"
  if ! kubectl get namespace "${ns}" >/dev/null 2>&1; then
    log "  namespace ${ns} not found — skip"
    return 0
  fi

  local deploys sts
  deploys=$(kubectl get deploy -n "${ns}" -o name 2>/dev/null || true)
  if [[ -n "${deploys}" ]]; then
    log "  scaling deployments in ${ns} to 0"
    kubectl scale ${deploys} -n "${ns}" --replicas=0 2>/dev/null || true
  fi

  sts=$(kubectl get sts -n "${ns}" -o name 2>/dev/null || true)
  if [[ -n "${sts}" ]]; then
    log "  scaling statefulsets in ${ns} to 0"
    kubectl scale ${sts} -n "${ns}" --replicas=0 2>/dev/null || true
  fi
}

park_kubernetes_workloads() {
  log_section "Scale Kubernetes workloads to 0"
  if ! cluster_exists; then
    log "EKS cluster not found — skip kubectl"
    return 0
  fi

  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"

  scale_namespace_workloads_to_zero "${HELM_NAMESPACE}"
  scale_namespace_workloads_to_zero "${MONITORING_NAMESPACE}"

  if [[ "${PARK_DELETE_ALB}" == "true" ]]; then
    for ing in "${HELM_INGRESS_RELEASE}" ${LEGACY_INGRESS_NAMES}; do
      log "  deleting Ingress ${ing} (drops platform ALB)"
      kubectl delete ingress "${ing}" -n "${HELM_NAMESPACE}" --ignore-not-found=true --wait=true 2>/dev/null || true
    done
    log "  deleting Ingress grafana in ${MONITORING_NAMESPACE} (drops Grafana ALB)"
    kubectl delete ingress grafana -n "${MONITORING_NAMESPACE}" --ignore-not-found=true --wait=true 2>/dev/null || true
    if (( WAIT_ALB_SECS > 0 )); then
      log "  waiting ${WAIT_ALB_SECS}s for ALB controller to reconcile"
      sleep "${WAIT_ALB_SECS}"
    fi
  fi
}

delete_k8s_albs_in_vpc() {
  [[ "${PARK_DELETE_ALB}" != "true" ]] && return 0
  [[ -z "${VPC_ID}" ]] && return 0

  log_section "Delete remaining k8s ALBs in VPC ${VPC_ID}"
  local arns
  arns=$(aws elbv2 describe-load-balancers --region "${AWS_REGION}" \
    --query "LoadBalancers[?VpcId=='${VPC_ID}' && contains(LoadBalancerName, 'k8s-')].LoadBalancerArn" \
    --output text 2>/dev/null || true)
  if [[ -z "${arns}" || "${arns}" == "None" ]]; then
    log "  no k8s ALBs in VPC"
    return 0
  fi
  for arn in ${arns}; do
    log "  delete-load-balancer ${arn}"
    aws elbv2 delete-load-balancer --region "${AWS_REGION}" --load-balancer-arn "${arn}" || true
  done
}

scale_eks_nodes_to_zero() {
  [[ "${PARK_SCALE_NODES_ZERO}" != "true" ]] && return 0

  log_section "Scale EKS node group to 0"
  local ng
  ng=$(eks_nodegroup_name)
  if [[ -z "${ng}" || "${ng}" == "None" ]]; then
    log "  no node group found — skip"
    return 0
  fi

  local max_size="${EKS_NODE_MAX_SIZE:-2}"
  log "  nodegroup=${ng} min=0 desired=0 max=${max_size}"
  aws eks update-nodegroup-config \
    --cluster-name "${EKS_CLUSTER_NAME}" \
    --nodegroup-name "${ng}" \
    --region "${AWS_REGION}" \
    --scaling-config "minSize=0,maxSize=${max_size},desiredSize=0"

  log "  node group scaling requested (EC2 worker billing stops when instances terminate)"
}

stop_jenkins_ec2() {
  [[ "${PARK_STOP_JENKINS}" != "true" ]] && return 0

  log_section "Stop Jenkins EC2 (optional)"
  local instance_id="${JENKINS_INSTANCE_ID:-}"
  if [[ -z "${instance_id}" ]]; then
    instance_id=$(aws ec2 describe-instances --region "${AWS_REGION}" \
      --filters "Name=tag:Name,Values=${JENKINS_INSTANCE_NAME_TAG}" \
                "Name=instance-state-name,Values=running,pending" \
      --query 'Reservations[0].Instances[0].InstanceId' --output text 2>/dev/null || true)
  fi
  if [[ -z "${instance_id}" || "${instance_id}" == "None" ]]; then
    log "  no running Jenkins instance (tag Name=${JENKINS_INSTANCE_NAME_TAG})"
    return 0
  fi
  log "  stopping instance ${instance_id}"
  aws ec2 stop-instances --region "${AWS_REGION}" --instance-ids "${instance_id}" || true
}

main() {
  log_section "Park platform (no terraform destroy)"
  require_env EKS_CLUSTER_NAME
  if [[ "${PARK_DELETE_ALB}" == "true" ]]; then
    require_env VPC_ID
  fi

  park_kubernetes_workloads
  delete_k8s_albs_in_vpc
  scale_eks_nodes_to_zero
  stop_jenkins_ec2

  log_section "Park complete"
  log "Still billed: EKS control plane (~\$0.10/hr), NAT gateway, Jenkins ALB (if Jenkins stack up), EBS PVCs"
  log "Wake: jenkins job deriv-wake-platform or jenkins/scripts/lifecycle/wake-platform.sh"
  log "Full off: deriv-teardown-platform-aws then terraform destroy"
}

main "$@"
