%postun
#!/bin/bash

# $1 is the number of time that this package is present on the system. If this script is run from an upgrade and not
if [ "$1" -eq "0" ]; then
    if podman volume ls | awk '{print $2}' | grep -q ^api-infoblox$; then
        printf "\n* Clean up api-infoblox volume...\n"
        podman volume rm api-infoblox
        podman volume rm api-infoblox-db
        podman volume rm api-infoblox-cacerts
    fi
fi

exit 0
