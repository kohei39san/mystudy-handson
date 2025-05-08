# Redmine on EC2

This Terraform configuration deploys a Redmine instance on AWS EC2 with access restricted to a specific IP address.

## Prerequisites

- Terraform installed (version ~> 1.9.6)
- AWS CLI configured with appropriate credentials
- SSH key pair (optional, can be created during deployment)

## Deployment Instructions

1. Initialize the Terraform configuration:

```bash
terraform init
```

2. Plan the deployment, specifying your allowed IP address:

```bash
terraform plan -var="allowed_ip=YOUR_IP_ADDRESS/32"
```

Replace `YOUR_IP_ADDRESS` with your public IP address. The `/32` suffix indicates a single IP address.

3. Apply the configuration:

```bash
terraform apply -var="allowed_ip=YOUR_IP_ADDRESS/32"
```

If you want to use your own SSH key pair, you can specify it like this:

```bash
terraform apply -var="allowed_ip=YOUR_IP_ADDRESS/32" -var="create_key_pair=true" -var="public_key=YOUR_PUBLIC_KEY"
```

Replace `YOUR_PUBLIC_KEY` with the content of your public key file.

## Accessing Redmine

After the deployment is complete, Terraform will output the following information:

- Public IP address of the Redmine instance
- Public DNS name of the Redmine instance
- HTTP URL to access Redmine
- SSH command to connect to the instance

### Web Access

Open a web browser and navigate to the HTTP URL provided in the output:

```
http://ec2-xx-xx-xx-xx.compute-1.amazonaws.com
```

### Default Credentials

The default login credentials for Redmine are:

- Username: `user`
- Password: Check the Bitnami application password using the instructions below

### Getting the Bitnami Application Password

Connect to the instance via SSH:

```bash
ssh bitnami@ec2-xx-xx-xx-xx.compute-1.amazonaws.com
```

Once connected, run the following command to get the Bitnami application password:

```bash
cat /home/bitnami/bitnami_credentials
```

This will display the default username and password for the Redmine application.

## AMI Selection

This configuration attempts to use the Bitnami Redmine AMI by default. If the Bitnami AMI is not available, it will fall back to Amazon Linux 2 and attempt to install Redmine manually. The fallback installation is basic and may require additional configuration.

To check which AMI was used after deployment:

```bash
terraform output redmine_ami_type
```

## Security Considerations

- Only the specified IP address can access the Redmine instance
- Consider setting up HTTPS for secure access
- Change the default passwords immediately after first login
- Consider implementing regular backups of your Redmine data
- The root EBS volume is encrypted for additional security

## Customization Options

You can customize the deployment by modifying the following variables:

- `instance_type`: EC2 instance type (default: t2.micro)
- `aws_region`: AWS region to deploy resources (default: ap-northeast-1)
- `vpc_cidr`: CIDR block for the VPC (default: 10.0.0.0/16)
- `subnet_cidr`: CIDR block for the public subnet (default: 10.0.1.0/24)

## Troubleshooting

### Cannot Connect to the Instance

- Verify that your current IP address matches the one specified in the `allowed_ip` variable
- Check that the security group allows traffic on ports 22, 80, and 443
- Ensure that the instance is in the "running" state

### Redmine Not Accessible

- If using the Bitnami AMI, wait a few minutes after deployment for the services to start
- If using the fallback Amazon Linux installation, additional manual configuration may be required
- Check the instance system log for any errors:
  ```bash
  aws ec2 get-console-output --instance-id <instance-id>
  ```

## Cleanup

To destroy the resources when they are no longer needed:

```bash
terraform destroy -var="allowed_ip=YOUR_IP_ADDRESS/32"
```