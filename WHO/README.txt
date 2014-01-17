CONVERSION OF WHO DATASETS TO RDF
================================

Sources are at https://svn.eionet.europa.eu/repositories/EEA/trunk/Data2RDF/WHO

Files at WHO like http://apps.who.int/athena/data/GHO/AIR_1.xml
have a schema identifer called ghodata.xsd.

The stylesheet ghodata2rdf.xsl will convert these files to Cube RDF.

The file http://apps.who.int/gho/athena/data/ contains a list of WHO's standard code lists.

  wget -O dimension.xml http://apps.who.int/gho/athena/data/

Each list (like COUNTRY) can then be downloaded as:

  http://apps.who.int/athena/metadata/dimension/COUNTRY.xml

You can use the dim2rdf.xsl to convert the dimensions to SKOS concept schemes.

Finally, you can use gho2void.xsl on http://apps.who.int/athena/metadata/dimension/GHO.xml to create
a VoID file of datasets.
