<!DOCTYPE xsl:stylesheet [
    <!ENTITY wbns "http://rdfdata.eionet.europa.eu/worldbank/">
]>
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
    xmlns:void="http://rdfs.org/ns/void#"
    xmlns:country="&wbns;classification/country/"
    xmlns:indicator="&wbns;classification/indicator/"
    xmlns:dataset="&wbns;dataset/"
    xmlns:year="http://reference.data.gov.uk/id/year/"
    xmlns:quarter="http://reference.data.gov.uk/id/quarter/"
    >

    <xsl:import href="common10.xsl"/>
    <xsl:output encoding="utf-8" indent="yes" method="xml" omit-xml-declaration="no"/>

    <xsl:param name="wbapi_lang"/>
    <xsl:param name="entitiesFile"/>
    <xsl:param name="currentDateTime"/>

    <xsl:variable name="wbld">&wbns;</xsl:variable>

    <xsl:template match="/">
        <rdf:RDF>
            <xsl:attribute name="xml:base">&wbns;</xsl:attribute>
            <foaf:Organization rdf:about="void.rdf#WORLDBANK">
                <rdfs:label>World Bank</rdfs:label>
                <foaf:name>World Bank</foaf:name>
                <foaf:homepage rdf:resource="http://www.worldbank.org/"/>
            </foaf:Organization>

            <xsl:call-template name="indicators"/>
        </rdf:RDF>
    </xsl:template>

    <xsl:template name="indicators">
        <void:DatasetDescription rdf:about="void.rdf">
            <rdfs:label>World Bank indicators</rdfs:label>
            <rdfs:label xml:lang="fr">Indicateurs de développement dans le monde</rdfs:label>

            <dcterms:description xml:lang="en">Indicators represent data like total population, gross national income, energy use, and many more.</dcterms:description>

            <xsl:variable name="dataSource">
                <xsl:text>http://api.worldbank.org/indicators?format=xml</xsl:text>
            </xsl:variable>
            <xsl:call-template name="provenance">
                <xsl:with-param name="date" select="$currentDateTime"/>
                <xsl:with-param name="dataSource" select="$dataSource"/>
            </xsl:call-template>
        </void:DatasetDescription>

        <xsl:for-each select="wb:indicators/wb:indicator">
            <xsl:variable name="id" select="normalize-space(@id)"/>

            <xsl:if test="not(contains($id, ' '))">
                <void:Dataset rdf:about="void.rdf#{$id}">
                    <void:dataDump rdf:resource="{$wbld}data/{$id}.rdf.gz"/>
                    <skos:notation><xsl:value-of select="$id"/></skos:notation>

                    <dcterms:publisher rdf:resource="void.rdf#WORLDBANK"/>
                    <dcterms:creator rdf:resource="void.rdf#WORLDBANK"/>
                    <xsl:if test="document($entitiesFile)/indicators/i[@name=$id]">
                        <foaf:entities rdf:datatype="http://www.w3.org/2001/XMLSchema#int"><xsl:value-of select="document($entitiesFile)/indicators/i[@name=$id]/@total"/></foaf:entities>
                    </xsl:if>
                    <xsl:if test="wb:name != ''">
                    <dcterms:title xml:lang="{$wbapi_lang}"><xsl:value-of select="normalize-space(wb:name/text())"/></dcterms:title>
                    </xsl:if>

                    <foaf:isPrimaryTopicOf rdf:resource="http://data.worldbank.org/indicator/{$id}"/>

                    <xsl:if test="wb:source/@id">
                    <dcterms:source rdf:resource="{$wbld}classification/source/{normalize-space(wb:source/@id)}"/>
                    </xsl:if>

                    <xsl:if test="wb:sourceNote != ''">
                    <dcterms:description xml:lang="{$wbapi_lang}"><xsl:value-of select="normalize-space(wb:sourceNote/text())"/></dcterms:description>
                    </xsl:if>

                    <xsl:if test="wb:sourceOrganization != ''">
                    <property:source-organization xml:lang="{$wbapi_lang}"><xsl:value-of select="wb:sourceOrganization/text()"/></property:source-organization>
                    </xsl:if>

                    <xsl:for-each select="wb:topics/wb:topic">
                    <dcterms:subject rdf:resource="{$wbld}classification/topic/{normalize-space(@id)}"/>
                    </xsl:for-each>

                    <!--
                    <xsl:variable name="dataSource">
                        <xsl:text>http://api.worldbank.org/indicator/</xsl:text><xsl:value-of select="$id"/><xsl:text>?format=xml</xsl:text>
                    </xsl:variable>

                    <xsl:call-template name="provenance">
                        <xsl:with-param name="date" select="$currentDateTime"/>
                        <xsl:with-param name="dataSource" select="$dataSource"/>
                    </xsl:call-template>
                    -->
                </void:Dataset>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
