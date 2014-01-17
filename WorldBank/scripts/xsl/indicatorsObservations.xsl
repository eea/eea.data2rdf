<!DOCTYPE xsl:stylesheet [
    <!ENTITY wbns "http://rdfdata.eionet.europa.eu/worldbank/">
]>
<!--
    Author: Sarven Capadisli <info@csarven.ca>
    Author URL: http://csarven.ca/#i
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:wgs="http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:qb="http://purl.org/linked-data/cube#"
    xmlns:sdmx-attribute="http://purl.org/linked-data/sdmx/2009/attribute#"
    xmlns:sdmx-dimension="http://purl.org/linked-data/sdmx/2009/dimension#"
    xmlns:sdmx-measure="http://purl.org/linked-data/sdmx/2009/measure#"
    xmlns:wb="http://www.worldbank.org"
    xmlns:wbld="&wbns;"
    xmlns:property="&wbns;property/"
    xmlns:country="&wbns;classification/country/"
    xmlns:indicator="&wbns;classification/indicator/"
    xmlns:dataset="&wbns;dataset/"
    xmlns:void="http://rdfs.org/ns/void#"
    xmlns:cr="http://cr.eionet.europa.eu/ontologies/contreg.rdf#"
    >

    <xsl:output encoding="utf-8" indent="yes" method="xml" omit-xml-declaration="no"/>

    <xsl:param name="wbapi_lang"/>
    <xsl:param name="today"/>
    <xsl:variable name="wbld">&wbns;</xsl:variable>

    <xsl:template match="/">
        <xsl:variable name="wbld_indicator" select="normalize-space(/wb:data/wb:data[1]/wb:indicator/@id)"/>
        <xsl:variable name="wbld_indlabel" select="normalize-space(/wb:data/wb:data[1]/wb:indicator/text())"/>
        <rdf:RDF>
            <xsl:attribute name="xml:base">&wbns;</xsl:attribute>

            <!-- This source file -->
            <rdf:Description rdf:about="data/{$wbld_indicator}.rdf.gz">
                <rdfs:label><xsl:value-of select="$wbld_indlabel"/></rdfs:label>
                <foaf:primaryTopic rdf:resource="dataset/wdi/{$wbld_indicator}"/>
                <!-- Should put in a created-date here -->
                <cr:hasSparqlBookmark rdf:resource="dataset/wdi/{$wbld_indicator}_sparql"/>
                <dcterms:license rdf:resource="http://www.worldbank.org/terms-of-use-datasets"/>
                <dcterms:created rdf:datatype="http://www.w3.org/2001/XMLSchema#date"><xsl:value-of select="$today"/></dcterms:created>
            </rdf:Description>

            <qb:DataSet rdf:about="dataset/wdi/{$wbld_indicator}">
                <rdfs:label><xsl:value-of select="$wbld_indlabel"/></rdfs:label>
                <sdmx-attribute:dsi><xsl:value-of select="$wbld_indicator"/></sdmx-attribute:dsi>
                <dcterms:source rdf:resource="http://api.worldbank.org/en/countries/all/indicators/{$wbld_indicator}?format=xml"/>
                <cr:hasSparqlBookmark rdf:resource="dataset/wdi/{$wbld_indicator}_sparql"/>
            </qb:DataSet>

            <cr:SparqlBookmark rdf:about="dataset/wdi/{$wbld_indicator}_sparql">
                <rdfs:label>Simple SPARQL query</rdfs:label>
                <!-- <dcterms:format>text/html</dcterms:format> -->
                <cr:sparqlQuery>PREFIX qb: &lt;http://purl.org/linked-data/cube#>
PREFIX sdmx-measure: &lt;http://purl.org/linked-data/sdmx/2009/measure#>
PREFIX sdmx-dimension: &lt;http://purl.org/linked-data/sdmx/2009/dimension#>
PREFIX sdmx-attribute: &lt;http://purl.org/linked-data/sdmx/2009/attribute#>
PREFIX skos: &lt;http://www.w3.org/2004/02/skos/core#>

SELECT *
WHERE {
  _:obs qb:dataSet &lt;&wbns;dataset/wdi/<xsl:value-of select="$wbld_indicator"/>&gt; .
  _:obs sdmx-dimension:timePeriod ?date .
  _:obs sdmx-dimension:refArea ?area .
  _:obs sdmx-measure:obsValue ?value .
  _:obs sdmx-attribute:decimals ?decimals .
  OPTIONAL { _:obs sdmx-attribute:comment ?comment }
}
</cr:sparqlQuery>
            </cr:SparqlBookmark>
        <xsl:call-template name="indicatorsObservations"/>
        </rdf:RDF>
    </xsl:template>

    <xsl:template name="indicatorsObservations">

        <xsl:for-each select="wb:data/wb:data">
            <xsl:variable name="wbld_date" select="normalize-space(wb:date/text())"/>

            <xsl:variable name="wbld_country">
                <xsl:value-of select="normalize-space(wb:country/@id)"/>
            </xsl:variable>

            <xsl:variable name="id" select="normalize-space(@id)"/>
            <xsl:variable name="wbld_indicator" select="normalize-space(wb:indicator/@id)"/>

            <xsl:if test="normalize-space(wb:value/text()) != ''
                        and $wbld_date != ''
                        and $wbld_date != 'mrv'
                        and $wbld_date != 'most recent value'
                        and $wbld_country != ''
                        and not(contains($id, ' '))
                        ">

                <qb:Observation rdf:about="dataset/wdi/{$wbld_indicator}/{$wbld_country},{translate($wbld_date,' ','_')}">
                   <!-- <rdf:type rdf:resource="http://purl.org/linked-data/cube#Observation"/> -->
                    <qb:dataSet rdf:resource="dataset/wdi/{$wbld_indicator}"/>


                    <!-- <property:indicator rdf:resource="classification/indicator/{$wbld_indicator}"/> -->

                    <sdmx-dimension:refArea rdf:resource="classification/country/{$wbld_country}"/>

                    <xsl:call-template name="timePeriod">
                        <xsl:with-param name="wbld_date" select="$wbld_date"/>
                    </xsl:call-template>

                    <sdmx-measure:obsValue>
                        <xsl:if test="string(number(wb:value/text())) != 'NaN'">
                            <xsl:attribute name="rdf:datatype">http://www.w3.org/2001/XMLSchema#decimal</xsl:attribute>
                        </xsl:if>
                        <xsl:value-of select="normalize-space(wb:value/text())"/>
                    </sdmx-measure:obsValue>

                    <sdmx-attribute:decimals>
                        <xsl:attribute name="rdf:resource">http://purl.org/linked-data/sdmx/2009/code#decimals-<xsl:value-of select="normalize-space(wb:decimal/text())"/></xsl:attribute>
                    </sdmx-attribute:decimals>

                </qb:Observation>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>

<!-- Figure out what to write for the period
     Writes sdmx-dimension:freq, sdmx-dimension:timePeriod and sdmx-attribute:comment
 -->
    <xsl:template name="timePeriod">
        <xsl:param name="wbld_date"/>

        <xsl:choose>
            <xsl:when test="string-length($wbld_date) = 4">
                <sdmx-dimension:freq rdf:resource="http://purl.org/linked-data/sdmx/2009/code#freq-A"/>
                <sdmx-dimension:timePeriod>
                    <xsl:attribute name="rdf:datatype">http://www.w3.org/2001/XMLSchema#date</xsl:attribute>
                    <xsl:value-of select="$wbld_date"/>-01-01</sdmx-dimension:timePeriod>
            </xsl:when>
            <xsl:when test="substring-after($wbld_date,' ') = 'Target'">
                <sdmx-dimension:freq rdf:resource="http://purl.org/linked-data/sdmx/2009/code#freq-A"/>
                <sdmx-dimension:timePeriod>
                    <xsl:attribute name="rdf:datatype">http://www.w3.org/2001/XMLSchema#date</xsl:attribute>
                    <xsl:value-of select="substring-before($wbld_date,' ')"/>-01-01</sdmx-dimension:timePeriod>
                <sdmx-attribute:comment>Target</sdmx-attribute:comment>
            </xsl:when>
            <xsl:when test="substring($wbld_date, 5, 1) = 'Q'">
                <sdmx-dimension:freq rdf:resource="http://purl.org/linked-data/sdmx/2009/code#freq-Q"/>
                <sdmx-dimension:timePeriod>
                    <xsl:attribute name="rdf:datatype">http://www.w3.org/2001/XMLSchema#date</xsl:attribute>
                    <xsl:value-of select="substring-before($wbld_date,' ')"/>
                    <xsl:choose>
                        <xsl:when test="substring($wbld_date, 6, 1) = '1'">-01-01</xsl:when>
                        <xsl:when test="substring($wbld_date, 6, 1) = '2'">-04-01</xsl:when>
                        <xsl:when test="substring($wbld_date, 6, 1) = '3'">-07-01</xsl:when>
                        <xsl:when test="substring($wbld_date, 6, 1) = '4'">-10-01</xsl:when>
                    </xsl:choose>
                </sdmx-dimension:timePeriod>
                <sdmx-attribute:comment>Target</sdmx-attribute:comment>
            </xsl:when>
            <xsl:otherwise>
                <sdmx-dimension:timePeriod>
                    <xsl:value-of select="$wbld_date"/>
                </sdmx-dimension:timePeriod>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>

</xsl:stylesheet>
