#!/bin/bash
# Deploy deriv-kafka Helm chart (Bitnami Kafka + optional topic bootstrap job).
set -euo pipefail

HELM_CHART="${HELM_CHART:-deploy/helm/deriv-kafka}"
HELM_RELEASE="${HELM_RELEASE:-deriv-kafka}"
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
  log_section "Helm deriv-kafka"
  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
  helm dependency update "${HELM_CHART}"
  deploy_helm_unlock

  local -a EXTRA=()
  [[ "${KAFKA_TOPICS_ENABLED:-}" == "true" ]] && EXTRA+=(--set kafkaTopics.enabled=true)

  helm upgrade --install "${HELM_RELEASE}" "${HELM_CHART}" \
    --namespace "${HELM_NAMESPACE}" \
    -f "${HELM_CHART}/values.yaml" \
    -f "${HELM_CHART}/values-dev.yaml" \
    --set "global.namespaceOverride=${HELM_NAMESPACE}" \
    --set "global.security.allowInsecureImages=true" \
    --set "namespace.name=${HELM_NAMESPACE}" \
    --set "kafka.image.registry=docker.io" \
    --set "kafka.image.repository=bitnamilegacy/kafka" \
    --set "kafka.image.tag=3.8.0-debian-12-r5" \
    "${EXTRA[@]}"

  for sts in "${HELM_RELEASE}-broker" "${HELM_RELEASE}-controller"; do
    kubectl rollout restart "statefulset/${sts}" -n "${HELM_NAMESPACE}" 2>/dev/null || true
  done
  for sts in "${HELM_RELEASE}-kafka-broker" "${HELM_RELEASE}-kafka-controller"; do
    kubectl rollout restart "statefulset/${sts}" -n "${HELM_NAMESPACE}" 2>/dev/null || true
  done
  log "deriv-kafka deploy OK"
}

main "$@"
