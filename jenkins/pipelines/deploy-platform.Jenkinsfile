// Deploy deriv-platform Helm release to EKS (backend + workers + frontend share image.tag).
// Jenkins job: Pipeline from SCM, script path: jenkins/pipelines/deploy-platform.Jenkinsfile
//
// Infra config: Jenkins globals or jenkins/config/dev.env (ECR, EKS, ACM, domains).
// App secrets: AWS Secrets Manager (PLATFORM_SECRET_ID) → synced to K8s before Helm.

pipeline {
    agent any

    parameters {
        string(
            name: 'IMAGE_TAG',
            defaultValue: 'latest',
            description: 'ECR tag applied to backend, workers, and frontend (e.g. master-abc1234)'
        )
    }

    environment {
        HELM_CHART = 'deploy/helm/deriv-platform'
        HELM_RELEASE = 'deriv-platform'
        HELM_NAMESPACE = 'deriv-dev'
        APP_SECRET = 'deriv-platform-app-secrets'
        PLATFORM_SECRET_ID = 'deriv-ai-bot/dev/platform'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Configure') {
            steps {
                script {
                    def common = load 'jenkins/pipelines/_common.groovy'
                    def cfg = common.loadDevConfig(this)

                    env.AWS_REGION = cfg.get('AWS_REGION', env.AWS_REGION ?: 'us-west-1')
                    env.ECR_REGISTRY = cfg.get('ECR_REGISTRY', env.ECR_REGISTRY ?: '')
                    env.EKS_CLUSTER_NAME = cfg.get('EKS_CLUSTER_NAME', env.EKS_CLUSTER_NAME ?: 'deriv-ai-bot-dev')
                    env.APP_ACM_CERTIFICATE_ARN = cfg.get('APP_ACM_CERTIFICATE_ARN', env.APP_ACM_CERTIFICATE_ARN ?: '')
                    env.API_ACM_CERTIFICATE_ARN = cfg.get('API_ACM_CERTIFICATE_ARN', env.API_ACM_CERTIFICATE_ARN ?: '')
                    env.APP_DOMAIN = cfg.get('APP_DOMAIN', env.APP_DOMAIN ?: 'app.testenvlab.shop')
                    env.API_DOMAIN = cfg.get('API_DOMAIN', env.API_DOMAIN ?: 'api.testenvlab.shop')
                    env.PLATFORM_SECRET_ID = cfg.get('PLATFORM_SECRET_ID', env.PLATFORM_SECRET_ID ?: 'deriv-ai-bot/dev/platform')

                    if (!env.ECR_REGISTRY?.trim()) {
                        error('Set ECR_REGISTRY in Jenkins global env or jenkins/config/dev.env')
                    }
                    if (!env.PLATFORM_SECRET_ID?.trim()) {
                        error('Set PLATFORM_SECRET_ID in Jenkins global env or jenkins/config/dev.env')
                    }
                    if (!params.IMAGE_TAG?.trim()) {
                        error('IMAGE_TAG parameter is required')
                    }
                    env.IMAGE_TAG = params.IMAGE_TAG.trim()

                    echo "Deploy ${env.HELM_RELEASE} to ${env.EKS_CLUSTER_NAME} (${env.AWS_REGION}) tag=${env.IMAGE_TAG} secrets=${env.PLATFORM_SECRET_ID}"
                }
            }
        }

        stage('Helm deploy') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail

aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"

helm dependency update "${HELM_CHART}"

kubectl create namespace "${HELM_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

echo "Loading platform secrets from AWS Secrets Manager (${PLATFORM_SECRET_ID})..."
APP_JSON=$(aws secretsmanager get-secret-value \
  --region "${AWS_REGION}" \
  --secret-id "${PLATFORM_SECRET_ID}" \
  --query SecretString --output text)

POSTGRES_PASSWORD=$(echo "${APP_JSON}" | jq -r '.POSTGRES_PASSWORD // empty')
AUTH_SECRET=$(echo "${APP_JSON}" | jq -r '.AUTH_SECRET // empty')
OPENAI_API_KEY=$(echo "${APP_JSON}" | jq -r '.OPENAI_API_KEY // empty')

for required_key in POSTGRES_PASSWORD AUTH_SECRET; do
  if [[ -z "${!required_key}" ]]; then
    echo "ERROR: ${PLATFORM_SECRET_ID} missing required JSON key: ${required_key}"
    echo "Populate with: terraform output -raw platform_secret_populate_command"
    exit 1
  fi
done

echo "Syncing K8s secret ${APP_SECRET} in ${HELM_NAMESPACE}..."
kubectl create secret generic "${APP_SECRET}" \
  --namespace "${HELM_NAMESPACE}" \
  --from-literal=POSTGRES_PASSWORD="${POSTGRES_PASSWORD}" \
  --from-literal=AUTH_SECRET="${AUTH_SECRET}" \
  --from-literal=OPENAI_API_KEY="${OPENAI_API_KEY}" \
  --dry-run=client -o yaml | kubectl apply -f -

HELM_PG_PASS_FILE=$(mktemp)
chmod 600 "${HELM_PG_PASS_FILE}"
printf '%s' "${POSTGRES_PASSWORD}" > "${HELM_PG_PASS_FILE}"
trap 'rm -f "${HELM_PG_PASS_FILE}"' EXIT

HELM_SET_INGRESS=()
if [[ -n "${APP_ACM_CERTIFICATE_ARN}" && -n "${API_ACM_CERTIFICATE_ARN}" ]]; then
  INGRESS_CERT_ARNS="${APP_ACM_CERTIFICATE_ARN},${API_ACM_CERTIFICATE_ARN}"
  HELM_SET_INGRESS=(
    --set-literal "ingress.certificateArns=${INGRESS_CERT_ARNS}"
    --set "ingress.hosts.app=${APP_DOMAIN}"
    --set "ingress.hosts.api=${API_DOMAIN}"
    --set "frontend.env.NEXT_PUBLIC_BOT_BASE_URL=https://${API_DOMAIN}"
  )
else
  echo "WARNING: APP_ACM_CERTIFICATE_ARN or API_ACM_CERTIFICATE_ARN unset — ingress TLS may not be updated"
fi

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
  --timeout 20m
'''
            }
        }

        stage('Verify rollouts') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail

kubectl get pods -n "${HELM_NAMESPACE}"

for dep in "${HELM_RELEASE}-backend" "${HELM_RELEASE}-frontend" "${HELM_RELEASE}-planner" "${HELM_RELEASE}-executor"; do
  kubectl rollout status "deployment/${dep}" -n "${HELM_NAMESPACE}" --timeout=5m
done
'''
            }
        }
    }

    post {
        success {
            echo "Deployed ${env.HELM_RELEASE} to EKS namespace ${env.HELM_NAMESPACE} with tag ${env.IMAGE_TAG}"
        }
    }
}
