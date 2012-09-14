#
#    Project: The EDNA Kernel
#             http://www.edna-site.org
#
#    Copyright (C) 2008-2012 European Synchrotron Radiation Facility
#                            Grenoble, France
#
#    Principal authors: Marie-Francoise Incardona (incardon@esrf.fr)
#                       Olof Svensson (svensson@esrf.fr) 
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


__authors__ = [ "Marie-Francoise Incardona", "Olof Svensson" ]
__contact__ = "svensson@esrf.fr"
__license__ = "LGPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"

"""
This class handles the EDNA configuration XML files.
"""

import os

from EDLogging import EDLogging
from EDVerbose import EDVerbose
from EDUtilsFile import EDUtilsFile
from EDUtilsPath import EDUtilsPath
from EDFactoryPluginStatic import EDFactoryPluginStatic
from EDThreading            import Semaphore

from XSDataCommon import XSConfiguration

class EDConfiguration(EDLogging):
    """
    This class handles the EDNA configuration XML files. The structure of
    the XML is described in the XSDataCommon data model.
    
    If environment variable strings like "$XXX" or "${XXX}" is present in the
    configuration file, the strings are replaced with the corresponding
    environment variable content. For example, if "${CCP4} is present in the
    XML string, the string "${CCP4}" is replaced by the environment variable $CCP4
    content.
    """


    def __init__(self, _strXMLFileName = None):
        """"Set  up semaphore for thread safeness and dictionary for config files"""
        EDLogging.__init__(self)
        self.__semaphore = Semaphore()
        self.__dictXSConfiguration = {}
        self.__dictPluginConfiguration = {}
        if _strXMLFileName is not None:
            self.addConfigurationFile(_strXMLFileName)
            
    
    def addConfigurationFile(self, _strXMLFileName, _bReplace = True):
        """Loads an XML config file into the dictionary if not already loaded"""
        strXMLFileName = os.path.abspath(_strXMLFileName)
        if not os.path.exists(strXMLFileName):
            self.WARNING("Trying to add configuration file but file %s doesn't exist!" % _strXMLFileName)
        else:
            if strXMLFileName in self.__dictXSConfiguration.keys():
                self.DEBUG("EDConfiguration.addConfigurationFile: File %s already parsed, in cache" % strXMLFileName)
            else:
                self.DEBUG("EDConfiguration.addConfigurationFile: Parsing file %s" % strXMLFileName)
                strXMLConfiguration = EDUtilsFile.readFileAndParseVariables(strXMLFileName)
                xsConfiguration = XSConfiguration.parseString(strXMLConfiguration)
                # Make sure we are thread safe when manipulating the cache
                with self.__semaphore:
                    self.__dictXSConfiguration[strXMLFileName] = xsConfiguration
                # First look for configuration imports
                for xsImportConfiguration in xsConfiguration.XSImportConfiguration:
                    if xsImportConfiguration.directory is None or xsImportConfiguration.directory == "None":
                        strImportPath = os.path.join(os.path.dirname(strXMLFileName), xsImportConfiguration.name+".xml")
                    else:
                        strImportPath = os.path.join(xsImportConfiguration.directory, xsImportConfiguration.name+".xml")
                    self.DEBUG("Importing configuration file : %s" % strImportPath)
                    self.addConfigurationFile(strImportPath, True)
                # Make sure we are thread safe when manipulating the cache
                with self.__semaphore:
                    # Load configurations into the plugin dictionary
                    for xsPluginItem in xsConfiguration.XSPluginList.XSPluginItem:
                        strPluginName = xsPluginItem.name
                        if strPluginName in self.__dictPluginConfiguration:
                            if _bReplace:
                                self.DEBUG("EDConfiguration.addConfigurationFile: plugin configuration for %s already exists and is replaced." % strPluginName)                                
                            else:
                                self.DEBUG("EDConfiguration.addConfigurationFile: plugin configuration for %s already exists and will not be replaced." % strPluginName)
                        else:
                            self.DEBUG("EDConfiguration.addConfigurationFile: adding plugin configuration for %s." % strPluginName)
                            self.__dictPluginConfiguration[strPluginName] = xsPluginItem                        
        
    
    def getXSConfigurationItem(self, _strPluginName):
        xsConfigurationItem = None
        # First check plugin dictionary:
        if _strPluginName in self.__dictPluginConfiguration.keys():
            xsConfigurationItem = self.__dictPluginConfiguration[_strPluginName]
        else:
            # Try to load "project" configuration
            strPathToProjectConfigurationFile = EDFactoryPluginStatic.getPathToProjectConfigurationFile(_strPluginName)
            if strPathToProjectConfigurationFile is not None:
                self.addConfigurationFile(strPathToProjectConfigurationFile, _bReplace=False)
                if _strPluginName in self.__dictPluginConfiguration.keys():
                    xsConfigurationItem = self.__dictPluginConfiguration[_strPluginName]
        return xsConfigurationItem
        
    
    def setXSConfigurationItem(self, _xsPluginItem):
        if _xsPluginItem is not None:
            if _xsPluginItem.name is not None:
                strPluginName = _xsPluginItem.name
                if strPluginName in self.__dictPluginConfiguration.keys():
                    self.DEBUG("Replacing configuration for plugin %s" % strPluginName)
                else:
                    self.DEBUG("Setting configuration for plugin %s" % strPluginName)
                with self.__semaphore:
                    self.__dictPluginConfiguration[strPluginName] = _xsPluginItem


    def getStringValue(self,  _strConfigurationName, _strPluginName ):
        strValue = None
        xsPluginItem = self.getXSConfigurationItem(_strPluginName)
        if xsPluginItem is not None:
            xsParamList = xsPluginItem.getXSParamList()
            xsParamItems = xsParamList.getXSParamItem()
            for xsParamItem in xsParamItems:
                if (xsParamItem.getName() == _strConfigurationName):
                    strValue = xsParamItem.value
        return strValue

    def getStringParamValue(_xsPluginItem, _pyStrParamName):
        """
        Returns the parameter value in a string format
        """
        xsParamList = _xsPluginItem.getXSParamList()
        paramValue = None

        if (xsParamList != None):
            xsParamItems = xsParamList.getXSParamItem()
            for xsParamItem in xsParamItems:
                if (xsParamItem.getName() == _pyStrParamName):
                    paramValue = xsParamItem.getValue()
        return paramValue
    getStringParamValue = staticmethod(getStringParamValue)


    def getIntegerParamValue(_xsPluginItem, _pyStrParamName):
        """
        Returns the parameter value in a integer format
        """
        strParamValue = EDConfiguration.getStringParamValue(_xsPluginItem, _pyStrParamName)
        intParamValue = None
        if strParamValue is not None:
            intParamValue = int(strParamValue)
        return intParamValue
    getIntegerParamValue = staticmethod(getIntegerParamValue)


    def getPluginListSize(self):
        """
        Returns the size of the XSPluginItem list
        """
        iSize = len(self.getPluginList().getXSPluginItem())
        return iSize
