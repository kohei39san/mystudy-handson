resource "aws_eks_cluster" "cluster" {
  name     = var.cluster_name
  role_arn = aws_iam_role.eks-master.arn
  version  = var.cluster_version

  vpc_config {
    security_group_ids      = ["${aws_security_group.cluster-sg.id}"]
    subnet_ids              = aws_subnet.sn.*.id
    endpoint_private_access = true
    endpoint_public_access  = false
  }
}

data "aws_ssm_parameter" "eks_ami_release_version" {
  name = "/aws/service/eks/optimized-ami/${aws_eks_cluster.cluster.version}/amazon-linux-2/recommended/release_version"
}

resource "aws_eks_node_group" "node_group" {
  cluster_name    = aws_eks_cluster.cluster.name
  node_group_name = var.node_group_name
  version         = var.cluster_version
  release_version = nonsensitive(data.aws_ssm_parameter.eks_ami_release_version.value)
  node_role_arn   = aws_iam_role.eks-node.arn
  instance_types  = var.node_instance_types
  subnet_ids      = aws_subnet.sn[*].id

  scaling_config {
    desired_size = var.node_desired_size
    max_size     = var.node_max_size
    min_size     = var.node_min_size
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks-cluster,
    aws_iam_role_policy_attachment.eks-service,
    aws_iam_role_policy_attachment.eks-worker-node,
    aws_iam_role_policy_attachment.eks-cni,
    aws_iam_role_policy_attachment.ecr-ro,
  ]
  lifecycle {
    ignore_changes = [scaling_config[0].desired_size]
  }
}
