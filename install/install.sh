#!/bin/sh

set -e

KIRIN_CONFIGURATION=/etc/kirin
KIRIN_CONFIGURATION_FILE=/etc/kirin/kirin.conf
KIRIN_GROUP="kirin"
KIRIN_DATA_DIR=/var/lib/kirin
KIRIN_LOG_DIR=/var/log/kirin
KIRIN_USER="kirin"
CURRENT_LOCATION=`pwd -LP`

parentdir="$(dirname "$CURRENT_LOCATION")"
main="$parentdir/main.py"

cp -f ./kirin.service /lib/systemd/system/kirin.service
sed -i "s|main.py|$main|g" "/lib/systemd/system/kirin.service"
systemctl enable kirin.service >/dev/null || true
chmod +x ../main.py

mkdir -p $KIRIN_CONFIGURATION
cp -f ./kirin.conf $KIRIN_CONFIGURATION_FILE

if ! getent passwd | grep -q "^kirin:"; then
    adduser --system --home $KIRIN_DATA_DIR --quiet --group $KIRIN_USER
fi

# Configuration file
chown $KIRIN_USER:$KIRIN_GROUP $KIRIN_CONFIGURATION_FILE
chmod 0640 $KIRIN_CONFIGURATION_FILE

# Log
mkdir -p $KIRIN_LOG_DIR
chown $KIRIN_USER:$ODOO_GROUP $KIRIN_LOG_DIR
chmod 0750 $KIRIN_LOG_DIR

# Data dir
chown $KIRIN_USER:$KIRIN_GROUP $KIRIN_DATA_DIR

exit 0