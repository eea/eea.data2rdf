#!/bin/bash

. ./globals.rc

# Compute the number of records
echo "Scanning files to get totals. This will take a while"
echo python compute.entities.py "$INDICDIR" "${VOCDIR}entities.xml"

python compute.entities.py "$INDICDIR" "${VOCDIR}entities.xml"

nowtime=`date -Iseconds`

file=${VOCDIR}indicators.xml
if [ -s $file ]; then
        filename=$(basename $file);
        extension=${filename##*.};
        graph=${filename%.*};

    xsltproc -o "${WEBSITE}void.rdf" --stringparam wbapi_lang en \
        --stringparam entitiesFile ../${VOCDIR}entities.xml \
        --stringparam currentDateTime "$nowtime" xsl/indicatorsVoid.xsl "$file"
    echo "Created ${WEBSITE}void.rdf"
else
    echo "File was empty"
fi
