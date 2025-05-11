#!/bin/bash

# Update system packages
yum update -y

# Install necessary packages
yum install -y httpd httpd-devel gcc gcc-c++ make curl wget

# Install Ruby dependencies
yum install -y ruby ruby-devel
yum install -y mariadb-server mariadb-devel
yum install -y ImageMagick ImageMagick-devel

# Start and enable MariaDB
systemctl start mariadb
systemctl enable mariadb

# Secure MariaDB installation with default password for redmine
mysql -e "CREATE DATABASE redmine CHARACTER SET utf8mb4;"
mysql -e "CREATE USER 'redmine'@'localhost' IDENTIFIED BY 'redmine';"
mysql -e "GRANT ALL PRIVILEGES ON redmine.* TO 'redmine'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

# Install Redmine
cd /opt
wget https://www.redmine.org/releases/redmine-5.0.5.tar.gz
tar xzf redmine-5.0.5.tar.gz
mv redmine-5.0.5 redmine
cd redmine

# Configure database connection
cat > config/database.yml << EOF
production:
  adapter: mysql2
  database: redmine
  host: localhost
  username: redmine
  password: redmine
  encoding: utf8mb4
EOF

# Install bundler and dependencies
gem install bundler
bundle install --without development test

# Generate secret token
bundle exec rake generate_secret_token

# Create database structure
RAILS_ENV=production bundle exec rake db:migrate

# Load default data
RAILS_ENV=production REDMINE_LANG=en bundle exec rake redmine:load_default_data

# Set permissions
mkdir -p tmp tmp/pdf public/plugin_assets
chown -R apache:apache files log tmp public/plugin_assets
chmod -R 755 files log tmp public/plugin_assets

# Configure Apache
cat > /etc/httpd/conf.d/redmine.conf << EOF
<VirtualHost *:80>
  ServerName localhost
  DocumentRoot /opt/redmine/public

  <Directory "/opt/redmine/public">
    Allow from all
    Require all granted
    Options -MultiViews
  </Directory>

  ErrorLog /var/log/httpd/redmine_error.log
  CustomLog /var/log/httpd/redmine_access.log combined
</VirtualHost>
EOF

# Start and enable Apache
systemctl start httpd
systemctl enable httpd

# Configure firewall
firewall-cmd --permanent --add-service=http
firewall-cmd --reload

echo "Redmine installation completed!"