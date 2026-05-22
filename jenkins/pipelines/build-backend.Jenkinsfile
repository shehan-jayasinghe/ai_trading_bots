// Build and push deriv-backend image to ECR.
// Jenkins job: Pipeline from SCM, script path: jenkins/pipelines/build-backend.Jenkinsfile

pipeline {
    agent any

    environment {
        IMAGE_REPO = 'deriv-backend'
        DOCKERFILE = 'deploy/docker/backend.Dockerfile'
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
                /*Yes, exactly! If the git repo’s dev.env file contains the same variable, it will override the Jenkins global
                variable for that run. In other words, the pipeline will prioritize the values from the repo if they exist;
                otherwise, it falls back on the global ones.*/
                    def common = load 'jenkins/pipelines/_common.groovy'
                    def cfg = common.loadDevConfig(this)
                    env.AWS_REGION = cfg.get('AWS_REGION', 'us-west-1')
                    env.ECR_REGISTRY = cfg.get('ECR_REGISTRY', env.ECR_REGISTRY ?: '')
                    if (!env.ECR_REGISTRY?.trim()) {
                        error('Set ECR_REGISTRY and AWS_REGION in Jenkins → System → Global properties → Environment variables')
                    }
                    env.IMAGE_TAG = common.imageTag(this)
                    env.IMAGE_URI = "${env.ECR_REGISTRY}/${env.IMAGE_REPO}:${env.IMAGE_TAG}"
                }
            }
        }

        stage('ECR login') {
            steps {
                script {
                    def common = load 'jenkins/pipelines/_common.groovy'
                    common.ecrLogin(this, env.AWS_REGION, env.ECR_REGISTRY)
                }
            }
        }

        stage('Build and push') {
            steps {
                sh '''
                    set -euo pipefail
                    docker build -f "${DOCKERFILE}" -t "${IMAGE_URI}" .
                    docker push "${IMAGE_URI}"
                '''
            }
        }

        stage('Tag latest on main') {
            when {
                expression { env.BRANCH_NAME == 'main' }
            }
            steps {
                sh '''
                    set -euo pipefail
                    LATEST="${ECR_REGISTRY}/${IMAGE_REPO}:latest"
                    docker tag "${IMAGE_URI}" "${LATEST}"
                    docker push "${LATEST}"
                '''
            }
        }
    }

    post {
        success {
            echo "Pushed ${env.IMAGE_URI}"
            writeFile file: 'build-backend-image.txt', text: "${env.IMAGE_URI}\n"
            archiveArtifacts artifacts: 'build-backend-image.txt', onlyIfSuccessful: true
        }
    }
}
