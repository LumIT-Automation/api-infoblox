#!/bin/bash

# Resolve HOST IP as mta.
serverAddress="$(ip route | grep default | grep -oP '(?<=via\ ).*(?=\ dev)')"

# Avoid error "'/etc/hosts': Device or resource busy".
sed -r '/[[:space:]]+mta$/d' /etc/hosts > /etc/hosts.tmp
cat /etc/hosts.tmp > /etc/hosts

echo -e "$serverAddress\tmta" >> /etc/hosts

exit 0
