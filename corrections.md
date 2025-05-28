Based on the tflint warnings and code analysis, the following corrections have been made:

1. Key Names:
- Fixed typo in "manaaged_node_linux_key_pair" -> "managed_node_linux_key_pair"
- Fixed typo in "manaaged_node_windows_key_pair" -> "managed_node_windows_key_pair"
- Renamed "key_server" -> "eice_tunnel_key"
- Added default value "simple_ec2_key" for empty key_pair

2. IAM Profile Names:
- Fixed "ami_ec2_managed_node_instance_profile" -> "managed_node_instance_profile"
- Added default value "eice_tunnel_instance_profile" for empty iam_instance_profile
- Added default value "simple_ec2_instance_profile" for empty iam_instance_profile

3. AMI ID:
- Replaced hardcoded AMI ID with SSM parameter store path
- Added data source to lookup AMI ID from SSM parameter store
- Old: ami-0529e165c6694e490
- New: /aws/service/ami-windows-latest/Windows_Server-2016-Japanese-Full-Base

4. AWS Provider Tags:
- Added common tags to all AWS providers using default_tags:
  - Environment = "Development"
  - Terraform = "true"

These changes have been implemented across multiple files to ensure consistency and fix the tflint warnings. The use of SSM parameter store for AMI IDs provides a more maintainable solution for managing AMI references.