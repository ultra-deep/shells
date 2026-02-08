#!/bin/bash

creating_swap () {
	
    # Name of the file to create
    file_name="me_create_swap.sh"
    
     # Check if the file already exists
  if [[ -e "$file_name" ]]; then
    echo "The swap File '$file_name' already exists!"
    return 1
  fi
  
    # Write the content into the file
    cat <<EOF > "$file_name"
fallocate -l 2G /swapfile
mkswap /swapfile
chmod 0600 /swapfile
swapon /swapfile
EOF

	chmod +x $file_name
	./$file_name
}

init_firewall() {
	yum install -y epel-release
	yum install -y bash-completion
	yum install -y firewalld
	systemctl start firewalld
	systemctl enable firewalld
	echo "setup firewall..."
	firewall-cmd --add-port=443/tcp --permanent
	firewall-cmd --add-port=80/tcp --permanent
	firewall-cmd --add-port=8888/tcp --permanent
	firewall-cmd --add-port=47000/tcp --permanent
	firewall-cmd --add-port=47001/tcp --permanent
	firewall-cmd --add-port=47002/tcp --permanent
	firewall-cmd --add-port=47003/tcp --permanent
	firewall-cmd --add-port=47004/tcp --permanent
	firewall-cmd --add-port=47005/tcp --permanent
	firewall-cmd --add-port=47006/tcp --permanent
	firewall-cmd --reload⁠
}


creating_swap
init_firewall


bash <(curl -Ls https://raw.githubusercontent.com/mhsanaei/3x-ui/master/install.sh)
