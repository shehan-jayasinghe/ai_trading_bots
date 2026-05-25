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
        HELM_CHART = 'deploy/helm/deriv-platform'
        HELM_RELEASE = 'deriv-platform'
        HELM_NAMESPACE = 'deriv-dev'
        APP_SECRET = 'deriv-platform-app-secrets'
        PLATFORM_SECRET_ID = 'deriv-ai-bot/dev/platform'
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
                    def cfg = common.loadDevConfig(this)

                    env.AWS_REGION = cfg.get('AWS_REGION', env.AWS_REGION ?: 'us-west-1')
                    env.ECR_REGISTRY = cfg.get('ECR_REGISTRY', env.ECR_REGISTRY ?: '')
                    env.EKS_CLUSTER_NAME = cfg.get('EKS_CLUSTER_NAME', env.EKS_CLUSTER_NAME ?: 'deriv-ai-bot-dev')
                    env.VPC_ID = cfg.get('VPC_ID', env.VPC_ID ?: '')
                    env.ALB_CONTROLLER_ROLE_ARN = cfg.get('ALB_CONTROLLER_ROLE_ARN', env.ALB_CONTROLLER_ROLE_ARN ?: '')
                    env.EXTERNAL_DNS_ROLE_ARN = cfg.get('EXTERNAL_DNS_ROLE_ARN', env.EXTERNAL_DNS_ROLE_ARN ?: '')
                    env.EXTERNAL_DNS_DOMAIN_FILTER = cfg.get('EXTERNAL_DNS_DOMAIN_FILTER', env.EXTERNAL_DNS_DOMAIN_FILTER ?: 'testenvlab.shop')
                    env.EXTERNAL_DNS_TXT_OWNER_ID = cfg.get('EXTERNAL_DNS_TXT_OWNER_ID', env.EXTERNAL_DNS_TXT_OWNER_ID ?: 'deriv-dev')
                    env.APP_ACM_CERTIFICATE_ARN = cfg.get('APP_ACM_CERTIFICATE_ARN', env.APP_ACM_CERTIFICATE_ARN ?: '')
                    env.API_ACM_CERTIFICATE_ARN = cfg.get('API_ACM_CERTIFICATE_ARN', env.API_ACM_CERTIFICATE_ARN ?: '')
                    env.APP_DOMAIN = cfg.get('APP_DOMAIN', env.APP_DOMAIN ?: 'app.testenvlab.shop')
                    env.API_DOMAIN = cfg.get('API_DOMAIN', env.API_DOMAIN ?: 'api.testenvlab.shop')
                    env.PLATFORM_SECRET_ID = cfg.get('PLATFORM_SECRET_ID', env.PLATFORM_SECRET_ID ?: 'deriv-ai-bot/dev/platform')
                    env.LOKI_S3_BUCKET = cfg.get('LOKI_S3_BUCKET', env.LOKI_S3_BUCKET ?: '')
                    env.LOKI_ROLE_ARN = cfg.get('LOKI_ROLE_ARN', env.LOKI_ROLE_ARN ?: '')
                    env.MONITORING_ENABLED = cfg.get('MONITORING_ENABLED', env.MONITORING_ENABLED ?: 'true')
                    env.JENKINS_INSTANCE_ID = cfg.get('JENKINS_INSTANCE_ID', env.JENKINS_INSTANCE_ID ?: '')
                    env.EKS_NODE_DESIRED_SIZE = cfg.get('EKS_NODE_DESIRED_SIZE', env.EKS_NODE_DESIRED_SIZE ?: '1')
                    env.EKS_NODE_MAX_SIZE = cfg.get('EKS_NODE_MAX_SIZE', env.EKS_NODE_MAX_SIZE ?: '2')
                    env.WAKE_START_JENKINS = params.WAKE_START_JENKINS ? 'true' : 'false'
                    env.WAKE_RUN_HELM_DEPLOY = params.WAKE_RUN_HELM_DEPLOY ? 'true' : 'false'
                    env.WAKE_IMAGE_TAG = params.IMAGE_TAG.trim()
                    env.HELM_DEBUG = 'false'

                    if (!env.ECR_REGISTRY?.trim() && params.WAKE_RUN_HELM_DEPLOY) {
                        error('Set ECR_REGISTRY for Helm deploy')
                    }
                    if (!env.EKS_CLUSTER_NAME?.trim()) {
                        error('Set EKS_CLUSTER_NAME')
                    }
                    if (params.WAKE_RUN_HELM_DEPLOY) {
                        if (!env.VPC_ID?.trim() || !env.ALB_CONTROLLER_ROLE_ARN?.trim()) {
                            error('Set VPC_ID and ALB_CONTROLLER_ROLE_ARN for Helm deploy')
                        }
                    }
                }
            }
        }

        stage('Wake') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail
chmod +x jenkins/scripts/wake-platform.sh \
  jenkins/scripts/helm-platform-deploy.sh \
  jenkins/scripts/eks-ingress-controllers.sh \
  jenkins/scripts/eks-monitoring.sh
jenkins/scripts/wake-platform.sh
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
