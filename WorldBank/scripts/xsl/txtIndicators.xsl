<!DOCTYPE xsl:stylesheet [
    <!ENTITY wbns "http://rdfdata.eionet.europa.eu/worldbank/">
]>
<xsl:stylesheet version="1.0"
    xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
    xmlns:qb="http://purl.org/linked-data/cube#"
    xmlns:wb="http://www.worldbank.org">

    <xsl:output encoding="utf-8" indent="no" method="text"/>

    <xsl:param name="wbapi_lang"/>

    <xsl:template match="/">
            <xsl:for-each select="wb:indicators/wb:indicator">
            <xsl:value-of select="@id"/><xsl:text>
</xsl:text>
            </xsl:for-each>
    </xsl:template>

</xsl:stylesheet>
