#!/bin/bash
echo HELLO_FROM_CPANEL $(hostname) $(date -u +%FT%T) uid=$(id -un)
ls /tmp | head -5
