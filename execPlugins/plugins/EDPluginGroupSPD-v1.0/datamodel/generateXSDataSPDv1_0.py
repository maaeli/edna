#!/usr/bin/env python
# coding: utf8 
#
#    Project: ExecPlugins/SPD
#             http://www.edna-site.org
#
#    File: "$Id:$"
#
#    Copyright (C) 2011, ESRF, Grenoble
#
#    Principal author:       Jérôme Kieffer
#
#    Contributing authors:   
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
import os, sys

xsDataName = "XSDataSPDv1_0.edml"

if "EDNA_HOME" not in os.environ:
    full_path = os.path.abspath(sys.argv[0])
    while True:
        old_path = full_path
        full_path = os.path.dirname(old_path)
        if old_path == full_path:
            print("Something weird is happening: I did not find the EDNA_ROOT !!!")
            sys.exit(1)
        if  os.path.isdir(os.path.join(full_path, "kernel", "datamodel")):
            EDNA_HOME = full_path
            os.environ["EDNA_HOME"] = full_path
            break
else:
    EDNA_HOME = os.environ["EDNA_HOME"]

xsdHomeDir = os.path.dirname(os.path.abspath(sys.argv[0]))
xsdFilePath = os.path.join(xsdHomeDir, xsDataName)
pyHomeDir = os.path.join(os.path.dirname(xsdHomeDir), "plugins")
includeXSDFilePath = os.path.join(EDNA_HOME, "kernel", "datamodel")
jar = os.path.join(includeXSDFilePath, "EDGenerateDS.jar")
os.system("java -jar %s -includepaths %s,%s -source %s -targetdir %s" % (jar, includeXSDFilePath, xsdHomeDir, xsdFilePath, pyHomeDir))

