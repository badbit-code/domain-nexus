#! /bin/bash

git checkout deploy

git pull

docker-compose --env-file ./.env build