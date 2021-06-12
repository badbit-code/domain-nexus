#! /bin/bash

cd /home/project/expired-domains/

git checkout deploy

git pull

docker-compose up --build --remove-orphans -d domain-collector

docker-compose up --build --remove-orphans -d alexa-meta-collector

docker-compose up --build --remove-orphans -d whois-meta-collector

docker-compose up --build --remove-orphans -d wiki-meta-collector

# docker-compose up --build --remove-orphans -d public_api