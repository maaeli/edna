#
#    Project: CCP4v0
#             http://www.edna-site.org
#
#    File: "$Id: generateXSDataCCP4v0.sh,v 1.1.1.1 2010/03/10 10:37:47 gxy38 Exp $"
#
#    Copyright (C) 2010 CCP4
#
#
#    Principal authors: The CCP4 development team
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    and the GNU Lesser General Public License  along with this program.  
#    If not, see <http://www.gnu.org/licenses/>.
#


full_path="$(cd "${0%/*}" 2>/dev/null; echo "$PWD"/"${0##*/}")"
export EDNA_HOME=`dirname "$full_path" | sed 's/\/dimplev0\/datamodel$//'`

xsDataBaseName=XSDataCCP4DIMPLE
xsdHomeDir=${EDNA_HOME}/dimplev0/datamodel
pyHomeDir=${EDNA_HOME}/dimplev0/src
includeXSDFilePath=${EDNA_HOME}/kernel/datamodel/XSDataCommon.xsd

sh ${EDNA_HOME}/kernel/datamodel/generateDataBinding.sh ${xsDataBaseName} ${xsdHomeDir} ${pyHomeDir} ${includeXSDFilePath} 
