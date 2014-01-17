#!/usr/bin/python
import os, sys
import gzip

thisdir = os.listdir(sys.argv[1])
outputfile = open(sys.argv[2],'w')
outputfile.write('''<indicators>\n''')

for xmlfile in thisdir:
    if xmlfile[-7:] == '.xml.gz':
        f = gzip.open(sys.argv[1] + xmlfile)
        f.readline() # XML prologue
        head = f.readline()
        segs = head.split('"')
        f.close()
        if len(segs) == 11 and segs[6] == ' total=':
            outputfile.write('''<i name="%s" total="%s" pages="%s"/>\n''' % (xmlfile[:-7], segs[7], segs[3]))
#       else:
#           outputfile.write('''<i name="%s" NOTOTAL="1"/>\n''' % xmlfile[:-7])

outputfile.write('''</indicators>\n''')
outputfile.close()
