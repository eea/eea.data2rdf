#!/usr/bin/sh

. ./globals.rc

declare -A excludes

for exclude in NY.AGR.SUBS.GD.ZS \
		SE.ENR.PRSC.FM.ZS.GL SE.PRM.CMPT.ZS.GL \
		SP.POP.2DAY.TO SP.POP.DDAY.TO \
		TM.MRC.NOTX.DV.ZS TM.MRC.NOTX.LD.ZS \
		TM.TAX.AGRI.CD.DV TM.TAX.AGRI.CD.LD \
		TM.TAX.CLTH.CD.DV TM.TAX.CLTH.CD.LD \
		TM.TAX.TXTL.CD.DV TM.TAX.TXTL.CD.LD
do
    excludes[$exclude]="1"
done

WBAPI="http://api.worldbank.org/en/countries/all/indicators/"

# Download
xsltproc ${XSLDIR}txtIndicators.xsl ${VOCDIR}indicators.xml | while read indicator
do
    if [ "${excludes[$indicator]}" == "1" ]; then
        echo Skipping $indicator
        continue
    fi
    if [ ! -s "${INDICDIR}${indicator}.xml.gz" ]; then
        wget -nv -O "${INDICDIR}${indicator}.xml" "${WBAPI}${indicator}?format=xml&per_page=23000"
        [ -s "${INDICDIR}${indicator}.xml" ] && gzip "${INDICDIR}${indicator}.xml"
        sleep 2
    #else
    #    echo "$indicator already downloaded"
    fi
done
