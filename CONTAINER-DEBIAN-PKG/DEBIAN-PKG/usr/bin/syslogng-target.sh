#!/bin/bash

# Resolve HOST IP as syslog.host.
serverAddress="$(ip route | grep default | grep -oP '(?<=via\ ).*(?=\ dev)')"

# Avoid error "'/etc/hosts': Device or resource busy".
sed '/syslog.host/d' /etc/hosts > /etc/hosts.tmp
cat /etc/hosts.tmp > /etc/hosts

echo -e "$serverAddress\tsyslog.host" >> /etc/hosts

exit 0
