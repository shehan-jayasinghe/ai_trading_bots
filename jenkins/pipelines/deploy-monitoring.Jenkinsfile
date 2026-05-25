// Install Grafana + Loki + Promtail on EKS (platform logs → Grafana).
// Jenkins job: Pipeline from SCM, script path: jenkins/pipelines/deploy-monitoring.Jenkinsfile

pipeline {
    agent any

    environment {
        HELM_NAMESPACE = 'deriv-dev'
        MONITORING_NAMESPACE = 'monitoring'
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
                    env.EKS_CLUSTER_NAME = cfg.get('EKS_CLUSTER_NAME', env.EKS_CLUSTER_NAME ?: 'deriv-ai-bot-dev')
                    env.LOKI_S3_BUCKET = cfg.get('LOKI_S3_BUCKET', env.LOKI_S3_BUCKET ?: '')
                    env.LOKI_ROLE_ARN = cfg.get('LOKI_ROLE_ARN', env.LOKI_ROLE_ARN ?: '')

                    echo "Monitoring → ${env.EKS_CLUSTER_NAME} loki_bucket=${env.LOKI_S3_BUCKET ?: '(filesystem fallback)'}"
                }
            }
        }

        stage('Deploy monitoring') {
            steps {
                sh '''#!/bin/bash
set -euo pipefail
aws eks update-kubeconfig --region "${AWS_REGION}" --name "${EKS_CLUSTER_NAME}"
chmod +x jenkins/scripts/eks-monitoring.sh
jenkins/scripts/eks-monitoring.sh
'''
            }
        }
    }

    post {
        success {
            echo 'Grafana/Loki/Promtail installed — port-forward svc/grafana in namespace monitoring'
        }
    }
}
