// Deploy deriv-platform Helm release to EKS (backend + workers + frontend share image.tag).
// Jenkins job: Pipeline from SCM, script path: jenkins/pipelines/deploy-platform.Jenkinsfile
//
// Prerequisites: terraform + ansible eks-platform.yml (cluster, secret, ingress controllers).
// Set Jenkins globals (or jenkins/config/dev.env): ECR_REGISTRY, AWS_REGION, EKS_CLUSTER_NAME,
// APP_ACM_CERTIFICATE_ARN, API_ACM_CERTIFICATE_ARN (for ingress).

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

                    if (!env.ECR_REGISTRY?.trim()) {
                        error('Set ECR_REGISTRY in Jenkins global env or jenkins/config/dev.env')
                    }
                    if (!params.IMAGE_TAG?.trim()) {
                        error('IMAGE_TAG parameter is required')
                    }
                    env.IMAGE_TAG = params.IMAGE_TAG.trim()

                    echo "Deploy ${env.HELM_RELEASE} to ${env.EKS_CLUSTER_NAME} (${env.AWS_REGION}) with image.tag=${env.IMAGE_TAG}"
                }
            }
        }

        stage('Helm deploy') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail

aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"

helm dependency update "${HELM_CHART}"

# Idempotent: create namespace if missing; chart does not render Namespace (namespace.create=false)
kubectl create namespace "${HELM_NAMESPACE}" --dry-run=client -o yaml | kubectl apply -f -

# App secrets live in cluster (Ansible eks-platform.yml). Load for Bitnami Postgres upgrade + preflight.
secret_key() {
  kubectl get secret --namespace "${HELM_NAMESPACE}" "${APP_SECRET}" \
    -o "jsonpath={.data.${1}}" 2>/dev/null | base64 -d
}

POSTGRES_PASSWORD=$(secret_key POSTGRES_PASSWORD)
AUTH_SECRET=$(secret_key AUTH_SECRET)
OPENAI_API_KEY=$(secret_key OPENAI_API_KEY || true)

for required_key in POSTGRES_PASSWORD AUTH_SECRET; do
  if [[ -z "${!required_key}" ]]; then
    echo "ERROR: ${APP_SECRET} missing or empty key ${required_key} in ${HELM_NAMESPACE}"
    echo "Run infrastructure/ansible playbooks/eks-platform.yml first."
    exit 1
  fi
done

loaded_keys="POSTGRES_PASSWORD, AUTH_SECRET"
if [[ -n "${OPENAI_API_KEY}" ]]; then
  loaded_keys="${loaded_keys}, OPENAI_API_KEY"
fi
echo "Loaded cluster secret ${APP_SECRET} (${loaded_keys})"

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
  --set "global.postgresql.auth.password=${POSTGRES_PASSWORD}" \
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
