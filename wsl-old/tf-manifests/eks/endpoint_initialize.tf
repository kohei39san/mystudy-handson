resource "null_resource" "init_kubectl" {
  triggers = {
    instance_id = aws_instance.kubectl_instance.id
    cluster_id  = aws_eks_cluster.cluster.id
  }

  provisioner "local-exec" {
    command = "../../scripts/connect-eks-for-remote-ec2.sh"
    environment = {
      PRIVATE_KEY             = var.instance_private_key
      PUBLIC_KEY              = var.instance_public_key
      SSH_USER                = "ec2-user"
      SSO_ROLE_NAME           = var.instance_sso_role_name
      KUBECTL_ROLE_ARN        = aws_iam_role.kubectl_role.arn
      KUBECTL_INSTALL_URL     = var.instance_kubectl_install_url
      KUBECTL_SHA_INSTALL_URL = var.instance_kubectl_sha_install_url
      INSTANCE_IP             = aws_instance.kubectl_instance.public_ip
      INSTANCE_ID             = self.triggers.instance_id
      CLUSTER                 = aws_eks_cluster.cluster.name
    }
  }

  required_providers {
    null = {
      source  = "hashicorp/null"
      version = "~> 3.2.1"
    }
  }
}
