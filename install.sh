#!/bin/bash
if [[ $EUID -ne 0 ]]; then
    echo "This script must be run as root." 1>&2
else
    cp -r ImgurContract /usr/share/
    mv /usr/share/ImgurContract/uploadtoimgur.contract /usr/share/contractor/
    chmod 755 /usr/share/ImgurContract/upload.py
    chmod 644 /usr/share/contractor/uploadtoimgur.contract
    exit 1
fi

