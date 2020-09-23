#! /bin/bash
sudo yum update -y
sudo yum install -y httpd
sudo service httpd start
echo "<h1>Hackathon Testing site!</h1>" | sudo tee /var/www/html/index.html
sudo systemctl enable amazon-ssm-agent
sudo systemctl start amazon-ssm-agent
sudo aws s3 cp s3://${account_name}.hackathon/hackathon-virus.py /root/hackathon-virus.py