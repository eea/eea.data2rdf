#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2014 Søren Roug, European Environment Agency
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2.1 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
#
# Contributor(s):
#

import logging, os, time, sys, fnmatch
from toclabels import datasetLabels
import sdmx2rdf, downloadsdmx, toclabels
import urllib

# This program will rebuild all datasets that have not been built after a
# timestamp set in the config file or today's date

def listCachedDatasets(config, candidates = []):
    todownload = []
    try:
        rebuildDate = config.get('rebuild','timestamp')
        dateOfSource = time.mktime(time.strptime(rebuildDate, "%Y-%m-%d %H:%M:%S"))
    except:
        dateOfSource = time.time()

    sources = config.get('sources', 'sdmxfiles')
    for filename in os.listdir(sources):
        if filename[-9:] == ".sdmx.zip" and (len(candidates) == 0 or filename[:-9] in candidates):
            todownload.append( [filename[:-9], "", sources + "/" + filename, dateOfSource] )
    return todownload

def isSkipable(code, skiplist):
    for skip in skiplist:
        if fnmatch.fnmatch(code, skip):
            return True
    return False

if __name__ == '__main__':
    import ConfigParser, getopt, sys
    config = ConfigParser.SafeConfigParser()
    config.read('eurostat.cfg')
    skipline = config.get('rdf','skip')
    skiplist = skipline.split()

    try:
        opts, args = getopt.getopt(sys.argv[1:], "v")
    except getopt.GetoptError, err:
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    toDownload = listCachedDatasets(config, args)

    # Get the titles of the datasets
    dsLabels = toclabels.datasetLabels()

    # For each dataset, convert
    failures = 0
    for ds in toDownload:
        try:
            code, link, filename, lastModified = ds
            if isSkipable(code, skiplist):
                logging.debug("Skipping %s", code)
                continue
            label = dsLabels.get(code, code)
            sdmx2rdf.buildIfRdfIsOlder(config, code, label, lastModified)
        except KeyboardInterrupt:
            raise
        except:
            raise
            failures += 1
            logging.error("Failed to rebuild: %s", filename)
    if failures > 0:
        logging.warning("Failed: %s", failures)
