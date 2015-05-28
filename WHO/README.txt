CONVERSION OF WHO DATASETS TO RDF
=================================

Sources are at https://svn.eionet.europa.eu/repositories/EEA/trunk/Data2RDF/WHO


The stylesheet ghodata2rdf.xsl will convert these files to Cube RDF.

The file http://apps.who.int/gho/athena/data/ contains a list of WHO's standard code lists.

  wget -O dimension.xml http://apps.who.int/gho/athena/data/

Each list (like COUNTRY) can then be downloaded as:

  wget http://apps.who.int/gho/athena/api/COUNTRY.xml

You can use the dim2rdf.xsl to convert the dimensions to SKOS concept schemes.

You get the list of available datasets with:

  wget http://apps.who.int/gho/athena/api/GHO.xml

Each dataset can be downloaded with:

  wget http://apps.who.int/gho/athena/api/GHO/AIR_1.xml

Those file have a schema identifer called ghodata.xsd.

Finally, you can use gho2void.xsl on GHO.xml to create
a VoID file of datasets.
