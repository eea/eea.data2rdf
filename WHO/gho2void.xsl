<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"
  xmlns:rdfs="http://www.w3.org/2000/01/rdf-schema#"
  xmlns:foaf="http://xmlns.com/foaf/0.1/"
  xmlns:skos="http://www.w3.org/2004/02/skos/core#"
  xmlns:void="http://rdfs.org/ns/void#"
  xmlns:dct="http://purl.org/dc/terms/"
  xmlns:cc="http://creativecommons.org/ns#"
  xmlns:cr="http://cr.eionet.europa.eu/ontologies/contreg.rdf#"
version="1.0">

  <xsl:output method="xml" indent="yes"/>

  <xsl:param name="baseuri"/>
  <xsl:param name="vocabulary"/>
  <xsl:param name="datasets" select="document('tmp/void-support.xml')/datasets/text()"/>

<xsl:template match="GHO">
    <rdf:RDF>
	<!-- <xsl:attribute name="xml:base"><xsl:value-of select="$baseuri"/>void.rdf</xsl:attribute> -->

        <void:DatasetDescription rdf:about="">
            <rdfs:label>WHO datasets from http://apps.who.int/gho/athena/data</rdfs:label>
            <dct:source rdf:resource="#WHO"/>
            <dct:date rdf:datatype="http://www.w3.org/2001/XMLSchema#date">2012-11-23</dct:date>
    <!--
            <cc:license rdf:resource="http://creativecommons.org/licenses/by/2.5/dk/"/>
            <cc:morePermissions rdf:resource="http://www.eea.europa.eu/legal/copyright"/>
    -->
        </void:DatasetDescription>

        <foaf:Organization rdf:ID="WHO">
            <foaf:name>World Health Organization</foaf:name>
            <foaf:homepage rdf:resource="http://www.who.int/"/>
        </foaf:Organization>

        <skos:Concept rdf:ID="_AIR">
            <skos:notation>AIR</skos:notation>
            <skos:prefLabel>Air pollution</skos:prefLabel>
        </skos:Concept>

        <skos:Concept rdf:ID="_BP">
            <skos:notation>BP</skos:notation>
            <skos:prefLabel>Blood pressure</skos:prefLabel>
        </skos:Concept>

        <skos:Concept rdf:ID="_CC">
            <skos:notation>CC</skos:notation>
            <skos:prefLabel>Climate change</skos:prefLabel>
        </skos:Concept>

        <skos:Concept rdf:ID="_CHOL">
            <skos:notation>CHOL</skos:notation>
            <skos:prefLabel>Cholesterol</skos:prefLabel>
        </skos:Concept>

        <skos:Concept rdf:ID="_CM">
            <skos:notation>CM</skos:notation>
            <skos:prefLabel>Child mortality</skos:prefLabel>
        </skos:Concept>

        <skos:Concept rdf:ID="_LEAD">
            <skos:notation>LEAD</skos:notation>
            <skos:prefLabel>Lead</skos:prefLabel>
        </skos:Concept>

        <skos:Concept rdf:ID="_LIFE">
            <skos:notation>LIFE</skos:notation>
            <skos:prefLabel>Life</skos:prefLabel>
        </skos:Concept>

        <skos:Concept rdf:ID="_OCC">
            <skos:notation>OCC</skos:notation>
            <skos:prefLabel>Occupational health</skos:prefLabel>
        </skos:Concept>

        <skos:Concept rdf:ID="_RS">
            <skos:notation>RS</skos:notation>
            <skos:prefLabel>Road safety</skos:prefLabel>
        </skos:Concept>

        <skos:Concept rdf:ID="_SHS">
            <skos:notation>SHS</skos:notation>
            <skos:prefLabel>Second-hand smoke</skos:prefLabel>
        </skos:Concept>

         <xsl:call-template name="concepts"/>

	<xsl:apply-templates select="Metadata"/>
    </rdf:RDF>
</xsl:template>

<xsl:template match="Metadata|Dimension">
    <xsl:apply-templates/>
</xsl:template>

<xsl:template match="Code">
    <void:Dataset>
	<xsl:attribute name="rdf:ID"><xsl:value-of select="@Label"/></xsl:attribute>
	<dct:creator rdf:resource="#WHO"/>
	<dct:publisher rdf:resource="#WHO"/>
	<skos:notation><xsl:value-of select="@Label"/></skos:notation>
	<foaf:isPrimaryTopicOf><xsl:attribute name="rdf:resource"><xsl:value-of select="@URL"/></xsl:attribute></foaf:isPrimaryTopicOf>
	<dct:title><xsl:value-of select="Display"/></dct:title>
	<rdfs:label><xsl:value-of select="Display"/></rdfs:label>
	<void:dataDump><xsl:attribute name="rdf:resource">data/<xsl:value-of select="@Label"/>.rdf.gz</xsl:attribute></void:dataDump>
        <xsl:choose>
            <xsl:when test="substring(@Label,1,4) = 'AIR_'">
                <cr:tag>air pollution</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_AIR</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,3) = 'BP_'">
                <cr:tag>blood pressure</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_BP</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,3) = 'CC_'">
                <cr:tag>climate change</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_CC</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,5) = 'CHOL_'">
                <cr:tag>cholesterol</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_CHOL</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,8) = 'CHOLERA_'">
                <cr:tag>cholera</cr:tag>
            </xsl:when>
            <xsl:when test="substring(@Label,1,3) = 'CM_'">
                <cr:tag>child mortality</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_CM</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,5) = 'LEAD_'">
                <cr:tag>lead</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_LEAD</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,5) = 'LIFE_'">
                <cr:tag>life</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_LIFE</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,8) = 'MALARIA_'">
                <cr:tag>malaria</cr:tag>
            </xsl:when>
            <xsl:when test="substring(@Label,1,7) = 'MENING_'">
                <cr:tag>meningitis</cr:tag>
            </xsl:when>
            <xsl:when test="substring(@Label,1,3) = 'MH_'">
                <cr:tag>mental health</cr:tag>
            </xsl:when>
            <xsl:when test="substring(@Label,1,5) = 'MORT_'">
                <cr:tag>mortality</cr:tag>
            </xsl:when>
            <xsl:when test="substring(@Label,1,10) = 'NUTRITION_'">
                <cr:tag>nutrition</cr:tag>
            </xsl:when>
            <xsl:when test="substring(@Label,1,4) = 'OCC_'">
                <cr:tag>occupational health</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_OCC</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,3) = 'RS_'">
                <cr:tag>road safety</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_RS</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,4) = 'SHS_'">
                <cr:tag>second-hand smoke</cr:tag>
               <dct:subject><xsl:attribute name="rdf:resource">#_SHS</xsl:attribute></dct:subject>
            </xsl:when>
            <xsl:when test="substring(@Label,1,3) = 'TB_'">
                <cr:tag>tuberculosis</cr:tag>
            </xsl:when>
            <xsl:when test="substring(@Label,1,8) = 'TOBACCO_'">
                <cr:tag>tobacco</cr:tag>
            </xsl:when>
        </xsl:choose>
         <xsl:call-template name="categories"><xsl:with-param name="code" select="@Label"/></xsl:call-template>
	<xsl:apply-templates/>
    </void:Dataset>
</xsl:template>

<xsl:template match="description">
     <rdfs:seeAlso><xsl:attribute name="rdf:resource"><xsl:value-of select="@url"/></xsl:attribute></rdfs:seeAlso>
</xsl:template>

<xsl:template match="*"/>

<xsl:template name="concepts">
  <xsl:for-each select="document('dimensions/GHOCAT.xml')/GHO/Metadata/Dimension/Code">
    <skos:Concept><xsl:attribute name="rdf:ID">_<xsl:value-of select="@Label"/></xsl:attribute>
      <skos:notation><xsl:value-of select="@Label"/></skos:notation>
      <skos:prefLabel><xsl:value-of select="Display"/></skos:prefLabel>
    </skos:Concept>
  </xsl:for-each>
</xsl:template>

<xsl:template name="categories">
	<xsl:param name="code"/>
        <xsl:for-each select="document('dimensions/GHOCAT.xml')/GHO/Metadata/Dimension/Code">
        <xsl:if test="starts-with($code,@Label)">
           <dct:subject><xsl:attribute name="rdf:resource">#_<xsl:value-of select="@Label"/></xsl:attribute></dct:subject>
        </xsl:if>
        </xsl:for-each>
</xsl:template>
</xsl:stylesheet>
