data "aws_iam_policy_document" "jenkins_assume_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "jenkins" {
  name               = "${var.name}-role"
  assume_role_policy = data.aws_iam_policy_document.jenkins_assume_role.json

  tags = var.tags
}

data "aws_iam_policy_document" "jenkins_ecr" {
  statement {
    sid       = "ECRAuth"
    effect    = "Allow"
    actions   = ["ecr:GetAuthorizationToken"]
    resources = ["*"]
  }

  statement {
    sid    = "ECRPushPull"
    effect = "Allow"
    actions = [
      "ecr:BatchCheckLayerAvailability",
      "ecr:GetDownloadUrlForLayer",
      "ecr:BatchGetImage",
      "ecr:PutImage",
      "ecr:InitiateLayerUpload",
      "ecr:UploadLayerPart",
      "ecr:CompleteLayerUpload",
      "ecr:DescribeRepositories",
      "ecr:DescribeImages",
      "ecr:ListImages",
      "ecr:CreateRepository",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "jenkins_ecr" {
  name   = "${var.name}-ecr"
  role   = aws_iam_role.jenkins.id
  policy = data.aws_iam_policy_document.jenkins_ecr.json
}

data "aws_region" "current" {}

data "aws_caller_identity" "current" {}

locals {
  eks_cluster_name = element(split("/", var.eks_cluster_arn), 1)
}

data "aws_iam_policy_document" "jenkins_eks" {
  statement {
    sid    = "EKSRead"
    effect = "Allow"
    actions = [
      "eks:DescribeCluster",
      "eks:ListClusters",
      "eks:DescribeNodegroup",
      "eks:ListNodegroups",
    ]
    resources = [var.eks_cluster_arn]
  }

  statement {
    sid    = "EKSAddonRead"
    effect = "Allow"
    actions = [
      "eks:DescribeAddon",
      "eks:ListAddons",
    ]
    resources = [
      "arn:aws:eks:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:addon/${local.eks_cluster_name}/*",
    ]
  }

  statement {
    sid       = "EKSAccessKubernetesApi"
    effect    = "Allow"
    actions   = ["eks:AccessKubernetesApi"]
    resources = [var.eks_cluster_arn]
  }
}

resource "aws_iam_role_policy" "jenkins_eks" {
  name   = "${var.name}-eks"
  role   = aws_iam_role.jenkins.id
  policy = data.aws_iam_policy_document.jenkins_eks.json
}

data "aws_iam_policy_document" "jenkins_secrets_manager" {
  count = length(var.secrets_manager_secret_arns) > 0 ? 1 : 0

  statement {
    sid    = "SecretsManagerRead"
    effect = "Allow"
    actions = [
      "secretsmanager:GetSecretValue",
      "secretsmanager:DescribeSecret",
    ]
    resources = var.secrets_manager_secret_arns
  }
}

resource "aws_iam_role_policy" "jenkins_secrets_manager" {
  count = length(var.secrets_manager_secret_arns) > 0 ? 1 : 0

  name   = "${var.name}-secrets-manager"
  role   = aws_iam_role.jenkins.id
  policy = data.aws_iam_policy_document.jenkins_secrets_manager[0].json
}

resource "aws_iam_instance_profile" "jenkins" {
  name = "${var.name}-profile"
  role = aws_iam_role.jenkins.name

  tags = var.tags
}
