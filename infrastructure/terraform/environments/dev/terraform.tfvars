aws_region            = "us-west-1"
project_name          = "deriv-ai-bot"
environment           = "dev"
vpc_name              = "deriv-ai-dev"
vpc_cidr              = "10.0.0.0/16"
availability_zones    = ["us-west-1a", "us-west-1c"]
private_subnet_cidrs  = ["10.0.3.0/24", "10.0.4.0/24"]
public_subnet_cidrs   = ["10.0.1.0/24", "10.0.2.0/24"]
single_nat_gateway    = true
jenkins_instance_type = "t3.medium"
ami_id                = "ami-00271c85bf8a52b84"
root_domain           = "testenvlab.shop"
jenkins_domain        = "jenkins.testenvlab.shop"
alb_name              = "deriv-jenkins-dev-alb"
enable_eks          = false
eks_cluster_version = "1.31"
# REQUIRED before terraform apply:
# public_key = "ssh-rsa AAAA... user@host"   # paste from your .pub file

public_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDE71BUwy1phOlc7uel+77ydxu1cIgliF5eec6FYu9Pq3mk+FGe7FZ3et25zXuKqHoJet4q+oLy0ur58vByFzjLhIhk9QONZf39jG5VtbgCCP6vCgueKUm0pRLXOdHdWxXjvdN6gh2bjB+ArTkM9+SaDwJwspi3us2WLSiJYsKBzHl5gHnAL4KkcD0uMMM0TXGGSo8zCkrrMg6rbfUwvyOG1/uG3T+Wn/1eAz49DWdWtia+3hOnHUXLMCTbKlIpdLG/sqpTK9512B0m1e4+04PZoQoupjOf7MDSo2A3GuJsOoevOUp/i7PXAvrNX+tMXWcCB87vfH+n1Er4fi1SYGKUAieq11Gbcn7+D8sMfBa1h9bbRNPg1tb2esVNuHuEbWfhWt5dpM0o+C095yHCIDOkQkajTlDCke9ovoG1RD/tbYFvcwLSkoBuKA2PrJ+PNIXmwhZCYlyEbpnvTFnkxzXSH06DinZnqiA3CwSIFU5ZhPvftIt/cmhOQcV2fyz2wUi6JQXVhggbr4sdEyZIc7DZ6ydozTq6ziC3h/WNp9m2koadZCGDhuYHRnXXZimpQZ0HesQVK0nJPVyxZK77WHZnLEdL7X46SkCuiNFzRCYxxXuuFpjcvBG6xvuFiva+J12BhM9AmQtn3d8Y/ilW1A+NkoggrWRTIH00oDE8fL4sgQ== jenkins-dev"