#!/bin/bash

creating_swapfile_service() {
FULL_PATH_OF_SWAP_FILE=$1
    # Write the content into the file
    cat <<EOF > "/etc/systemd/system/swapfile.service"
[Unit]
Description=Enable Swapfile
After=local-fs.target

[Service]
Type=oneshot
ExecStart=$FULL_PATH_OF_SWAP_FILE
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
EOF
}

create_swap_file() {
file_name=$1
      # Write the content into the file
    cat <<EOF > "$file_name"
fallocate -l 2G /swapfile
mkswap /swapfile
chmod 0600 /swapfile
swapon /swapfile
EOF
}

creating_swap () {
	
    # Name of the file to create
    file_name="me_create_swap.sh"
    
     # Check if the file already exists
  if [[ -e "$file_name" ]]; then
    echo "The swap File '$file_name' already exists!"
  else
    create_swap_file $file_name
  fi
	chmod +x $file_name
	./$file_name
	
	FULL_PATH_OF_SWAP_FILE="$(pwd)/$file_name"
	echo "creating SERVICE swap file : $FULL_PATH_OF_SWAP_FILE"
	creating_swapfile_service $FULL_PATH_OF_SWAP_FILE
	
	# load and make enable service
	systemctl daemon-reload
	systemctl enable swapfile.service
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
	firewall-cmd --add-port=8080/tcp --permanent
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

# bash <(curl -Ls https://raw.githubusercontent.com/ultra-deep/shells/refs/heads/main/v2ray_3x-ui.sh)
