#!/bin/bash

. ./globals.rc

today=`date '+%Y-%m-%d'`

for file in ${INDICDIR}*.xml.gz
do
    filename=$(basename $file);
    graph=${filename%.xml.gz};

    if [ "$file" -nt "${RDFDATA}$graph.rdf.gz" ]; then
        zcat "$file" | xsltproc --stringparam wbapi_lang en --stringparam today "$today" \
            ${XSLDIR}indicatorsObservations.xsl - | gzip > "${RDFDATA}$graph.rdf.gz"
        echo "Created ${RDFDATA}$graph.rdf.gz"
#   else
#       echo "${RDFDATA}$graph.rdf.gz File is newer"
    fi
done;
