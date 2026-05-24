// Remove Kubernetes-created ALBs, target groups, and stray EIPs before terraform destroy.
// Jenkins job: Pipeline from SCM, script path: jenkins/pipelines/teardown-platform-aws.Jenkinsfile
//
// Infra config: same globals as deriv-deploy-platform (VPC_ID, EKS_CLUSTER_NAME, AWS_REGION).

pipeline {
    agent any

    environment {
        HELM_RELEASE = 'deriv-platform'
        HELM_NAMESPACE = 'deriv-dev'
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
                    env.VPC_ID = cfg.get('VPC_ID', env.VPC_ID ?: '')

                    if (!env.VPC_ID?.trim()) {
                        error('Set VPC_ID in Jenkins global env or jenkins/config/dev.env')
                    }
                    if (!env.EKS_CLUSTER_NAME?.trim()) {
                        error('Set EKS_CLUSTER_NAME in Jenkins global env or jenkins/config/dev.env')
                    }

                    echo "Teardown K8s AWS orphans: cluster=${env.EKS_CLUSTER_NAME} vpc=${env.VPC_ID}"
                }
            }
        }

        stage('Teardown') {
            steps {
                sh 'chmod +x jenkins/scripts/teardown-k8s-aws-orphans.sh'
                sh 'jenkins/scripts/teardown-k8s-aws-orphans.sh'
            }
        }
    }

    post {
        success {
            echo 'K8s ALB / EIP cleanup finished — run terraform destroy on dev when ready'
        }
        failure {
            echo 'Teardown failed — check console; you may need to delete ALBs manually in AWS console'
        }
    }
}
