#!/bin/bash
# Called from deploy-platform.Jenkinsfile with required env vars set.
set -euo pipefail

HELM_LOG="${WORKSPACE:-/tmp}/helm-deploy.log"
: > "${HELM_LOG}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

log() {
  printf '[%s] %s\n' "$(date -Is)" "$*"
}

log_section() {
  echo ""
  log "========== $* =========="
}

deploy_preflight() {
  log_section "Pre-flight"
  log "Cluster: ${EKS_CLUSTER_NAME} (${AWS_REGION})"
  log "Release: ${HELM_RELEASE} namespace: ${HELM_NAMESPACE} image.tag: ${IMAGE_TAG}"

  kubectl get nodes -o wide || true
  helm version
  helm list -n "${HELM_NAMESPACE}" 2>/dev/null || true
  kubectl get pods -n "${HELM_NAMESPACE}" -o wide 2>/dev/null || true

  log_section "ECR image tags"
  local missing=0
  for repo in deriv-backend deriv-workers deriv-frontend; do
    if aws ecr describe-images --region "${AWS_REGION}" \
        --repository-name "${repo}" \
        --image-ids "imageTag=${IMAGE_TAG}" >/dev/null 2>&1; then
      log "  OK   ${ECR_REGISTRY}/${repo}:${IMAGE_TAG}"
    else
      log "  MISS ${ECR_REGISTRY}/${repo}:${IMAGE_TAG}"
      missing=1
    fi
  done
  if [[ "${missing}" -eq 1 ]]; then
    log "WARNING: one or more images missing in ECR (or Jenkins lacks ecr:DescribeImages)"
    log "WARNING: deploy may still work if images exist — check pod image pull events"
  fi
}

deploy_check_ebs_csi() {
  log_section "EBS CSI preflight"
  local addon_status=""
  local describe_err=""

  if addon_status=$(aws eks describe-addon \
    --cluster-name "${EKS_CLUSTER_NAME}" \
    --addon-name aws-ebs-csi-driver \
    --region "${AWS_REGION}" \
    --query addon.status \
    --output text 2>&1); then
    log "EKS add-on aws-ebs-csi-driver status=${addon_status}"
  else
    describe_err="${addon_status}"
    addon_status=""
    log "WARNING: aws eks describe-addon failed: ${describe_err}"
    log "WARNING: continuing if CSI controller pods are Running (check Jenkins IAM eks:DescribeAddon on addon ARN)"
  fi

  local csi_ok=0
  if kubectl get pods -n kube-system -l app.kubernetes.io/name=aws-ebs-csi-driver --no-headers 2>/dev/null \
      | grep -q Running; then
    csi_ok=1
  fi

  if [[ "${addon_status}" == "ACTIVE" && "${csi_ok}" -eq 1 ]]; then
    log "EBS CSI OK (add-on ACTIVE, controller pods Running)"
    return 0
  fi

  if [[ "${csi_ok}" -eq 1 ]]; then
    log "EBS CSI OK (controller pods Running; add-on API status=${addon_status:-unknown})"
    return 0
  fi

  if [[ "${addon_status}" != "ACTIVE" && -n "${addon_status}" ]]; then
    log "ERROR: aws-ebs-csi-driver add-on status=${addon_status} (expected ACTIVE)"
  else
    log "ERROR: no Running aws-ebs-csi-driver pods in kube-system"
    kubectl get pods -n kube-system 2>/dev/null | grep -i ebs || true
  fi
  log "Fix: terraform apply (EBS CSI add-on) and ensure Jenkins role can DescribeAddon on addon/*"
  exit 1
}

# Clear pending-upgrade / pending-install locks from aborted or timed-out Helm runs.
deploy_helm_unlock() {
  log_section "Helm release lock check"

  if ! helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" >/dev/null 2>&1; then
    log "No existing release — fresh install"
    return 0
  fi

  local status
  status=$(helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" -o json | jq -r '.info.status // "unknown"')
  log "Current status: ${status}"

  if [[ "${status}" != pending-* && "${status}" != "failed" ]]; then
    log "Release ready for upgrade"
    return 0
  fi

  if [[ "${status}" == "failed" ]]; then
    log "Release status is failed — skipping rollback (upgrade --install will reconcile)"
    return 0
  fi

  log "Clearing stuck Helm release (status=${status})..."

  local last_deployed
  last_deployed=$(helm history "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" -o json \
    | jq -r '[.[] | select(.status == "deployed") | .revision] | last // empty')

  if [[ -n "${last_deployed}" ]]; then
    log "Rolling back to last deployed revision ${last_deployed}"
    helm rollback "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" "${last_deployed}" --wait --timeout 5m || true
  else
    log "No deployed revision found; trying rollback 0"
    helm rollback "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" 0 2>/dev/null || true
  fi

  status=$(helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" -o json 2>/dev/null | jq -r '.info.status // empty' || true)
  if [[ "${status}" == pending-* ]]; then
    log "Still pending; deleting pending Helm release secret(s)"
    while read -r rev; do
      [[ -n "${rev}" ]] || continue
      local secret_name="sh.helm.release.v1.${HELM_RELEASE}.v${rev}"
      kubectl delete secret -n "${HELM_NAMESPACE}" "${secret_name}" --ignore-not-found=true
      log "Deleted ${secret_name}"
    done < <(helm history "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" -o json \
      | jq -r '.[] | select(.status | test("pending")) | .revision')
  fi

  status=$(helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" -o json 2>/dev/null | jq -r '.info.status // "none"' || echo "none")
  log "Status after unlock: ${status}"
}

deploy_sync_secrets() {
  log_section "Secrets Manager → Kubernetes"
  log "Reading ${PLATFORM_SECRET_ID}..."
  APP_JSON=$(aws secretsmanager get-secret-value \
    --region "${AWS_REGION}" \
    --secret-id "${PLATFORM_SECRET_ID}" \
    --query SecretString --output text)

  POSTGRES_PASSWORD=$(echo "${APP_JSON}" | jq -r '.POSTGRES_PASSWORD // empty')
  AUTH_SECRET=$(echo "${APP_JSON}" | jq -r '.AUTH_SECRET // empty')
  OPENAI_API_KEY=$(echo "${APP_JSON}" | jq -r '.OPENAI_API_KEY // empty')

  for required_key in POSTGRES_PASSWORD AUTH_SECRET; do
    if [[ -z "${!required_key}" ]]; then
      log "ERROR: ${PLATFORM_SECRET_ID} missing JSON key: ${required_key}"
      exit 1
    fi
  done
  log "Loaded keys: POSTGRES_PASSWORD, AUTH_SECRET${OPENAI_API_KEY:+, OPENAI_API_KEY}"

  # Bitnami PostgreSQL chart expects adminPasswordKey (default: postgres-password) in existingSecret.
  kubectl create secret generic "${APP_SECRET}" \
    --namespace "${HELM_NAMESPACE}" \
    --from-literal=POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    --from-literal=postgres-password="${POSTGRES_PASSWORD}" \
    --from-literal=AUTH_SECRET="${AUTH_SECRET}" \
    --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY}" \
    --dry-run=client -o yaml | kubectl apply -f -
  log "Synced secret ${APP_SECRET}"

  export POSTGRES_PASSWORD
}

# StatefulSet pods are not always recreated when only the image changes; delete stale pods
# still pulling removed docker.io/bitnami/* tags before Helm waits on readiness.
deploy_fixup_bitnami_image_pods() {
  log_section "Bitnami image pod fixup"
  local pod img
  for pod in deriv-platform-postgresql-0; do
    img=$(kubectl get pod "${pod}" -n "${HELM_NAMESPACE}" \
      -o jsonpath='{.spec.containers[0].image}' 2>/dev/null || true)
    if [[ -z "${img}" ]]; then
      continue
    fi
    if [[ "${img}" == *"/bitnami/"* && "${img}" != *bitnamilegacy* ]]; then
      log "  deleting ${pod} (stale image ${img})"
      kubectl delete pod "${pod}" -n "${HELM_NAMESPACE}" --wait=false || true
    fi
  done
}

deploy_restart_data_statefulsets() {
  log_section "Restart data StatefulSets"
  for sts in deriv-platform-postgresql deriv-platform-kafka-broker deriv-platform-kafka-controller; do
    if kubectl rollout restart "statefulset/${sts}" -n "${HELM_NAMESPACE}" 2>/dev/null; then
      log "  restarted statefulset/${sts}"
    fi
  done
}

deploy_wait_for_platform() {
  log_section "Wait for platform pods"
  local deadline=$((SECONDS + 900))
  local ok=0

  while (( SECONDS < deadline )); do
    local not_ready
    not_ready=$(kubectl get pods -n "${HELM_NAMESPACE}" \
      -l app.kubernetes.io/instance="${HELM_RELEASE}" \
      --field-selector=status.phase!=Running,status.phase!=Succeeded \
      --no-headers 2>/dev/null | wc -l | tr -d ' ')
    if [[ "${not_ready}" -eq 0 ]]; then
      ok=1
      break
    fi
    log "  ${not_ready} pod(s) not Running yet..."
    sleep 15
  done

  kubectl get pods -n "${HELM_NAMESPACE}" -o wide || true
  if [[ "${ok}" -ne 1 ]]; then
    log "ERROR: platform pods not all Running within 15m"
    return 1
  fi
  log "All platform pods Running"
}

deploy_wait_for_ingress() {
  log_section "Wait for Ingress ALB address"
  local deadline=$((SECONDS + 600))
  local addr=""

  while (( SECONDS < deadline )); do
    addr=$(kubectl get ingress "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" \
      -o jsonpath='{.status.loadBalancer.ingress[0].hostname}' 2>/dev/null || true)
    if [[ -n "${addr}" ]]; then
      log "  Ingress ADDRESS: ${addr}"
      kubectl get ingress "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" -o wide || true
      return 0
    fi
    log "  waiting for Ingress load balancer (ALB controller provisioning)..."
    sleep 15
  done

  log "WARNING: Ingress has no hostname after 10m — check ALB controller logs"
  kubectl describe ingress "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" 2>/dev/null | tail -30 || true
  return 1
}

deploy_helm() {
  deploy_helm_unlock

  log_section "Helm upgrade --install"
  HELM_PG_PASS_FILE=$(mktemp)
  chmod 600 "${HELM_PG_PASS_FILE}"
  printf '%s' "${POSTGRES_PASSWORD}" > "${HELM_PG_PASS_FILE}"

  HELM_SET_INGRESS=()
  if [[ -n "${APP_ACM_CERTIFICATE_ARN:-}" && -n "${API_ACM_CERTIFICATE_ARN:-}" ]]; then
    INGRESS_CERT_ARNS="${APP_ACM_CERTIFICATE_ARN},${API_ACM_CERTIFICATE_ARN}"
    HELM_SET_INGRESS=(
      --set-literal "ingress.certificateArns=${INGRESS_CERT_ARNS}"
      --set "ingress.hosts.app=${APP_DOMAIN}"
      --set "ingress.hosts.api=${API_DOMAIN}"
      --set "frontend.env.NEXT_PUBLIC_BOT_BASE_URL=https://${API_DOMAIN}"
    )
  else
    log "WARNING: ACM ARNs unset — ingress TLS may not be updated"
  fi

  HELM_EXTRA=()
  if [[ "${HELM_DEBUG:-true}" == "true" ]]; then
    HELM_EXTRA+=(--debug)
    log "Helm --debug enabled (install progress in console + ${HELM_LOG})"
  fi

  log "Helm applies manifests first; data pods restart separately (up to ~15m). Log: ${HELM_LOG}"

  set -o pipefail
  helm upgrade --install "${HELM_RELEASE}" "${HELM_CHART}" \
    --namespace "${HELM_NAMESPACE}" \
    -f "${HELM_CHART}/values.yaml" \
    -f "${HELM_CHART}/values-dev.yaml" \
    --set "image.registry=${ECR_REGISTRY}" \
    --set "image.tag=${IMAGE_TAG}" \
    --set "global.namespaceOverride=${HELM_NAMESPACE}" \
    --set "global.security.allowInsecureImages=true" \
    --set "namespace.name=${HELM_NAMESPACE}" \
    --set "namespace.create=false" \
    --set "secrets.existingSecret=${APP_SECRET}" \
    --set "postgresql.auth.existingSecret=${APP_SECRET}" \
    --set "postgresql.image.registry=docker.io" \
    --set "postgresql.image.repository=bitnamilegacy/postgresql" \
    --set "postgresql.image.tag=16.4.0-debian-12-r14" \
    --set "kafka.image.registry=docker.io" \
    --set "kafka.image.repository=bitnamilegacy/kafka" \
    --set "kafka.image.tag=3.8.0-debian-12-r5" \
    --set-file "global.postgresql.auth.password=${HELM_PG_PASS_FILE}" \
    "${HELM_SET_INGRESS[@]}" \
    "${HELM_EXTRA[@]}" \
    2>&1 | tee -a "${HELM_LOG}"
  rm -f "${HELM_PG_PASS_FILE}"

  log "Helm apply finished"

  deploy_fixup_bitnami_image_pods
  deploy_restart_data_statefulsets
  deploy_wait_for_platform
  deploy_wait_for_ingress
}

deploy_postflight() {
  log_section "Post-deploy status"
  helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" || true
  kubectl get pvc -n "${HELM_NAMESPACE}" || true
  kubectl get all -n "${HELM_NAMESPACE}" -o wide || true
  kubectl get events -n "${HELM_NAMESPACE}" --sort-by='.lastTimestamp' 2>/dev/null | tail -20 || true

  log "Pods not Running/Completed:"
  kubectl get pods -n "${HELM_NAMESPACE}" --field-selector=status.phase!=Running,status.phase!=Succeeded 2>/dev/null || true
}

main() {
  aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
  helm dependency update "${HELM_CHART}"
  kubectl create namespace "${HELM_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

  deploy_preflight
  deploy_check_ebs_csi
  "${SCRIPT_DIR}/eks-ingress-controllers.sh"
  deploy_sync_secrets
  deploy_helm
  if [[ "${MONITORING_ENABLED:-true}" == "true" ]]; then
    "${SCRIPT_DIR}/eks-monitoring.sh"
  fi
  deploy_postflight
}

main "$@"
