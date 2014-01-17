<!DOCTYPE xsl:stylesheet [
    <!ENTITY wbns "http://rdfdata.eionet.europa.eu/worldbank/">
]>

<!--
    Common styles for XSL-T version 1.0
-->
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:wb="http://www.worldbank.org"
    xmlns:property="&wbns;property/"
    >

    <xsl:output encoding="utf-8" indent="yes" method="xml" omit-xml-declaration="no"/>

    <xsl:param name="pathToCountries"/>
    <xsl:param name="pathToCurrencies"/>

    <xsl:variable name="classification">&wbns;classification/</xsl:variable>

    <xsl:template name="safe-term">
        <xsl:param name="string"/>
        <xsl:value-of select="replace(replace(replace(replace(replace(lower-case(encode-for-uri(replace(normalize-space($string), ' - ', '-'))), '%20|%2f|%27', '-'), '%28|%29|%24|%2c', ''), '_', '-'), '--', '-'), '^-|-$', '')"/>
    </xsl:template>

    <xsl:template name="datatype-dateTime">
        <xsl:attribute name="rdf:datatype">
            <xsl:text>http://www.w3.org/2001/XMLSchema#dateTime</xsl:text>
        </xsl:attribute>
    </xsl:template>

    <xsl:template name="datatype-date">
        <xsl:attribute name="rdf:datatype">
            <xsl:text>http://www.w3.org/2001/XMLSchema#date</xsl:text>
        </xsl:attribute>
    </xsl:template>

    <xsl:template name="datatype-xsd-decimal">
        <xsl:attribute name="rdf:datatype">
            <xsl:text>http://www.w3.org/2001/XMLSchema#decimal</xsl:text>
        </xsl:attribute>
    </xsl:template>

    <xsl:template name="datatype-dbo-usd">
        <xsl:attribute name="rdf:datatype">
            <xsl:text>http://dbpedia.org/resource/United_States_dollar</xsl:text>
        </xsl:attribute>
    </xsl:template>

    <xsl:template name="provenance">
        <xsl:param name="date"/>
        <xsl:param name="dataSource"/>
        <dcterms:created rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime">2013-03-09T00:00:00Z</dcterms:created>

        <dcterms:issued>
            <xsl:call-template name="datatype-dateTime"/>
            <xsl:value-of select="$date"/>
        </dcterms:issued>
        <dcterms:source rdf:resource="{$dataSource}"/>
        <foaf:maker rdf:resource="http://www.eionet.europa.eu/users/roug"/>
        <dcterms:license rdf:resource="http://creativecommons.org/publicdomain/zero/1.0/"/>
    </xsl:template>

</xsl:stylesheet>
