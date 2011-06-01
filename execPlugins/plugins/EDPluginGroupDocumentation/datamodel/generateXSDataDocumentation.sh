#!/bin/sh
#
#    Project: The EDNA Archive Project
#             http://www.edna-site.org
#
#    File: "$Id:$"
#
#    Copyright (C) ESRF
#
#    Principal author:       Jerome Kieffer
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


if [ -z "$EDNA_HOME" ]; then
#	This cryptic version is kept in case of need ... showed to be useful for MacOSX users
#	full_path="$(cd "${0%/*}" 2>/dev/null; echo "$PWD"/"${0##*/}")"
	full_path=$( readlink -fn $0)
	export EDNA_HOME=`dirname "$full_path" | sed 's/\/execPlugins\/.*\/datamodel$//'`
	echo "Guessing EDNA_HOME= "$EDNA_HOME
fi

xsDataBaseName=XSDataDocumentation.edml
xsDataBaseDir=EDPluginGroupDocumentation
xsdHomeDir=${EDNA_HOME}/execPlugins/plugins/${xsDataBaseDir}/datamodel
pyHomeDir=${EDNA_HOME}/execPlugins/plugins/${xsDataBaseDir}/plugins
includeXSDFilePath=${EDNA_HOME}/kernel/datamodel

java -jar ${EDNA_HOME}/kernel/datamodel/EDGenerateDS.jar
echo java -jar ${EDNA_HOME}/kernel/datamodel/EDGenerateDS.jar -includepaths ${includeXSDFilePath},${xsdHomeDir} -source ${xsdHomeDir}/${xsDataBaseName}  -targetdir ${pyHomeDir}

java -jar ${EDNA_HOME}/kernel/datamodel/EDGenerateDS.jar -includepaths ${includeXSDFilePath},${xsdHomeDir} -source ${xsdHomeDir}/${xsDataBaseName}  -targetdir ${pyHomeDir}
