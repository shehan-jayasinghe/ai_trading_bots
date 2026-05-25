#!/bin/bash
# Restart ALB controller after Helm upgrade so webhook TLS matches caBundle.
set -euo pipefail

log() { printf '[%s] %s\n' "$(date -Is)" "$*"; }

if ! kubectl get deployment aws-load-balancer-controller -n kube-system >/dev/null 2>&1; then
  log "aws-load-balancer-controller not found — skip post-install"
  exit 0
fi

log "restarting ALB controller (webhook TLS sync)"
kubectl rollout restart deployment/aws-load-balancer-controller -n kube-system
kubectl rollout status deployment/aws-load-balancer-controller -n kube-system --timeout=5m

deadline=$((SECONDS + 120))
while (( SECONDS < deadline )); do
  if kubectl get endpoints aws-load-balancer-webhook-service -n kube-system \
      -o jsonpath='{.subsets[0].addresses[0].ip}' 2>/dev/null | grep -q .; then
    log "ALB webhook endpoints ready"
    exit 0
  fi
  sleep 5
done

log "ERROR: aws-load-balancer-webhook-service has no endpoints"
exit 1
