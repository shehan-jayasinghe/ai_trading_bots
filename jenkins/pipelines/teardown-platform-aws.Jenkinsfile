// Remove Kubernetes-created ALBs, target groups, and stray EIPs before terraform destroy.
// Jenkins job: Pipeline from SCM, script path: jenkins/pipelines/teardown-platform-aws.Jenkinsfile
//
// Infra config: Jenkins global env vars (see jenkins/global-env.example)

pipeline {
    agent any

    environment {
        HELM_RELEASES = 'deriv-ingress deriv-apps deriv-kafka deriv-postgres deriv-platform'
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

                    env.AWS_REGION = common.envOrCfg(this, 'AWS_REGION', 'us-west-1')
                    env.EKS_CLUSTER_NAME = common.envOrCfg(this, 'EKS_CLUSTER_NAME', 'deriv-ai-bot-dev')
                    env.VPC_ID = common.envOrCfg(this, 'VPC_ID', '')

                    if (!env.EKS_CLUSTER_NAME?.trim()) {
                        error('Set EKS_CLUSTER_NAME in Jenkins global environment variables')
                    }
                    if (!env.VPC_ID?.trim()) {
                        error('Set VPC_ID in Jenkins global environment variables')
                    }

                    echo "Teardown K8s AWS orphans: cluster=${env.EKS_CLUSTER_NAME} vpc=${env.VPC_ID}"
                }
            }
        }

        stage('Teardown') {
            steps {
                sh 'chmod +x jenkins/scripts/lifecycle/teardown-k8s-aws-orphans.sh'
                sh 'jenkins/scripts/lifecycle/teardown-k8s-aws-orphans.sh'
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
