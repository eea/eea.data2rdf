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

import sys, zipfile, os, logging


def loadDatasetLabels():
    """ Read the dataset titles from the downloaded all_dic.zip
        The titles are in the file en/table_dic.dic
        The file is not complete
    """
    datasets = {}
    zfd = zipfile.ZipFile("all_dic.zip")
    winfile = StringIO(zfd.read("en/table_dic.dic"))
    tsvfile = codecs.EncodedFile(winfile, "utf-8", "cp1252")
    reader = csv.reader(tsvfile, delimiter='\t', quoting=csv.QUOTE_NONE)
    for row in reader:
        if len(row) == 0: continue    # Found an empty line
        code = row[0].lower().strip()
        if code == "": continue       # Found an empty code
        datasets[code] = row[1].strip()
    tsvfile.close()
    zfd.close()
    return datasets

if __name__ == '__main__':
    import ConfigParser, getopt
    from toclabels import datasetLabels
    config = ConfigParser.SafeConfigParser()
    config.read('eurostat.cfg')
    repository = config.get('sources','sdmxfiles')

    try:
        opts, args = getopt.getopt(sys.argv[1:], "v")
    except getopt.GetoptError, err:
        sys.exit(2)
    for o, a in opts:
        if o == "-v":
            logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    for dataset in args:
        if dataset[-9:] == '.sdmx.zip': dataset = dataset[:-9]
        print "Contents of:", dataset
        sdmxname = repository + "/" + dataset + ".sdmx.zip"
        zfd = zipfile.ZipFile(sdmxname)
        for name in zfd.namelist():
            print " ", name
        zfd.close()
