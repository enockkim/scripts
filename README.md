# scripts
Scripts for deploying servers

# Install mysql on linux

# Ref
https://www.digitalocean.com/community/tutorials/how-to-install-the-latest-mysql-on-debian-10

sudo apt update
sudo apt install gnupg
cd /tmp
wget https://dev.mysql.com/get/mysql-apt-config_0.8.22-1_all.deb
ls
sudo dpkg -i mysql-apt-config*
sudo apt update
sudo apt install mysql-server
sudo systemctl status mysql
mysql_secure_installation

# Create remote user

# Ref
https://stackoverflow.com/questions/16287559/mysql-adding-user-for-remote-access

CREATE USER 'remote'@'localhost' IDENTIFIED BY 'mypass';
CREATE USER 'remote'@'%' IDENTIFIED BY 'mypass';
Then:

GRANT ALL ON *.* TO 'remote'@'localhost';
GRANT ALL ON *.* TO 'remote'@'%';
FLUSH PRIVILEGES;


# Subdomains Nginx

# Ref 
https://www.youtube.com/watch?v=gsSGDEexBl8