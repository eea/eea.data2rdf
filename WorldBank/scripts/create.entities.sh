#!/bin/bash

. ./globals.rc

# Compute the number of records
echo "Scanning files to get totals. This will take a while"
echo python compute.entities.py "$INDICDIR" "${VOCDIR}entities.xml"

python compute.entities.py "$INDICDIR" "${VOCDIR}entities.xml"
