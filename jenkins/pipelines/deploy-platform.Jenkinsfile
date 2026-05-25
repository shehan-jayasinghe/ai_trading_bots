// Deploy deriv-platform Helm release to EKS (backend + workers + frontend share image.tag).
// Jenkins job: Pipeline from SCM, script path: jenkins/pipelines/deploy-platform.Jenkinsfile
//
// Infra config: Jenkins globals or jenkins/config/dev.env (ECR, EKS, ACM, domains).
// App secrets: AWS Secrets Manager (PLATFORM_SECRET_ID) → synced to K8s before Helm.
// Install progress: Helm --debug streamed to console + workspace/helm-deploy.log

pipeline {
    agent any

    parameters {
        string(
            name: 'IMAGE_TAG',
            defaultValue: 'latest',
            description: 'ECR tag applied to backend, workers, and frontend (e.g. master-abc1234)'
        )
        booleanParam(
            name: 'HELM_DEBUG',
            defaultValue: true,
            description: 'Helm --debug during install (recommended for first deploy; shows wait progress)'
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
                    env.VPC_ID = cfg.get('VPC_ID', env.VPC_ID ?: '')
                    env.ALB_CONTROLLER_ROLE_ARN = cfg.get('ALB_CONTROLLER_ROLE_ARN', env.ALB_CONTROLLER_ROLE_ARN ?: '')
                    env.EXTERNAL_DNS_ROLE_ARN = cfg.get('EXTERNAL_DNS_ROLE_ARN', env.EXTERNAL_DNS_ROLE_ARN ?: '')
                    env.EXTERNAL_DNS_DOMAIN_FILTER = cfg.get('EXTERNAL_DNS_DOMAIN_FILTER', env.EXTERNAL_DNS_DOMAIN_FILTER ?: 'testenvlab.shop')
                    env.EXTERNAL_DNS_TXT_OWNER_ID = cfg.get('EXTERNAL_DNS_TXT_OWNER_ID', env.EXTERNAL_DNS_TXT_OWNER_ID ?: 'deriv-dev')
                    env.PLATFORM_SECRET_ID = cfg.get('PLATFORM_SECRET_ID', env.PLATFORM_SECRET_ID ?: 'deriv-ai-bot/dev/platform')
                    env.LOKI_S3_BUCKET = cfg.get('LOKI_S3_BUCKET', env.LOKI_S3_BUCKET ?: '')
                    env.LOKI_ROLE_ARN = cfg.get('LOKI_ROLE_ARN', env.LOKI_ROLE_ARN ?: '')
                    env.MONITORING_ENABLED = cfg.get('MONITORING_ENABLED', env.MONITORING_ENABLED ?: 'true')
                    env.HELM_DEBUG = params.HELM_DEBUG ? 'true' : 'false'

                    if (!env.ECR_REGISTRY?.trim()) {
                        error('Set ECR_REGISTRY in Jenkins global env or jenkins/config/dev.env')
                    }
                    if (!env.PLATFORM_SECRET_ID?.trim()) {
                        error('Set PLATFORM_SECRET_ID in Jenkins global env or jenkins/config/dev.env')
                    }
                    if (!params.IMAGE_TAG?.trim()) {
                        error('IMAGE_TAG parameter is required')
                    }
                    if (!env.VPC_ID?.trim()) {
                        error('Set VPC_ID in Jenkins global env or jenkins/config/dev.env')
                    }
                    if (!env.ALB_CONTROLLER_ROLE_ARN?.trim()) {
                        error('Set ALB_CONTROLLER_ROLE_ARN in Jenkins global env or jenkins/config/dev.env')
                    }
                    if (!env.EXTERNAL_DNS_ROLE_ARN?.trim()) {
                        error('Set EXTERNAL_DNS_ROLE_ARN in Jenkins global env or jenkins/config/dev.env')
                    }
                    env.IMAGE_TAG = params.IMAGE_TAG.trim()

                    echo "Deploy ${env.HELM_RELEASE} → ${env.EKS_CLUSTER_NAME} tag=${env.IMAGE_TAG} helm_debug=${env.HELM_DEBUG}"
                }
            }
        }

        stage('Helm deploy') {
            steps {
                sh 'chmod +x
                 jenkins/scripts/helm-platform-deploy.sh
                 jenkins/scripts/eks-ingress-controllers.sh
                 jenkins/scripts/eks-monitoring.sh
                 jenkins/scripts/deploy-diagnostics.sh'
                sh 'jenkins/scripts/helm-platform-deploy.sh'
            }
        }

        stage('Verify rollouts') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail
aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
for dep in "${HELM_RELEASE}-backend" "${HELM_RELEASE}-frontend" "${HELM_RELEASE}-planner" "${HELM_RELEASE}-executor"; do
  echo "Rollout: ${dep}"
  kubectl rollout status "deployment/${dep}" -n "${HELM_NAMESPACE}" --timeout=5m
done
'''
            }
        }
    }

    post {
        always {
            sh 'jenkins/scripts/deploy-diagnostics.sh || true'
            archiveArtifacts artifacts: 'helm-deploy.log', allowEmptyArchive: true, fingerprint: false
        }
        success {
            echo "Deployed ${env.HELM_RELEASE} to ${env.HELM_NAMESPACE} with tag ${env.IMAGE_TAG}"
        }
        failure {
            echo "Deploy failed — see console, helm-deploy.log artifact, and diagnostics above"
        }
        aborted {
            echo "Deploy aborted — partial release may exist; check helm-deploy.log and diagnostics"
        }
    }
}
