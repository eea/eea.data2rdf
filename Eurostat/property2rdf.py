#!/usr/bin/python
import csv, codecs, sys
import zipfile, time, os
from cStringIO import StringIO
from rdfdocument import RdfDocument


class PropReader(object):

    def __init__(self, tsvfile, config, rdfout):
        """ datastream expects a file descriptor with the content in UTF-8 encoding
        """
        self.baseuri = config.get('rdf', 'baseuri')
        self.rdfout = rdfout
        self.timeOfRun = time.strftime("%Y-%m-%dT%H:%M:%S")
        reader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
        self.rdfout.writeHeader(self.baseuri)
        self.rdfout.writeProvenance("property.rdf", "dic/en/dimlst.dic")
        for row in reader:
            if len(row) == 0: continue    # Found an empty line
            code = row[0].lower().strip()
            if code == "": continue       # Found an empty code
            self.rdfout.writeStartResource("rdf:Property", "property#%s" % code)
            self.rdfout.writeDataProperty("rdfs:label", row[1].strip())
            self.rdfout.writeEndResource("rdf:Property")
        self.rdfout.writeFinish()


def buildProperty(config):
    dimLstFN = "en/dimlst.dic"
    website = config.get('destination', 'schema')
    zfd = zipfile.ZipFile("all_dic.zip")

    #Check the timestamp on en/dimlst.dic
    rdfFileName = website + "/" + "property.rdf"
    try: lastRun = os.stat(rdfFileName).st_mtime
    except: lastRun = 0.0
    zi = zfd.getinfo(dimLstFN)
    buildTime = time.mktime(zi.date_time + (0,1,-1))
    if buildTime < lastRun:
        print "%s newer than %s" % (rdfFileName, time.strftime("%Y-%m-%d", time.localtime(buildTime)))
        zfd.close()
        return
    print "Building %s" % rdfFileName
    winfile = StringIO(zfd.read(dimLstFN))
    tsvfile = codecs.EncodedFile(winfile, "utf-8", "cp1252")
    rdfout = RdfDocument(config, rdfFileName, compress=False)
    PropReader(tsvfile, config, rdfout)
    tsvfile.close()
    zfd.close()

if __name__ == '__main__':
    import ConfigParser
    config = ConfigParser.SafeConfigParser()
    config.read('eurostat.cfg')
    buildProperty(config)
