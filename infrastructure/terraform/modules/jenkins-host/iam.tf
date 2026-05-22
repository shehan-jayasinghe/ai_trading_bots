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

resource "aws_iam_instance_profile" "jenkins" {
  name = "${var.name}-profile"
  role = aws_iam_role.jenkins.name

  tags = var.tags
}
