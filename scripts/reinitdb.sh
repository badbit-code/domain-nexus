#! /usr/bin/env /bin/bash

# Connect to sql server with the express purpose of tearing down and rebuilding db 
# with the latest configuration init.sql settings

echo "
    
Warning: 

    This script will destroy and recreate the following objects:
        - DATABASE nexus
        - USER nexus_collector
        - USER nexus_reader
        
The following Environment variables need to be set for this script to function as intended:
    - POSTGRES_HOST
    - POSTGRES_USER
    - POSTGRES_PORT
"

if [[ $POSTGRES_HOST == "" ]]
then 
    echo "POSTGRES_HOST NOT DEFINED"
    exit
fi

echo "Modifying DB at host: $POSTGRES_HOST"

echo "Are you sure you want to continue (y/n): "

read CONTINUE

if [[ $CONTINUE != "y" ]]
then 
    exit
fi

DEFAULT_DB=defaultdb


echo "Enter password for nexus_reader user: "
read -s DEFAULT_NEXUS_R_PW
echo "Enter password for nexus_collector user: "
read -s DEFAULT_NEXUS_W_PW

base_connection_stub="psql -U doadmin -h $POSTGRES_HOST -p $POSTGRES_PORT -d $DEFAULT_DB --set=sslmode=require -a" 
nexus_connection_stub="psql -U doadmin -h $POSTGRES_HOST -p $POSTGRES_PORT -d nexus --set=sslmode=require -a" 

# Destroy nexus db and users
$base_connection_stub -c "DROP DATABASE nexus"
$base_connection_stub -c "DROPUSER nexus_collector"
$base_connection_stub -c "DROPUSER nexus_reader"

# Create nexus db
$base_connection_stub -c "CREATE DATABASE nexus"

# Create nexus users
$base_connection_stub -c "CREATE user nexus_reader ENCRYPTED PASSWORD '$DEFAULT_NEXUS_R_PW' NOCREATEUSER NOCREATEDB VALID UNTIL 'infinity'" 
$base_connection_stub -c "CREATE user nexus_collector ENCRYPTED PASSWORD '$DEFAULT_NEXUS_W_PW' NOCREATEUSER NOCREATEDB VALID UNTIL 'infinity'"

# Grant priviliges 
$base_connection_stub -c "GRANT CONNECT ON DATABASE nexus to nexus_collector"
$base_connection_stub -c "GRANT ALL PRIVILEGES ON DATABASE nexus to nexus_collector"

$base_connection_stub -c "GRANT CONNECT ON DATABASE nexus to nexus_reader"
$base_connection_stub -c "GRANT SELECT ON ALL TABLES IN SCHEMA public TO nexus_reader"

# Initialize the nexus DB
$nexus_connection_stub -f ./src/container/postgresql/init.sql
