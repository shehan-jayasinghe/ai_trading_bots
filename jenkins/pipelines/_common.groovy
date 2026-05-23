/** Shared helpers for deriv CI pipelines (load via: def common = load 'jenkins/pipelines/_common.groovy') */

def parseEnvFile(script, String path, Map cfg) {
    if (!script.fileExists(path)) {
        return
    }
    script.readFile(path).split('\n').each { line ->
        line = line.trim()
        if (!line || line.startsWith('#')) {
            return
        }
        def idx = line.indexOf('=')
        if (idx > 0) {
            def key = line.substring(0, idx).trim()
            if (!cfg.containsKey(key) || cfg[key] == '') {
                cfg[key] = line.substring(idx + 1).trim()
            }
        }
    }
}

def loadDevConfig(script) {
    def cfg = [:]
    parseEnvFile(script, "${script.env.WORKSPACE}/jenkins/config/dev.env", cfg)
    return cfg
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
    script.sh """
        set -euo pipefail
        echo "AWS caller identity:"
        aws sts get-caller-identity
        echo "Logging in to ECR (password not shown)..."
        aws ecr get-login-password --region ${region} | \\
          docker login --username AWS --password-stdin ${registry}
    """
    script.echo "ECR login succeeded for ${registry}"
}

return this
