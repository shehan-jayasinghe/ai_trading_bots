// Wake dev stack: start Jenkins, scale EKS nodes up, run deriv-deploy Helm flow.
// Jenkins job: jenkins/pipelines/wake-platform.Jenkinsfile

pipeline {
    agent any

    parameters {
        string(name: 'IMAGE_TAG', defaultValue: 'latest', description: 'ECR tag for helm deploy after nodes are up')
        booleanParam(name: 'WAKE_START_JENKINS', defaultValue: true, description: 'Start Jenkins EC2 if stopped')
        booleanParam(name: 'WAKE_RUN_HELM_DEPLOY', defaultValue: true, description: 'Run full helm-platform-deploy.sh')
    }

    environment {
        HELM_NAMESPACE = 'deriv-dev'
        APP_SECRET = 'deriv-platform-app-secrets'
        JENKINS_INSTANCE_NAME_TAG = 'deriv-ai-bot-jenkins-dev'
    }

    stages {
        stage('Checkout') {
            steps { checkout scm }
        }

        stage('Configure') {
            steps {
                script {
                    def common = load 'jenkins/pipelines/_common.groovy'

                    env.AWS_REGION = common.envOrCfg(this, 'AWS_REGION', 'us-west-1')
                    env.ECR_REGISTRY = common.envOrCfg(this, 'ECR_REGISTRY', '')
                    env.EKS_CLUSTER_NAME = common.envOrCfg(this, 'EKS_CLUSTER_NAME', 'deriv-ai-bot-dev')
                    env.VPC_ID = common.envOrCfg(this, 'VPC_ID', '')
                    env.ALB_CONTROLLER_ROLE_ARN = common.envOrCfg(this, 'ALB_CONTROLLER_ROLE_ARN', '')
                    env.EXTERNAL_DNS_ROLE_ARN = common.envOrCfg(this, 'EXTERNAL_DNS_ROLE_ARN', '')
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
                    env.MONITORING_ENABLED = common.envOrCfg(this, 'MONITORING_ENABLED', 'true')
                    env.JENKINS_INSTANCE_ID = common.envOrCfg(this, 'JENKINS_INSTANCE_ID', '')
                    env.EKS_NODE_DESIRED_SIZE = common.envOrCfg(this, 'EKS_NODE_DESIRED_SIZE', '5')
                    env.EKS_NODE_MAX_SIZE = common.envOrCfg(this, 'EKS_NODE_MAX_SIZE', '5')
                    env.WAKE_START_JENKINS = params.WAKE_START_JENKINS ? 'true' : 'false'
                    env.WAKE_RUN_HELM_DEPLOY = params.WAKE_RUN_HELM_DEPLOY ? 'true' : 'false'
                    env.WAKE_IMAGE_TAG = params.IMAGE_TAG.trim()
                    env.HELM_DEBUG = 'false'

                    if (!env.EKS_CLUSTER_NAME?.trim()) {
                        error('Set EKS_CLUSTER_NAME in Jenkins global environment variables')
                    }
                    if (params.WAKE_RUN_HELM_DEPLOY) {
                        common.requireEnv(this, 'ECR_REGISTRY')
                        common.requireEnv(this, 'VPC_ID')
                        common.requireEnv(this, 'ALB_CONTROLLER_ROLE_ARN')
                    }
                }
            }
        }

        stage('Wake') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail
chmod +x jenkins/scripts/lifecycle/wake-platform.sh \
  jenkins/scripts/deploy/helm-platform-deploy.sh \
  jenkins/scripts/deploy/preflight/platform-preflight.sh \
  jenkins/scripts/deploy/infrastructure/*.sh \
  jenkins/scripts/deploy/monitoring/helm-monitoring-deploy.sh
jenkins/scripts/lifecycle/wake-platform.sh
'''
            }
        }
    }

    post {
        success {
            echo 'Platform woken — check app/api URLs and kubectl get pods -n deriv-dev'
        }
    }
}
