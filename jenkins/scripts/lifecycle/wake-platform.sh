#!/bin/bash
# Wake dev platform: start Jenkins EC2, scale EKS nodes up, optionally run full Helm deploy.
set -euo pipefail

AWS_REGION="${AWS_REGION:-us-west-1}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"
EKS_NODE_DESIRED_SIZE="${EKS_NODE_DESIRED_SIZE:-2}"
EKS_NODE_MAX_SIZE="${EKS_NODE_MAX_SIZE:-2}"
WAKE_START_JENKINS="${WAKE_START_JENKINS:-true}"
WAKE_RUN_HELM_DEPLOY="${WAKE_RUN_HELM_DEPLOY:-true}"
WAKE_IMAGE_TAG="${WAKE_IMAGE_TAG:-latest}"
JENKINS_INSTANCE_NAME_TAG="${JENKINS_INSTANCE_NAME_TAG:-deriv-ai-bot-jenkins-dev}"
NODE_READY_TIMEOUT_SECS="${NODE_READY_TIMEOUT_SECS:-600}"
HELM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
APP_SECRET="${APP_SECRET:-deriv-platform-app-secrets}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DEPLOY_ROOT="${SCRIPT_DIR}/../deploy"

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

start_jenkins_ec2() {
  [[ "${WAKE_START_JENKINS}" != "true" ]] && return 0

  log_section "Start Jenkins EC2"
  local instance_id="${JENKINS_INSTANCE_ID:-}"
  if [[ -z "${instance_id}" ]]; then
    instance_id=$(aws ec2 describe-instances --region "${AWS_REGION}" \
      --filters "Name=tag:Name,Values=${JENKINS_INSTANCE_NAME_TAG}" \
      --query 'Reservations[0].Instances[0].InstanceId' --output text 2>/dev/null || true)
  fi
  if [[ -z "${instance_id}" || "${instance_id}" == "None" ]]; then
    log "  Jenkins instance not found (tag Name=${JENKINS_INSTANCE_NAME_TAG})"
    return 0
  fi

  local state
  state=$(aws ec2 describe-instances --region "${AWS_REGION}" --instance-ids "${instance_id}" \
    --query 'Reservations[0].Instances[0].State.Name' --output text 2>/dev/null || true)
  if [[ "${state}" == "running" ]]; then
    log "  ${instance_id} already running"
    return 0
  fi
  if [[ "${state}" == "stopped" ]]; then
    log "  starting ${instance_id}"
    aws ec2 start-instances --region "${AWS_REGION}" --instance-ids "${instance_id}"
    aws ec2 wait instance-running --region "${AWS_REGION}" --instance-ids "${instance_id}" || true
    log "  Jenkins EC2 running (allow ~2m for Jenkins service after boot)"
    return 0
  fi
  log "  instance ${instance_id} state=${state} — not starting"
}

scale_eks_nodes_up() {
  log_section "Scale EKS node group up"
  if ! cluster_exists; then
    log "ERROR: EKS cluster ${EKS_CLUSTER_NAME} not found"
    exit 1
  fi

  local ng
  ng=$(eks_nodegroup_name)
  if [[ -z "${ng}" || "${ng}" == "None" ]]; then
    log "ERROR: no node group on cluster"
    exit 1
  fi

  log "  nodegroup=${ng} min=0 desired=${EKS_NODE_DESIRED_SIZE} max=${EKS_NODE_MAX_SIZE}"
  aws eks update-nodegroup-config \
    --cluster-name "${EKS_CLUSTER_NAME}" \
    --nodegroup-name "${ng}" \
    --region "${AWS_REGION}" \
    --scaling-config "minSize=0,maxSize=${EKS_NODE_MAX_SIZE},desiredSize=${EKS_NODE_DESIRED_SIZE}"

  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"

  log "  waiting for at least one Ready node (timeout ${NODE_READY_TIMEOUT_SECS}s)"
  local deadline=$((SECONDS + NODE_READY_TIMEOUT_SECS))
  while (( SECONDS < deadline )); do
    if kubectl get nodes --no-headers 2>/dev/null | awk '$2=="Ready"{found=1} END{exit !found}'; then
      kubectl get nodes -o wide
      log "  node(s) Ready"
      return 0
    fi
    sleep 15
  done

  log "ERROR: no Ready nodes within timeout"
  kubectl get nodes -o wide 2>/dev/null || true
  exit 1
}

run_helm_deploy() {
  [[ "${WAKE_RUN_HELM_DEPLOY}" != "true" ]] && return 0

  log_section "Helm deploy (restore replicas + Ingress)"
  require_env ECR_REGISTRY
  export IMAGE_TAG="${WAKE_IMAGE_TAG}"
  export MONITORING_ENABLED="${MONITORING_ENABLED:-true}"
  export SKIP_PREFLIGHT=false
  chmod +x "${DEPLOY_ROOT}/helm-platform-deploy.sh" \
    "${DEPLOY_ROOT}/preflight/platform-preflight.sh" \
    "${DEPLOY_ROOT}/infrastructure/helm-eks-addons-deploy.sh" \
    "${DEPLOY_ROOT}/infrastructure/alb-controller-post-install.sh" \
    "${DEPLOY_ROOT}/monitoring/helm-monitoring-deploy.sh"
  "${DEPLOY_ROOT}/preflight/platform-preflight.sh"
  "${DEPLOY_ROOT}/infrastructure/helm-eks-addons-deploy.sh"
  export SKIP_PREFLIGHT=true
  "${DEPLOY_ROOT}/helm-platform-deploy.sh"
  "${DEPLOY_ROOT}/monitoring/helm-monitoring-deploy.sh"
}

main() {
  log_section "Wake platform"
  require_env EKS_CLUSTER_NAME

  start_jenkins_ec2
  scale_eks_nodes_up
  run_helm_deploy

  log_section "Wake complete"
  log "Verify: kubectl get pods -n ${HELM_NAMESPACE:-deriv-dev}"
  log "URLs: https://${API_DOMAIN:-api.testenvlab.shop}/hello (after Ingress provisions)"
}

main "$@"
