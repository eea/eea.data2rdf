<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:skos="http://www.w3.org/2004/02/skos/core#"
  xmlns:dcterms="http://purl.org/dc/terms/"
  xmlns:cc="http://creativecommons.org/ns#"
version="1.0">

  <xsl:output method="xml" indent="yes"/>

  <xsl:param name="vocabulary"/>
  <xsl:param name="baseuri"/>

<xsl:template match="GHO">
	<rdf:RDF>
		<xsl:attribute name="xml:base"><xsl:value-of select="$baseuri"/></xsl:attribute>
		<rdf:Description rdf:about="">
			<rdfs:label>Code list from http://apps.who.int/gho/athena/data/</rdfs:label>
			<dcterms:source>WHO</dcterms:source>
			<dcterms:created rdf:datatype="http://www.w3.org/2001/XMLSchema#dateTime"><xsl:value-of select="@Created"/></dcterms:created>
<!--
			<cc:license rdf:resource="http://creativecommons.org/licenses/by/2.5/dk/"/>
			<cc:morePermissions rdf:resource="http://www.eea.europa.eu/legal/copyright"/>
-->
		</rdf:Description>
		<xsl:apply-templates select="Metadata/Dimension"/>
	</rdf:RDF>
</xsl:template>

<xsl:template match="Metadata/Dimension">
		<xsl:apply-templates select="Code"/>
</xsl:template>

<xsl:template match="Code">
	<skos:Concept>
		<xsl:attribute name="rdf:ID"><xsl:value-of select="@Label"/></xsl:attribute>
		<skos:notation><xsl:value-of select="@Label"/></skos:notation>
		<skos:prefLabel><xsl:value-of select="Display"/></skos:prefLabel>
		<skos:inScheme>
			<rdf:Description rdf:about="">
				<skos:hasTopConcept><xsl:attribute name="rdf:resource">#<xsl:value-of select="@Label"/></xsl:attribute></skos:hasTopConcept>
			</rdf:Description>
		</skos:inScheme>
	</skos:Concept>
</xsl:template>

<xsl:template match="*"/>

</xsl:stylesheet>
