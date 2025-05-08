# Find the latest Bitnami Redmine AMI
data "aws_ami" "redmine" {
  most_recent = true
  owners      = ["979382823631"] # Bitnami

  filter {
    name   = "name"
    values = ["bitnami-redmine-*-linux-debian-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }

  filter {
    name   = "root-device-type"
    values = ["ebs"]
  }

  filter {
    name   = "architecture"
    values = ["x86_64"]
  }
}

# Fallback to Amazon Linux 2 if Bitnami AMI is not available
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

locals {
  # Use Bitnami AMI if available, otherwise use Amazon Linux
  ami_id = length(data.aws_ami.redmine.id) > 0 ? data.aws_ami.redmine.id : data.aws_ami.amazon_linux.id
  
  # Determine if we're using the Bitnami AMI
  is_bitnami = length(data.aws_ami.redmine.id) > 0
}

# Create a key pair if specified
resource "aws_key_pair" "redmine_key" {
  count      = var.create_key_pair ? 1 : 0
  key_name   = var.key_name
  public_key = var.public_key
}

# Create the EC2 instance
resource "aws_instance" "redmine" {
  ami                    = local.ami_id
  instance_type          = var.instance_type
  subnet_id              = aws_subnet.redmine_subnet.id
  vpc_security_group_ids = [aws_security_group.redmine_sg.id]
  key_name               = var.create_key_pair ? aws_key_pair.redmine_key[0].key_name : var.key_name

  root_block_device {
    volume_size = 20
    volume_type = "gp3"
    encrypted   = true
  }

  user_data = local.is_bitnami ? <<-EOF
    #!/bin/bash
    # Update system packages
    apt-get update -y
    apt-get upgrade -y
    
    # Backup Bitnami credentials for easy access
    cp /home/bitnami/bitnami_credentials /home/bitnami/bitnami_credentials.backup
    
    # Set hostname
    hostnamectl set-hostname redmine-server
    
    # Additional setup can be added here if needed
  EOF : <<-EOF
    #!/bin/bash
    # Update system packages
    yum update -y
    
    # Install required packages
    yum install -y httpd mariadb-server mariadb ruby ruby-devel gcc make git
    
    # Start and enable services
    systemctl start httpd mariadb
    systemctl enable httpd mariadb
    
    # Set hostname
    hostnamectl set-hostname redmine-server
    
    # Install Redmine manually since we're not using Bitnami AMI
    cd /opt
    git clone https://github.com/redmine/redmine.git --branch 5.0-stable
    cd redmine
    
    # Install bundler
    gem install bundler
    
    # Install dependencies
    bundle install --without development test
    
    # Configure database
    cp config/database.yml.example config/database.yml
    # Additional manual setup would be required here
    
    echo "Manual Redmine installation completed. Further configuration required."
  EOF

  tags = {
    Name = "Redmine-Server"
    Application = "Redmine"
    ManagedBy = "Terraform"
  }
}