// Park dev stack: scale pods/nodes to 0, remove k8s ALB, stop Jenkins EC2 (no terraform destroy).
// Jenkins job: jenkins/pipelines/park-platform.Jenkinsfile

pipeline {
    agent any

    parameters {
        booleanParam(name: 'PARK_STOP_JENKINS', defaultValue: true, description: 'Stop Jenkins EC2 instance')
        booleanParam(name: 'PARK_DELETE_ALB', defaultValue: true, description: 'Delete Ingress and k8s ALB')
        booleanParam(name: 'PARK_SCALE_NODES_ZERO', defaultValue: true, description: 'Scale EKS node group to 0')
    }

    environment {
        HELM_INGRESS_RELEASE = 'deriv-ingress'
        HELM_NAMESPACE = 'deriv-dev'
        MONITORING_NAMESPACE = 'monitoring'
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
                    env.EKS_CLUSTER_NAME = cfg.get('EKS_CLUSTER_NAME', env.EKS_CLUSTER_NAME ?: 'deriv-ai-bot-dev')
                    env.VPC_ID = cfg.get('VPC_ID', env.VPC_ID ?: '')
                    env.JENKINS_INSTANCE_ID = cfg.get('JENKINS_INSTANCE_ID', env.JENKINS_INSTANCE_ID ?: '')
                    env.PARK_STOP_JENKINS = params.PARK_STOP_JENKINS ? 'true' : 'false'
                    env.PARK_DELETE_ALB = params.PARK_DELETE_ALB ? 'true' : 'false'
                    env.PARK_SCALE_NODES_ZERO = params.PARK_SCALE_NODES_ZERO ? 'true' : 'false'

                    if (!env.EKS_CLUSTER_NAME?.trim()) {
                        error('Set EKS_CLUSTER_NAME in Jenkins global env or jenkins/config/dev.env')
                    }
                    if (params.PARK_DELETE_ALB && !env.VPC_ID?.trim()) {
                        error('Set VPC_ID when PARK_DELETE_ALB is enabled')
                    }
                }
            }
        }

        stage('Park') {
            steps {
                sh 'chmod +x jenkins/scripts/lifecycle/park-platform.sh'
                sh 'jenkins/scripts/lifecycle/park-platform.sh'
            }
        }
    }

    post {
        success {
            echo 'Platform parked — EKS API/NAT may still bill. Wake with deriv-wake-platform.'
        }
    }
}
