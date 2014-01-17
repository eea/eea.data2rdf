#!/usr/bin/sh

. ./globals.rc

mkdir -p "${VOCDIR}"
mkdir -p "${RDFCLAS}"

# Currencies
if [ -f "${VOCDIR}dl_iso_table_a1.xml" ]; then
    echo "${VOCDIR}dl_iso_table_a1.xml already downloaded"
else
    wget -nv -O "${VOCDIR}dl_iso_table_a1.xml" http://www.currency-iso.org/content/dam/isocy/downloads/dl_iso_table_a1.xml
fi

saxon "-o:${RDFCLAS}currencies.rdf" "${VOCDIR}dl_iso_table_a1.xml" "xsl/currencies.xsl" \
        wbapi_lang="en" pathToCountries="../${VOCDIR}countries.xml" pathToCurrencies="../${RDFCLAS}currencies.rdf"

# Also creates the RDF
for voc in 'countries' 'sources' 'topics' 'regions' 'incomeLevels' 'lendingTypes' 'indicators'
do
    if [ -f "${VOCDIR}${voc}.xml" ]; then
        echo "${VOCDIR}${voc}.xml already downloaded"
    else
        wget -nv -O "${VOCDIR}${voc}.xml" "http://api.worldbank.org/en/${voc}?format=xml&per_page=20000"

    fi
    saxon "-o:${RDFCLAS}${voc}.rdf" "${VOCDIR}${voc}.xml" "xsl/${voc}.xsl" \
        wbapi_lang="en" pathToCountries="../${VOCDIR}countries.xml" pathToCurrencies="../${RDFCLAS}currencies.rdf"
done

