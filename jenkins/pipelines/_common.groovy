/** Shared helpers for deriv CI pipelines (load via: def common = load 'jenkins/pipelines/_common.groovy') */

/**
 * Read config from Jenkins global environment variables (Manage Jenkins → System → Global properties).
 * See jenkins/global-env.example for the full list.
 */
def envOrCfg(script, String key, String defaultVal = '') {
    def value = script.env."${key}"
    if (value?.trim()) {
        return value.trim()
    }
    return defaultVal
}

def requireEnv(script, String key) {
    def value = envOrCfg(script, key, '')
    if (!value) {
        error("Missing Jenkins global environment variable: ${key} (see jenkins/global-env.example)")
    }
    return value
}

def imageTag(script) {
    def branch = script.env.BRANCH_NAME ?: script.env.GIT_BRANCH ?: 'local'
    branch = branch.replaceFirst(/^origin\//, '')
    def sha = script.sh(script: 'git rev-parse --short HEAD', returnStdout: true).trim()
    def safe = branch.replaceAll(/[^a-zA-Z0-9.-]/, '-').take(40)
    return "${safe}-${sha}"
}

def ecrLogin(script, String region, String registry) {
    script.echo "ECR login: region=${region}, registry=${registry}"

    script.sh("""#!/bin/bash
                set -euo pipefail

                echo "AWS caller identity:"
                aws sts get-caller-identity

                echo "Logging in to ECR (password not shown)..."

                aws ecr get-login-password --region ${region} | \\
                docker login --username AWS --password-stdin ${registry}
                """)

    script.echo "ECR login succeeded for ${registry}"
}

return this
