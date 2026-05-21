variable "domain_name" {
  description = "FQDN for the ACM certificate (e.g. jenkins.testenvlab.shop)"
  type        = string
}

variable "hosted_zone_id" {
  description = "Route53 hosted zone ID for DNS validation"
  type        = string
}

variable "tags" {
  description = "Tags applied to the certificate"
  type        = map(string)
  default     = {}
}
