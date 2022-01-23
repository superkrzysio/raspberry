#!/bin/bash

# link to folder from RPi, so that I can run scripts from PC directly on RPi
# I did not make it work automatically yet, must be pasted manually
# I saved this mainly as a spell scroll

ssh pi@192.168.0.17 -R 10000:192.168.0.12:22 "mkdir -p /tmp/dev && sshfs -p 10000 -o idmap=user krzysio@127.0.0.1:/home/krzysio/PycharmProjects/raspberry /tmp/dev"

