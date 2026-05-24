#!/bin/bash
# Run on failure/abort (Jenkins post always). Best-effort; does not fail the build.
set +e

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }

HELM_NAMESPACE="${HELM_NAMESPACE:-deriv-dev}"
HELM_RELEASE="${HELM_RELEASE:-deriv-platform}"
EKS_CLUSTER_NAME="${EKS_CLUSTER_NAME:-deriv-ai-bot-dev}"
AWS_REGION="${AWS_REGION:-us-west-1}"
HELM_LOG="${WORKSPACE:-/tmp}/helm-deploy.log"

log "========== Deploy diagnostics (always) =========="

if [[ -f "${HELM_LOG}" ]]; then
  log "Last 80 lines of Helm log (${HELM_LOG}):"
  tail -80 "${HELM_LOG}"
else
  log "No Helm log at ${HELM_LOG}"
fi

if ! command -v kubectl >/dev/null 2>&1; then
  log "kubectl not available — skip cluster snapshot"
  exit 0
fi

aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}" >/dev/null 2>&1

log "Pods:"
kubectl get pods -n "${HELM_NAMESPACE}" -o wide 2>/dev/null || true

log "Recent events:"
kubectl get events -n "${HELM_NAMESPACE}" --sort-by='.lastTimestamp' 2>/dev/null | tail -25 || true

log "Helm release:"
helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" 2>/dev/null || true

log "Problem pod descriptions (first 3 not Running):"
kubectl get pods -n "${HELM_NAMESPACE}" -o jsonpath='{range .items[?(@.status.phase!="Running")]}{.metadata.name}{"\n"}{end}' 2>/dev/null \
  | head -3 \
  | while read -r pod; do
      [[ -n "${pod}" ]] || continue
      log "--- describe pod/${pod} (events) ---"
      kubectl describe pod "${pod}" -n "${HELM_NAMESPACE}" 2>/dev/null | sed -n '/^Events:/,$p' | head -20
    done

exit 0
