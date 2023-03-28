#!/bin/bash

# use docker for dev database environment

# only run once when first time setup for mariadb
#docker volume create debian-mariadb-data

# start the container, refer to yaml for rest of info
docker-compose -f docker-compose.mariadb.yml up -d