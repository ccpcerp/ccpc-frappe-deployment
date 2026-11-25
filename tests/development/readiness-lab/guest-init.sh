#!/bin/sh
set -eu
export PATH=/bin:/usr/bin:/usr/sbin
shutdown() { /bin/busybox poweroff -f; }
trap shutdown EXIT
mount -t proc proc /proc
mount -t sysfs sysfs /sys
mount -t devtmpfs devtmpfs /dev
mount -t tmpfs tmpfs /run
mount -t tmpfs tmpfs /tmp
hostname synthetic-db-lab
ip link set lo up
mkdir -p /run/lab
chown 1000:1000 /run/lab
cd /lab
# PID 1 only initializes the synthetic guest. MariaDB and tests run unprivileged.
exec /bin/sh -c '
    set +e
    /usr/bin/setpriv --reuid=1000 --regid=1000 --clear-groups --no-new-privs /usr/bin/python3 -B /lab/test_mariadb_pr41.py
    status=$?
    if [ "$status" -eq 0 ]; then echo "CCPC_SYNTHETIC_LAB_PASS"; fi
    /bin/busybox poweroff -f
'
