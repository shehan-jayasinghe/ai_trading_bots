// Deploy full platform: preflight → EKS addons → postgres → kafka → apps → ingress → monitoring.
// Script path: jenkins/pipelines/deploy-platform.Jenkinsfile
// Infra config: Jenkins global env vars (see jenkins/global-env.example)

pipeline {
    agent any

    parameters {
        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'ECR tag for backend, workers, frontend')
        booleanParam(name: 'HELM_DEBUG', defaultValue: true, description: 'Helm --debug for deriv-apps')
        booleanParam(name: 'DEPLOY_ADDONS', defaultValue: true, description: 'Run eks-cluster-addons chart')
        booleanParam(name: 'DEPLOY_MONITORING', defaultValue: true, description: 'Run eks-monitoring chart')
    }

    environment {
        HELM_APPS_RELEASE = 'deriv-apps'
        HELM_NAMESPACE = 'deriv-dev'
        APP_SECRET = 'deriv-platform-app-secrets'
    }

    stages {
        stage('Checkout') { steps { checkout scm } }

        stage('Configure') {
            steps {
                script {
                    def common = load 'jenkins/pipelines/_common.groovy'

                    env.AWS_REGION = common.envOrCfg(this, 'AWS_REGION', 'us-west-1')
                    env.ECR_REGISTRY = common.requireEnv(this, 'ECR_REGISTRY')
                    env.EKS_CLUSTER_NAME = common.envOrCfg(this, 'EKS_CLUSTER_NAME', 'deriv-ai-bot-dev')
                    env.VPC_ID = common.requireEnv(this, 'VPC_ID')
                    env.ALB_CONTROLLER_ROLE_ARN = common.requireEnv(this, 'ALB_CONTROLLER_ROLE_ARN')
                    env.EXTERNAL_DNS_ROLE_ARN = common.requireEnv(this, 'EXTERNAL_DNS_ROLE_ARN')
                    env.EXTERNAL_DNS_DOMAIN_FILTER = common.envOrCfg(this, 'EXTERNAL_DNS_DOMAIN_FILTER', 'testenvlab.shop')
                    env.EXTERNAL_DNS_TXT_OWNER_ID = common.envOrCfg(this, 'EXTERNAL_DNS_TXT_OWNER_ID', 'deriv-dev')
                    env.APP_ACM_CERTIFICATE_ARN = common.envOrCfg(this, 'APP_ACM_CERTIFICATE_ARN', '')
                    env.API_ACM_CERTIFICATE_ARN = common.envOrCfg(this, 'API_ACM_CERTIFICATE_ARN', '')
                    env.APP_DOMAIN = common.envOrCfg(this, 'APP_DOMAIN', 'app.testenvlab.shop')
                    env.API_DOMAIN = common.envOrCfg(this, 'API_DOMAIN', 'api.testenvlab.shop')
                    env.PLATFORM_SECRET_ID = common.envOrCfg(this, 'PLATFORM_SECRET_ID', 'deriv-ai-bot/dev/platform')
                    env.LOKI_S3_BUCKET = common.envOrCfg(this, 'LOKI_S3_BUCKET', '')
                    env.LOKI_ROLE_ARN = common.envOrCfg(this, 'LOKI_ROLE_ARN', '')
                    env.GRAFANA_SECRET_ID = common.envOrCfg(this, 'GRAFANA_SECRET_ID', 'deriv-ai-bot/dev/grafana')
                    env.GRAFANA_DOMAIN = common.envOrCfg(this, 'GRAFANA_DOMAIN', 'grafana.testenvlab.shop')
                    env.GRAFANA_ACM_CERTIFICATE_ARN = common.envOrCfg(this, 'GRAFANA_ACM_CERTIFICATE_ARN', '')
                    env.IMAGE_TAG = params.IMAGE_TAG.trim()
                    env.HELM_DEBUG = params.HELM_DEBUG ? 'true' : 'false'
                    env.MONITORING_ENABLED = params.DEPLOY_MONITORING ? 'true' : 'false'
                    env.SKIP_PREFLIGHT = 'false'
                }
            }
        }

        stage('Preflight') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail
chmod +x jenkins/scripts/deploy/preflight/platform-preflight.sh
jenkins/scripts/deploy/preflight/platform-preflight.sh
'''
            }
        }

        stage('Helm EKS addons') {
            when { expression { return params.DEPLOY_ADDONS } }
            steps {
                sh '''#!/bin/bash
set -euo pipefail
chmod +x jenkins/scripts/deploy/infrastructure/*.sh
jenkins/scripts/deploy/infrastructure/helm-eks-addons-deploy.sh
'''
            }
        }

        stage('Helm platform') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail
export SKIP_PREFLIGHT=true
chmod +x jenkins/scripts/deploy/helm-platform-deploy.sh \
  jenkins/scripts/deploy/data/*.sh \
  jenkins/scripts/deploy/app/*.sh
jenkins/scripts/deploy/helm-platform-deploy.sh
'''
            }
        }

        stage('Helm monitoring') {
            when { expression { return params.DEPLOY_MONITORING } }
            steps {
                sh '''#!/bin/bash
set -euo pipefail
chmod +x jenkins/scripts/deploy/monitoring/helm-monitoring-deploy.sh
jenkins/scripts/deploy/monitoring/helm-monitoring-deploy.sh
'''
            }
        }

        stage('Verify rollouts') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail
aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
for dep in deriv-apps-backend deriv-apps-frontend deriv-apps-planner deriv-apps-executor; do
  kubectl rollout status "deployment/${dep}" -n "${HELM_NAMESPACE}" --timeout=5m
done
'''
            }
        }
    }

    post {
        always {
            sh 'chmod +x jenkins/scripts/deploy/diagnostics/deploy-diagnostics.sh; jenkins/scripts/deploy/diagnostics/deploy-diagnostics.sh || true'
            archiveArtifacts artifacts: 'helm-deploy.log', allowEmptyArchive: true, fingerprint: false
        }
    }
}
