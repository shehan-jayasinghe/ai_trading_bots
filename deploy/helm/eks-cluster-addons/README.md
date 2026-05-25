# eks-cluster-addons Helm chart

Umbrella chart: **AWS Load Balancer Controller** + **external-dns**.

```bash
helm dependency update deploy/helm/eks-cluster-addons
helm upgrade --install eks-cluster-addons deploy/helm/eks-cluster-addons \
  -n kube-system \
  -f values.yaml -f values-dev.yaml \
  --set aws-load-balancer-controller.vpcId=$VPC_ID \
  --set aws-load-balancer-controller.serviceAccount.annotations.eks\\.amazonaws\\.com/role-arn=$ALB_ARN \
  ...
```

After install, run `jenkins/scripts/deploy/infrastructure/alb-controller-post-install.sh` (webhook TLS sync).

Jenkins: `deriv-deploy-platform` (`DEPLOY_ADDONS=true`) or `jenkins/scripts/deploy/infrastructure/helm-eks-addons-deploy.sh`.
