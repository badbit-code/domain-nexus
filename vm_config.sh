#! /bin/bash

apt update
apt install -y git
apt install -y bash
apt install -y zsh
apt install -y docker docker-compose
apt install -y python3.9 python3.9-dev python3.9-venv


# Setup User Accounts

# Add docker to sudo
groupadd docker

users=( anthony derek ben )
PW=change-me-54613169-37972 
groupadd badbit

for user in "${users[@]}"; do

mkdir /home/$user
mkdir /home/$user/.ssh
touch /home/$user/.profile
touch /home/$user/.bashrc

useradd $user
usermod -aG sudo,badbit,docker $user
echo -e "$PW\n$PW\n" | passwd $user
passwd -e $user

usermod --shell /bin/bash $user

chown $user:$user -R /home/$user

done;

# Setup Project Directory

mkdir /home/project
chgrp badbit -R /home/project
chomod 775 -R /home/project



