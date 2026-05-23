data "aws_iam_policy_document" "external_dns" {
  statement {
    sid    = "ChangeRecords"
    effect = "Allow"
    actions = [
      "route53:ChangeResourceRecordSets",
    ]
    resources = [
      "arn:aws:route53:::hostedzone/${var.hosted_zone_id}",
    ]
  }

  statement {
    sid    = "ListRecords"
    effect = "Allow"
    actions = [
      "route53:ListHostedZones",
      "route53:ListResourceRecordSets",
      "route53:ListTagsForResource",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_policy" "external_dns" {
  name        = "${var.cluster_name}-external-dns"
  description = "Route53 permissions for external-dns on ${var.cluster_name}"
  policy      = data.aws_iam_policy_document.external_dns.json
  tags        = var.tags
}

module "irsa" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role-for-service-accounts-eks"
  version = "~> 5.48"

  role_name = "${var.cluster_name}-external-dns"

  oidc_providers = {
    main = {
      provider_arn               = var.oidc_provider_arn
      namespace_service_accounts = ["kube-system:external-dns"]
    }
  }

  role_policy_arns = {
    external_dns = aws_iam_policy.external_dns.arn
  }

  tags = var.tags
}
