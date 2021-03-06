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
    xmlns:sdmx-dimension="http://purl.org/linked-data/sdmx/2009/dimension#"
    xmlns:sdmx-code="http://purl.org/linked-data/sdmx/2009/code#"
    xmlns:wb="http://www.worldbank.org"
    xmlns:wbld="&wbns;"
    xmlns:property="&wbns;property/"
    xmlns:classification="&wbns;classification/">

    <xsl:import href="common.xsl"/>
    <xsl:output encoding="utf-8" indent="yes" method="xml" omit-xml-declaration="no"/>

    <xsl:param name="wbapi_lang"/>
    <xsl:param name="pathToMeta"/>
    <xsl:param name="pathToCountries"/>
    <xsl:param name="pathToLendingTypes"/>
    <xsl:param name="pathToCurrencies"/>
    <xsl:param name="pathToRegionsExtra"/>
    <xsl:param name="pathToFinancesDictionary"/>
    <xsl:param name="financeDatasetID"/>

    <xsl:variable name="wbld">&wbns;</xsl:variable>
    <xsl:variable name="property">&wbns;property/</xsl:variable>
    <xsl:variable name="classification">&wbns;classification/</xsl:variable>
    <xsl:variable name="qb">http://purl.org/linked-data/cube#</xsl:variable>
    <xsl:variable name="rdfProperty">http://www.w3.org/1999/02/22-rdf-syntax-ns#Property</xsl:variable>



    <xsl:template match="/">
        <rdf:RDF>
        <xsl:call-template name="financesObservations"/>
        </rdf:RDF>
    </xsl:template>

    <xsl:template name="financesObservations">
        <xsl:variable name="currentDateTime" select="format-dateTime(current-dateTime(), '[Y0001]-[M01]-[D01]T[H01]:[m01]:[s01]Z')"/>

        <xsl:choose>
            <!-- XXX: When running this XSLT, make sure that this case gets taken care of first. -->
            <xsl:when test="$financeDatasetID = 'wc6g-9zmq'">
                <xsl:for-each select="response/row/row">

                    <xsl:variable name="data_element" select="wbldfn:canonical-term(wbldfn:safe-term(data_element))"/>

                    <xsl:if test="wbldfn:usable-term($data_element)">
                        <xsl:variable name="dataset_name">
                            <xsl:if test="wbldfn:prepend-dataset($data_element)">
                                <xsl:value-of select="wbldfn:safe-term(dataset_name)"/><xsl:text>-</xsl:text>
                            </xsl:if>
                        </xsl:variable>

                        <xsl:variable name="resourceDescriptionProperty">
                            <xsl:value-of select="$wbld"/><xsl:text>property/</xsl:text><xsl:value-of select="$dataset_name"/><xsl:value-of select="$data_element"/>
                        </xsl:variable>

                        <rdf:Description rdf:about="{$resourceDescriptionProperty}">
                            <rdf:type rdf:resource="http://www.w3.org/1999/02/22-rdf-syntax-ns#Property"/>

                            <!-- TODO: I'm not sure about these qb concept/codeList for ibrd/ida project-ids-->
<!--                            <qb:concept rdf:resource="{$classification}{$data_element}"/> -->

                            <xsl:if test="wbldfn:classification($data_element)">
                                <qb:codeList rdf:resource="{$classification}{$data_element}"/>
                            </xsl:if>

                            <rdfs:label xml:lang="{$wbapi_lang}"><xsl:value-of select="normalize-space(data_element)"/></rdfs:label>
                            <!-- <property:uuid><xsl:value-of select="@_uuid"/></property:uuid> -->
                            <!-- <property:view-row-id><xsl:value-of select="@_id"/></property:view-row-id> -->

                            <xsl:variable name="dataSource">
                                <xsl:text>http://finances.worldbank.org/api/views/wc6g-9zmq/rows.xml</xsl:text>
                            </xsl:variable>
                            <xsl:call-template name="provenance">
                                <xsl:with-param name="date" select="$currentDateTime"/>
                                <xsl:with-param name="dataSource" select="$dataSource"/>
                            </xsl:call-template>

                            <xsl:choose>
                                <xsl:when test="$data_element = 'admin-budget-type'
                                                or $data_element = 'agreement-signing-date'
                                                or $data_element = 'approval-quarter'
                                                or $data_element = 'as-of-date'
                                                or $data_element = 'beneficiary'
                                                or $data_element = 'board-approval-date'
                                                or $data_element = 'borrower'
                                                or $data_element = 'calendar-year'
                                                or $data_element = 'category'
                                                or $data_element = 'closed-date-most-recent'
                                                or $data_element = 'contribution-type'
                                                or $data_element = 'counterparty-rating'
                                                or $data_element = 'country'
                                                or $data_element = 'credit-status'
                                                or $data_element = 'donor'
                                                or $data_element = 'donor-agency'
                                                or $data_element = 'effective-date-most-recent'
                                                or $data_element = 'end-of-period'
                                                or $data_element = 'financial-product'
                                                or $data_element = 'first-repayment-date'
                                                or $data_element = 'fiscal-year'
                                                or $data_element = 'fiscal-year-of-agreement'
                                                or $data_element = 'fiscal-year-of-receipt'
                                                or $data_element = 'fund'
                                                or $data_element = 'fund-name'
                                                or $data_element = 'fund-type'
                                                or $data_element = 'grant-agreement-date'
                                                or $data_element = 'grant-fund-number'
                                                or $data_element = 'grant-name'
                                                or $data_element = 'guarantor'
                                                or $data_element = 'last-disbursement-date'
                                                or $data_element = 'last-repayment-date'
                                                or $data_element = 'line-item'
                                                or $data_element = 'loan-number'
                                                or $data_element = 'loan-status'
                                                or $data_element = 'loan-type'
                                                or $data_element = 'member'
                                                or $data_element = 'membership'
                                                or $data_element = 'notes'
                                                or $data_element = 'organization'
                                                or $data_element = 'period-end-date'
                                                or $data_element = 'principal-recipient'
                                                or $data_element = 'program-code'
                                                or $data_element = 'program-name'
                                                or $data_element = 'project'
                                                or $data_element = 'receipt-quarter'
                                                or $data_element = 'receipt-type'
                                                or $data_element = 'recipient'
                                                or $data_element = 'region'
                                                or $data_element = 'sector-theme'
                                                or $data_element = 'source'
                                                or $data_element = 'status'
                                                or $data_element = 'sub-account'
                                                or $data_element = 'transfer-quarter'
                                                or $data_element = 'trustee-fund'
                                                or $data_element = 'trustee-fund-name'
                                                or $data_element = 'use-code'
                                                or $data_element = 'vpu'
                                                or $data_element = 'vpu-code'
                                                or $data_element = 'vpu-group'
                                                or $data_element = 'vpu-group-code'
                                                or $data_element = 'vpu-type'
                                                ">
                                    <rdf:type rdf:resource="{$qb}DimensionProperty"/>
                                </xsl:when>

                                <xsl:when test="wbldfn:money-amount($data_element)">
                                    <rdf:type rdf:resource="{$qb}MeasureProperty"/>
                                </xsl:when>

                                <xsl:when test="$data_element = 'equity-to-loans-ratio'
                                                or $data_element = 'interest-rate'
                                                or $data_element = 'number-of-votes'
                                                or $data_element = 'percentage-of-total-shares'
                                                or $data_element = 'percentage-of-total-votes'
                                                or $data_element = 'service-charge-rate'
                                                or $data_element = 'shares'
                                                ">
                                    <rdf:type rdf:resource="{$qb}MeasureProperty"/>
                                </xsl:when>

                                <xsl:when test="$data_element = 'currency'">
                                    <rdf:type rdf:resource="{$qb}AttributeProperty"/>
                                    <rdfs:subPropertyOf rdf:resource="http://purl.org/linked-data/sdmx/2009/attribute#unitMeasure"/>
                                </xsl:when>

                                <!-- XXX: This is mostly here for development. The final output shouldn't have this property, object -->
                                <xsl:otherwise>
<xsl:message>FIXME-i--------<xsl:value-of select="$data_element"/></xsl:message>
                                    <rdf:type rdf:resource="{$qb}FIXME-i--------"/>
                                </xsl:otherwise>
                            </xsl:choose>
                        </rdf:Description>

                        <rdf:Description rdf:about="{$classification}finance">
                            <skos:hasTopConcept rdf:resource="{$classification}{$data_element}"/>
                        </rdf:Description>

                        <rdf:Description rdf:about="{$classification}{$data_element}">
<!--                                <rdf:type rdf:resource="http://www.w3.org/2004/02/skos/core#Concept"/> -->
                            <skos:inScheme rdf:resource="{$classification}finance"/>
                            <skos:topConceptOf rdf:resource="{$classification}finance"/>

                            <skos:prefLabel xml:lang="{$wbapi_lang}"><xsl:value-of select="normalize-space(data_element)"/></skos:prefLabel>
                            <skos:definition xml:lang="{$wbapi_lang}"><xsl:value-of select="description"/></skos:definition>

                            <xsl:variable name="dataSource">
                                <xsl:text>http://finances.worldbank.org/api/views/</xsl:text><xsl:value-of select="$financeDatasetID"/><xsl:text>/rows.xml</xsl:text>
                            </xsl:variable>
                            <xsl:call-template name="provenance">
                                <xsl:with-param name="date" select="$currentDateTime"/>
                                <xsl:with-param name="dataSource" select="$dataSource"/>
                            </xsl:call-template>
                        </rdf:Description>
                    </xsl:if>
                </xsl:for-each>
            </xsl:when>

            <xsl:otherwise>
                <xsl:choose>
                    <xsl:when test="$financeDatasetID = '536v-dxib'">
                        <xsl:variable name="datasetCase">
                            <xsl:text>a</xsl:text>
                        </xsl:variable>
                        <xsl:variable name="ignoreProperty">
                            <xsl:text>receipt-amount</xsl:text>
                        </xsl:variable>
                        <xsl:call-template name="createDescriptions">
                            <xsl:with-param name="datasetCase" select="$datasetCase"/>
                            <xsl:with-param name="ignoreProperty" select="$ignoreProperty"/>
                        </xsl:call-template>

                        <xsl:variable name="datasetCase">
                            <xsl:text>b</xsl:text>
                        </xsl:variable>
                        <xsl:variable name="ignoreProperty">
                            <xsl:text>amount-in-usd</xsl:text>
                        </xsl:variable>
                        <xsl:call-template name="createDescriptions">
                            <xsl:with-param name="datasetCase" select="$datasetCase"/>
                            <xsl:with-param name="ignoreProperty" select="$ignoreProperty"/>
                        </xsl:call-template>
                    </xsl:when>

                    <xsl:otherwise>
                        <xsl:call-template name="createDescriptions"/>
                    </xsl:otherwise>
                </xsl:choose>
            </xsl:otherwise>
        </xsl:choose>
    </xsl:template>


    <xsl:template name="createDescriptions">
        <xsl:param name="datasetCase"/>
        <xsl:param name="ignoreProperty"/>

        <xsl:variable name="financeDatasetID">
            <xsl:choose>
                <xsl:when test="$datasetCase = ''">
                    <xsl:value-of select="$financeDatasetID"/>
                </xsl:when>
                <xsl:otherwise>
                    <xsl:value-of select="$financeDatasetID"/><xsl:text>/</xsl:text><xsl:value-of select="$datasetCase"/>
                </xsl:otherwise>
            </xsl:choose>
        </xsl:variable>


        <xsl:for-each select="//response/row/row[1]/*">
            <xsl:variable name="dataElement" select="wbldfn:canonical-term(wbldfn:safe-term(name()))"/>

            <xsl:if test="wbldfn:usable-term($dataElement) and $dataElement != $ignoreProperty">
                <xsl:variable name="financeDataset">
                    <xsl:value-of select="$wbld"/><xsl:text>dataset/world-bank-finances/</xsl:text><xsl:value-of select="$financeDatasetID"/>
                </xsl:variable>

                <xsl:variable name="datasetName">
                    <xsl:value-of select="document($pathToMeta)/rdf:RDF/rdf:Description[@rdf:about = $financeDataset]/rdfs:label"/>
                </xsl:variable>

                <xsl:variable name="datasetName">
                    <xsl:if test="wbldfn:prepend-dataset($dataElement)">
                        <xsl:value-of select="wbldfn:safe-term($datasetName)"/><xsl:text>-</xsl:text>
                    </xsl:if>
                </xsl:variable>

                <xsl:variable name="resourceDescriptionProperty">
                    <xsl:value-of select="$wbld"/><xsl:text>property/</xsl:text><xsl:value-of select="$datasetName"/><xsl:value-of select="$dataElement"/>
                </xsl:variable>
<!-- <xsl:message><xsl:text>resourceDescriptionProperty: </xsl:text><xsl:value-of select="$resourceDescriptionProperty"/></xsl:message> -->

                <qb:DataStructureDefinition rdf:about="{$wbld}dataset/world-bank-finances/{$financeDatasetID}/structure">
                    <qb:component>
                        <qb:ComponentSpecification>
                            <xsl:variable name="componentPropertyURI">
                                <xsl:value-of select="document($pathToFinancesDictionary)/rdf:RDF/rdf:Description[@rdf:about = $resourceDescriptionProperty][1]/rdf:type[@rdf:resource != $rdfProperty]/@rdf:resource"/>
                            </xsl:variable>

                            <xsl:variable name="componentPropertyURI">
                                <xsl:choose>
                                    <xsl:when test="$componentPropertyURI = ''">
                                        <xsl:value-of select="document($pathToMeta)/rdf:RDF/rdf:Description[@rdf:about = $resourceDescriptionProperty][1]/rdf:type[@rdf:resource != $rdfProperty]/@rdf:resource"/>
                                    </xsl:when>

                                    <xsl:otherwise>
                                        <xsl:value-of select="$componentPropertyURI"/>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>

<!-- <xsl:message><xsl:text>componentPropertyURI: </xsl:text><xsl:value-of select="$componentPropertyURI"/></xsl:message> -->
                            <xsl:variable name="componentProperty">
                                <xsl:choose>
                                    <xsl:when test="$componentPropertyURI = 'http://purl.org/linked-data/cube#DimensionProperty'">
                                        <xsl:text>qb:dimension</xsl:text>
                                    </xsl:when>
                                    <xsl:when test="$componentPropertyURI = 'http://purl.org/linked-data/cube#MeasureProperty'">
                                        <xsl:text>qb:measure</xsl:text>
                                    </xsl:when>
                                    <xsl:when test="$componentPropertyURI = 'http://purl.org/linked-data/cube#AttributeProperty'">
                                        <xsl:text>qb:attribute</xsl:text>
                                    </xsl:when>
                                    <xsl:otherwise>
<xsl:message>FIXME-ii--------<xsl:value-of select="$dataElement"/></xsl:message>
                                        <xsl:text>qb:FIXME-ii--------</xsl:text>
                                    </xsl:otherwise>
                                </xsl:choose>
                            </xsl:variable>

                            <xsl:element name="{$componentProperty}">
                                <xsl:attribute name="rdf:resource" select="$resourceDescriptionProperty"/>
                            </xsl:element>
                        </qb:ComponentSpecification>
                    </qb:component>
                </qb:DataStructureDefinition>
            </xsl:if>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
