#!/usr/bin/python
# -*- coding: utf-8 -*-
# Copyright (C) 2012 Søren Roug, European Environment Agency
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

import logging, os, time
from toclabels import datasetLabels
import sdmx2rdf, downloadsdmx, toclabels
import urllib



def pingDatabases(config, dataset):
    """ Sends a request to data stores as a signal to get them to reharvest
        the new RDF data.
    """
    baseuri = config.get('rdf', 'baseuri')
    urls = config.get('ping', 'stores', {'dataset': dataset, 'baseuri': baseuri})
    urllist = urls.split()
    for link in urllist:
        f = urllib.urlopen(link)
        f.read()
        f.close()


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

    # Download the TOC
    downloadsdmx.downloadTOC(config)
    # Get the titles of the datasets
    dsLabels = toclabels.datasetLabels()

    # Get a list of files to download. Datasets to skip have been excluded.
    toDownload = downloadsdmx.listNewDatasets(config)

    # For each dataset, download and then convert
    failures = 0
    for ds in toDownload:
        try:
            code, link, filename, lastModified = ds
            logging.info("Retrieving %s last updated %s" , code, time.strftime("%Y-%m-%d", lastModified))
            downloadsdmx.downloadSDMX(link, filename)
            label = dsLabels.get(code, code)
            sdmx2rdf.buildIfOlder(config, code, label)
        except KeyboardInterrupt:
            raise
        except:
            failures += 1
            logging.error("Failed to download: %s", filename)
    if failures > 0:
        logging.warning("Failed: %s", failures)
