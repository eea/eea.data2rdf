<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE xsl:stylesheet [
  <!ENTITY xsd "http://www.w3.org/2001/XMLSchema#">
  <!ENTITY ontology  "http://rdfdata.eionet.europa.eu/who/ontology/">
  <!ENTITY prefix  "http://rdfdata.eionet.europa.eu/who/ontology/">
]>

<xsl:stylesheet
  xmlns:property="&ontology;"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:skos="http://www.w3.org/2004/02/skos/core#"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:cc="http://creativecommons.org/ns#"
  xmlns:qb="http://purl.org/linked-data/cube#"
  xmlns:sdmx-measure="http://purl.org/linked-data/sdmx/2009/measure#"
  xmlns:sdmx-dimension="http://purl.org/linked-data/sdmx/2009/dimension#"
  xmlns:sdmx-attribute="http://purl.org/linked-data/sdmx/2009/attribute#"
version="1.0">

<xsl:output method="xml" indent="yes"/>

<xsl:template match="GHO">
	<rdf:RDF>
		<!-- <xsl:attribute name="xml:base">&prefix;</xsl:attribute> -->
		<rdf:Description rdf:about="">
                        <rdfs:label><xsl:value-of select="Metadata/Dimension[@Label='GHO']/Code/Display[1]"/></rdfs:label>
			<dcterms:source>Dataset from http://apps.who.int/athena/data/GHO/<xsl:value-of select="Metadata/Dimension[@Label='GHO']/Code/@Label"/>.xml</dcterms:source>
			<dcterms:source>WHO - World Health Organization</dcterms:source>
                        <dcterms:license rdf:resource="http://www.who.int/about/copyright/en/index.html"/>
			<dcterms:created rdf:datatype="&xsd;dateTime"><xsl:value-of select="@Created"/></dcterms:created>
<!--
			<cc:license rdf:resource="http://creativecommons.org/licenses/by/2.5/dk/"/>
			<cc:morePermissions rdf:resource="http://www.eea.europa.eu/legal/copyright"/>
-->
		</rdf:Description>
		<xsl:apply-templates select="Data"/>
	</rdf:RDF>
</xsl:template>

<xsl:template match="Data">
		<xsl:apply-templates select="Observation"/>
</xsl:template>

<xsl:template match="Observation">
	<qb:Observation>
		<xsl:attribute name="rdf:ID"><xsl:value-of select="generate-id()"/></xsl:attribute>
                <qb:dataSet rdf:resource=""/>
		<xsl:apply-templates/>
	</qb:Observation>
</xsl:template>

<xsl:template match="Dim[@Category='YEAR']">
    <xsl:element name="sdmx-dimension:timePeriod">
     <xsl:attribute name="rdf:datatype">http://www.w3.org/2001/XMLSchema#date</xsl:attribute><xsl:value-of select="@Code"/>-01-01</xsl:element>
</xsl:template>

<xsl:template match="Dim">
    <xsl:variable name="lcletters">abcdefghijklmnopqrstuvwxyz</xsl:variable>
    <xsl:variable name="ucletters">ABCDEFGHIJKLMNOPQRSTUVWXYZ</xsl:variable>

    <xsl:element name="{concat('property:',translate(@Category,$ucletters,$lcletters))}">
     <xsl:attribute name="rdf:resource">http://rdfdata.eionet.europa.eu/who/<xsl:value-of select="@Category"/>.rdf#<xsl:value-of select="@Code"/></xsl:attribute>
     </xsl:element>
</xsl:template>

<xsl:template match="Value">
  <sdmx-measure:obsValue rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal"><xsl:value-of select="@Numeric"/></sdmx-measure:obsValue>
<!-- See MDG_0000000023 Numeric="452.00000" Low="817.00000" High="195.00000" -->
  <xsl:if test="@Low">
    <property:low rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal"><xsl:value-of select="@Low"/></property:low>
  </xsl:if>
  <xsl:if test="@High">
    <property:high rdf:datatype="http://www.w3.org/2001/XMLSchema#decimal"><xsl:value-of select="@High"/></property:high>
  </xsl:if>
</xsl:template>

<xsl:template match="*"/>

</xsl:stylesheet>
