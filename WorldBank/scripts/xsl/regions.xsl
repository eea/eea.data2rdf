<!DOCTYPE xsl:stylesheet [
    <!ENTITY wbns "http://rdfdata.eionet.europa.eu/worldbank/">
]>
<!--
    Author: Sarven Capadisli <info@csarven.ca>
    Author URL: http://csarven.ca/#i
-->
<xsl:stylesheet version="2.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
    xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
    xmlns:owl="http://www.w3.org/2002/07/owl#"
    xmlns:xsd="http://www.w3.org/2001/XMLSchema#"
    xmlns:wbldfn="&wbns;xpath-function/"
    xmlns:wgs="http://www.w3.org/2003/01/geo/wgs84_pos#"
    xmlns:dcterms="http://purl.org/dc/terms/"
    xmlns:foaf="http://xmlns.com/foaf/0.1/"
    xmlns:skos="http://www.w3.org/2004/02/skos/core#"
    xmlns:qb="http://purl.org/linked-data/cube#"
    xmlns:wb="http://www.worldbank.org"
    xmlns:wbld="&wbns;"
    xmlns:property="&wbns;property/">

    <xsl:import href="common.xsl"/>
    <xsl:output encoding="utf-8" indent="yes" method="xml" omit-xml-declaration="no"/>

    <xsl:param name="wbapi_lang"/>
    <xsl:variable name="wbld">&wbns;</xsl:variable>

    <xsl:template match="/">
        <rdf:RDF>
        <xsl:call-template name="regions"/>
        </rdf:RDF>
    </xsl:template>

    <xsl:template name="regions">
        <xsl:variable name="currentDateTime" select="wbldfn:now()"/>

        <rdf:Description rdf:about="{$wbld}classification/region">
            <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#ConceptScheme"/>
            <skos:prefLabel xml:lang="en">Code list for regions</skos:prefLabel>

            <skos:closeMatch rdf:resource="http://dbpedia.org/resource/Region"/>

            <xsl:variable name="dataSource">
                <xsl:text>http://api.worldbank.org/regions?format=xml</xsl:text>
            </xsl:variable>
            <xsl:call-template name="provenance">
                <xsl:with-param name="date" select="$currentDateTime"/>
                <xsl:with-param name="dataSource" select="$dataSource"/>
            </xsl:call-template>
        </rdf:Description>

        <xsl:for-each select="wb:regions/wb:region">
            <rdf:Description rdf:about="{$wbld}classification/region">
                <skos:hasTopConcept rdf:resource="{$wbld}classification/region/{normalize-space(wb:code/text())}"/>
            </rdf:Description>

            <rdf:Description rdf:about="{$wbld}classification/region/{normalize-space(wb:code/text())}">
                <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/>

                <skos:inScheme rdf:resource="{$wbld}classification/region"/>
                <skos:topConceptOf rdf:resource="{$wbld}classification/region"/>

                <xsl:if test="@id != ''">
                <dcterms:identifier><xsl:value-of select="@id"/></dcterms:identifier>
                </xsl:if>

                <skos:notation><xsl:value-of select="normalize-space(wb:code/text())"/></skos:notation>

                <xsl:if test="wb:name != ''">
                <skos:prefLabel xml:lang="{$wbapi_lang}"><xsl:value-of select="wb:name/text()"/></skos:prefLabel>
                </xsl:if>

                <xsl:variable name="dataSource">
                    <xsl:text>http://api.worldbank.org/regions/</xsl:text><xsl:value-of select="normalize-space(@id)"/><xsl:text>?format=xml</xsl:text>
                </xsl:variable>
                <xsl:call-template name="provenance">
                    <xsl:with-param name="date" select="$currentDateTime"/>
                    <xsl:with-param name="dataSource" select="$dataSource"/>
                </xsl:call-template>
            </rdf:Description>
        </xsl:for-each>

        <rdf:Description rdf:about="{$wbld}property/region">
            <rdf:type rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"/>
            <rdf:type rdf:resource="http://purl.org/linked-data/cube#DimensionProperty"/>
            <rdfs:label xml:lang="en">Region</rdfs:label>
            <qb:codeList rdf:resource="{$wbld}classification/region"/>
        </rdf:Description>
    </xsl:template>
</xsl:stylesheet>
