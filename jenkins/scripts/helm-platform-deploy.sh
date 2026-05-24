#!/bin/bash
# Called from deploy-platform.Jenkinsfile with required env vars set.
set -euo pipefail

HELM_LOG="${WORKSPACE:-/tmp}/helm-deploy.log"
: > "${HELM_LOG}"

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
    log "WARNING: one or more images missing in ECR — Helm may wait until timeout (ImagePullBackOff)"
  fi
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

  kubectl create secret generic "${APP_SECRET}" \
    --namespace "${HELM_NAMESPACE}" \
    --from-literal=POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
    --from-literal=AUTH_SECRET="${AUTH_SECRET}" \
    --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY}" \
    --dry-run=client -o yaml | kubectl apply -f -
  log "Synced secret ${APP_SECRET}"

  export POSTGRES_PASSWORD
}

deploy_helm() {
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

  log "First install can take up to 20m (Postgres, Kafka, apps). Watch Helm lines below."
  log "Log file: ${HELM_LOG}"

  set -o pipefail
  helm upgrade --install "${HELM_RELEASE}" "${HELM_CHART}" \
    --namespace "${HELM_NAMESPACE}" \
    -f "${HELM_CHART}/values.yaml" \
    -f "${HELM_CHART}/values-dev.yaml" \
    --set "image.registry=${ECR_REGISTRY}" \
    --set "image.tag=${IMAGE_TAG}" \
    --set "global.namespaceOverride=${HELM_NAMESPACE}" \
    --set "namespace.name=${HELM_NAMESPACE}" \
    --set "namespace.create=false" \
    --set "secrets.existingSecret=${APP_SECRET}" \
    --set "postgresql.auth.existingSecret=${APP_SECRET}" \
    --set-file "global.postgresql.auth.password=${HELM_PG_PASS_FILE}" \
    "${HELM_SET_INGRESS[@]}" \
    --wait \
    --timeout 20m \
    "${HELM_EXTRA[@]}" \
    2>&1 | tee -a "${HELM_LOG}"
  rm -f "${HELM_PG_PASS_FILE}"

  log "Helm finished successfully"
}

deploy_postflight() {
  log_section "Post-deploy status"
  helm status "${HELM_RELEASE}" -n "${HELM_NAMESPACE}" || true
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
  deploy_sync_secrets
  deploy_helm
  deploy_postflight
}

main "$@"
