# Container image repositories for CI/CD.

module "ecr" {
  source = "../../modules/ecr"

  repository_names = var.ecr_repository_names
  tags             = local.common_tags
}
