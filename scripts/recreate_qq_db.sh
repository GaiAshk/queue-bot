#!/bin/bash

MYSQL_USER=root
MYSQL_PASSWORD=password
HOST=127.0.0.1

while ! mysqladmin ping --host="$HOST" --password="$MYSQL_PASSWORD" --user="$MYSQL_USER" --silent; do
    sleep 1
done

mysql --host="$HOST" --password="$MYSQL_PASSWORD" --user="$MYSQL_USER" -e 'DROP SCHEMA IF EXISTS qq;'
mysql --host="$HOST" --password="$MYSQL_PASSWORD" --user="$MYSQL_USER" -e 'CREATE SCHEMA IF NOT EXISTS qq;'
