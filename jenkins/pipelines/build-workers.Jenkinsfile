// Build and push deriv-workers image to ECR.
// Jenkins job: Pipeline from SCM, script path: jenkins/pipelines/build-workers.Jenkinsfile

pipeline {
    agent any

    environment {
        IMAGE_REPO = 'deriv-workers'
        DOCKERFILE = 'deploy/docker/workers.Dockerfile'
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
                sh '''#!/bin/bash
set -euo pipefail
docker build -f "${DOCKERFILE}" -t "${IMAGE_URI}" .
docker push "${IMAGE_URI}"
'''
            }
        }

        stage('Tag latest on master') {
            when {
                expression { env.BRANCH_NAME == 'master' || env.BRANCH_NAME == 'main' }
            }
            steps {
                sh '''#!/bin/bash
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
            writeFile file: 'build-workers-image.txt', text: "${env.IMAGE_URI}\n"
            archiveArtifacts artifacts: 'build-workers-image.txt', onlyIfSuccessful: true
        }
    }
}
