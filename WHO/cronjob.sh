#!/usr/bin/sh
cd /var/local/Data2RDF/WHO

(cd xmldata ;  ls -1rt *.xml | head -10 | xargs -d '\n' rm -f )

python downloaddatasets.py

python ghodata2rdf.py

python gho2void.py
