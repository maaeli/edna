#!/usr/bin/env python

#
# Generated Mon Mar 18 09:22::28 2013 by EDGenerateDS.
#

import os, sys
from xml.dom import minidom
from xml.dom import Node


strEdnaHome = os.environ.get("EDNA_HOME", None)

dictLocation = { \
 "XSDataCommon": "kernel/datamodel", \
 "XSDataEdnaSaxs": "ednaSaxs/datamodel", \
}

try:
    from XSDataCommon import XSData
    from XSDataCommon import XSDataDouble
    from XSDataCommon import XSDataInput
    from XSDataCommon import XSDataInteger
    from XSDataCommon import XSDataString
    from XSDataCommon import XSDataArray
    from XSDataCommon import XSDataBoolean
    from XSDataCommon import XSDataFile
    from XSDataCommon import XSDataResult
    from XSDataEdnaSaxs import XSDataAutoRg
    from XSDataEdnaSaxs import XSDataGnom
except ImportError as error:
    if strEdnaHome is not None:
        for strXsdName in dictLocation:
            strXsdModule = strXsdName + ".py"
            strRootdir = os.path.dirname(os.path.abspath(os.path.join(strEdnaHome, dictLocation[strXsdName])))
            for strRoot, listDirs, listFiles in os.walk(strRootdir):
                if strXsdModule in listFiles:
                    sys.path.append(strRoot)
    else:
        raise error
from XSDataCommon import XSData
from XSDataCommon import XSDataDouble
from XSDataCommon import XSDataInput
from XSDataCommon import XSDataInteger
from XSDataCommon import XSDataString
from XSDataCommon import XSDataArray
from XSDataCommon import XSDataBoolean
from XSDataCommon import XSDataFile
from XSDataCommon import XSDataResult
from XSDataEdnaSaxs import XSDataAutoRg
from XSDataEdnaSaxs import XSDataGnom




#
# Support/utility functions.
#

# Compabiltity between Python 2 and 3:
if sys.version.startswith('3'):
    unicode = str
    from io import StringIO
else:
    from StringIO import StringIO


def showIndent(outfile, level):
    for idx in range(level):
        outfile.write(unicode('    '))


def warnEmptyAttribute(_strName, _strTypeName):
    pass
    #if not _strTypeName in ["float", "double", "string", "boolean", "integer"]:
    #    print("Warning! Non-optional attribute %s of type %s is None!" % (_strName, _strTypeName))

class MixedContainer(object):
    # Constants for category:
    CategoryNone = 0
    CategoryText = 1
    CategorySimple = 2
    CategoryComplex = 3
    # Constants for content_type:
    TypeNone = 0
    TypeText = 1
    TypeString = 2
    TypeInteger = 3
    TypeFloat = 4
    TypeDecimal = 5
    TypeDouble = 6
    TypeBoolean = 7
    def __init__(self, category, content_type, name, value):
        self.category = category
        self.content_type = content_type
        self.name = name
        self.value = value
    def getCategory(self):
        return self.category
    def getContenttype(self, content_type):
        return self.content_type
    def getValue(self):
        return self.value
    def getName(self):
        return self.name
    def export(self, outfile, level, name):
        if self.category == MixedContainer.CategoryText:
            outfile.write(self.value)
        elif self.category == MixedContainer.CategorySimple:
            self.exportSimple(outfile, level, name)
        else:     # category == MixedContainer.CategoryComplex
            self.value.export(outfile, level, name)
    def exportSimple(self, outfile, level, name):
        if self.content_type == MixedContainer.TypeString:
            outfile.write(unicode('<%s>%s</%s>' % (self.name, self.value, self.name)))
        elif self.content_type == MixedContainer.TypeInteger or \
                self.content_type == MixedContainer.TypeBoolean:
            outfile.write(unicode('<%s>%d</%s>' % (self.name, self.value, self.name)))
        elif self.content_type == MixedContainer.TypeFloat or \
                self.content_type == MixedContainer.TypeDecimal:
            outfile.write(unicode('<%s>%f</%s>' % (self.name, self.value, self.name)))
        elif self.content_type == MixedContainer.TypeDouble:
            outfile.write(unicode('<%s>%g</%s>' % (self.name, self.value, self.name)))

#
# Data representation classes.
#



class XSDataSolutionScatteringSettings(XSData):
    def __init__(self, rMaxAbsTol=None, rMaxIntervals=None, rMaxStop=None, rMaxStart=None):
        XSData.__init__(self,)
        if rMaxStart is None:
            self._rMaxStart = None
        elif rMaxStart.__class__.__name__ == "XSDataDouble":
            self._rMaxStart = rMaxStart
        else:
            strMessage = "ERROR! XSDataSolutionScatteringSettings constructor argument 'rMaxStart' is not XSDataDouble but %s" % self._rMaxStart.__class__.__name__
            raise BaseException(strMessage)
        if rMaxStop is None:
            self._rMaxStop = None
        elif rMaxStop.__class__.__name__ == "XSDataDouble":
            self._rMaxStop = rMaxStop
        else:
            strMessage = "ERROR! XSDataSolutionScatteringSettings constructor argument 'rMaxStop' is not XSDataDouble but %s" % self._rMaxStop.__class__.__name__
            raise BaseException(strMessage)
        if rMaxIntervals is None:
            self._rMaxIntervals = None
        elif rMaxIntervals.__class__.__name__ == "XSDataInteger":
            self._rMaxIntervals = rMaxIntervals
        else:
            strMessage = "ERROR! XSDataSolutionScatteringSettings constructor argument 'rMaxIntervals' is not XSDataInteger but %s" % self._rMaxIntervals.__class__.__name__
            raise BaseException(strMessage)
        if rMaxAbsTol is None:
            self._rMaxAbsTol = None
        elif rMaxAbsTol.__class__.__name__ == "XSDataDouble":
            self._rMaxAbsTol = rMaxAbsTol
        else:
            strMessage = "ERROR! XSDataSolutionScatteringSettings constructor argument 'rMaxAbsTol' is not XSDataDouble but %s" % self._rMaxAbsTol.__class__.__name__
            raise BaseException(strMessage)
    # Methods and properties for the 'rMaxStart' attribute
    def getRMaxStart(self): return self._rMaxStart
    def setRMaxStart(self, rMaxStart):
        if rMaxStart is None:
            self._rMaxStart = None
        elif rMaxStart.__class__.__name__ == "XSDataDouble":
            self._rMaxStart = rMaxStart
        else:
            strMessage = "ERROR! XSDataSolutionScatteringSettings.setRMaxStart argument is not XSDataDouble but %s" % rMaxStart.__class__.__name__
            raise BaseException(strMessage)
    def delRMaxStart(self): self._rMaxStart = None
    rMaxStart = property(getRMaxStart, setRMaxStart, delRMaxStart, "Property for rMaxStart")
    # Methods and properties for the 'rMaxStop' attribute
    def getRMaxStop(self): return self._rMaxStop
    def setRMaxStop(self, rMaxStop):
        if rMaxStop is None:
            self._rMaxStop = None
        elif rMaxStop.__class__.__name__ == "XSDataDouble":
            self._rMaxStop = rMaxStop
        else:
            strMessage = "ERROR! XSDataSolutionScatteringSettings.setRMaxStop argument is not XSDataDouble but %s" % rMaxStop.__class__.__name__
            raise BaseException(strMessage)
    def delRMaxStop(self): self._rMaxStop = None
    rMaxStop = property(getRMaxStop, setRMaxStop, delRMaxStop, "Property for rMaxStop")
    # Methods and properties for the 'rMaxIntervals' attribute
    def getRMaxIntervals(self): return self._rMaxIntervals
    def setRMaxIntervals(self, rMaxIntervals):
        if rMaxIntervals is None:
            self._rMaxIntervals = None
        elif rMaxIntervals.__class__.__name__ == "XSDataInteger":
            self._rMaxIntervals = rMaxIntervals
        else:
            strMessage = "ERROR! XSDataSolutionScatteringSettings.setRMaxIntervals argument is not XSDataInteger but %s" % rMaxIntervals.__class__.__name__
            raise BaseException(strMessage)
    def delRMaxIntervals(self): self._rMaxIntervals = None
    rMaxIntervals = property(getRMaxIntervals, setRMaxIntervals, delRMaxIntervals, "Property for rMaxIntervals")
    # Methods and properties for the 'rMaxAbsTol' attribute
    def getRMaxAbsTol(self): return self._rMaxAbsTol
    def setRMaxAbsTol(self, rMaxAbsTol):
        if rMaxAbsTol is None:
            self._rMaxAbsTol = None
        elif rMaxAbsTol.__class__.__name__ == "XSDataDouble":
            self._rMaxAbsTol = rMaxAbsTol
        else:
            strMessage = "ERROR! XSDataSolutionScatteringSettings.setRMaxAbsTol argument is not XSDataDouble but %s" % rMaxAbsTol.__class__.__name__
            raise BaseException(strMessage)
    def delRMaxAbsTol(self): self._rMaxAbsTol = None
    rMaxAbsTol = property(getRMaxAbsTol, setRMaxAbsTol, delRMaxAbsTol, "Property for rMaxAbsTol")
    def export(self, outfile, level, name_='XSDataSolutionScatteringSettings'):
        showIndent(outfile, level)
        outfile.write(unicode('<%s>\n' % name_))
        self.exportChildren(outfile, level + 1, name_)
        showIndent(outfile, level)
        outfile.write(unicode('</%s>\n' % name_))
    def exportChildren(self, outfile, level, name_='XSDataSolutionScatteringSettings'):
        XSData.exportChildren(self, outfile, level, name_)
        if self._rMaxStart is not None:
            self.rMaxStart.export(outfile, level, name_='rMaxStart')
        else:
            warnEmptyAttribute("rMaxStart", "XSDataDouble")
        if self._rMaxStop is not None:
            self.rMaxStop.export(outfile, level, name_='rMaxStop')
        else:
            warnEmptyAttribute("rMaxStop", "XSDataDouble")
        if self._rMaxIntervals is not None:
            self.rMaxIntervals.export(outfile, level, name_='rMaxIntervals')
        else:
            warnEmptyAttribute("rMaxIntervals", "XSDataInteger")
        if self._rMaxAbsTol is not None:
            self.rMaxAbsTol.export(outfile, level, name_='rMaxAbsTol')
        else:
            warnEmptyAttribute("rMaxAbsTol", "XSDataDouble")
    def build(self, node_):
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'rMaxStart':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.setRMaxStart(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'rMaxStop':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.setRMaxStop(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'rMaxIntervals':
            obj_ = XSDataInteger()
            obj_.build(child_)
            self.setRMaxIntervals(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'rMaxAbsTol':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.setRMaxAbsTol(obj_)
        XSData.buildChildren(self, child_, nodeName_)
    #Method for marshalling an object
    def marshal(self):
        oStreamString = StringIO()
        oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
        self.export(oStreamString, 0, name_="XSDataSolutionScatteringSettings")
        oStringXML = oStreamString.getvalue()
        oStreamString.close()
        return oStringXML
    #Only to export the entire XML tree to a file stream on disk
    def exportToFile(self, _outfileName):
        outfile = open(_outfileName, "w")
        outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
        self.export(outfile, 0, name_='XSDataSolutionScatteringSettings')
        outfile.close()
    #Deprecated method, replaced by exportToFile
    def outputFile(self, _outfileName):
        print("WARNING: Method outputFile in class XSDataSolutionScatteringSettings is deprecated, please use instead exportToFile!")
        self.exportToFile(_outfileName)
    #Method for making a copy in a new instance
    def copy(self):
        return XSDataSolutionScatteringSettings.parseString(self.marshal())
    #Static method for parsing a string
    def parseString(_inString):
        doc = minidom.parseString(_inString)
        rootNode = doc.documentElement
        rootObj = XSDataSolutionScatteringSettings()
        rootObj.build(rootNode)
        # Check that all minOccurs are obeyed by marshalling the created object
        oStreamString = StringIO()
        rootObj.export(oStreamString, 0, name_="XSDataSolutionScatteringSettings")
        oStreamString.close()
        return rootObj
    parseString = staticmethod(parseString)
    #Static method for parsing a file
    def parseFile(_inFilePath):
        doc = minidom.parse(_inFilePath)
        rootNode = doc.documentElement
        rootObj = XSDataSolutionScatteringSettings()
        rootObj.build(rootNode)
        return rootObj
    parseFile = staticmethod(parseFile)
# end class XSDataSolutionScatteringSettings


class XSDataInputSolutionScattering(XSDataInput):
    def __init__(self, configuration=None, gnom=None, autorg=None, qMax=None, qMin=None, plotFit=None, onlyGnom=None, iNbThreads=None, mode=None, symmetry=None, angularUnits=None, rMaxSearchSettings=None, experimentalDataFile=None, experimentalDataStdArray=None, experimentalDataStdDev=None, experimentalDataIArray=None, experimentalDataValues=None, experimentalDataQArray=None, experimentalDataQ=None, title=None):
        XSDataInput.__init__(self, configuration)
        if title is None:
            self._title = None
        elif title.__class__.__name__ == "XSDataString":
            self._title = title
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'title' is not XSDataString but %s" % self._title.__class__.__name__
            raise BaseException(strMessage)
        if experimentalDataQ is None:
            self._experimentalDataQ = []
        elif experimentalDataQ.__class__.__name__ == "list":
            self._experimentalDataQ = experimentalDataQ
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'experimentalDataQ' is not list but %s" % self._experimentalDataQ.__class__.__name__
            raise BaseException(strMessage)
        if experimentalDataQArray is None:
            self._experimentalDataQArray = None
        elif experimentalDataQArray.__class__.__name__ == "XSDataArray":
            self._experimentalDataQArray = experimentalDataQArray
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'experimentalDataQArray' is not XSDataArray but %s" % self._experimentalDataQArray.__class__.__name__
            raise BaseException(strMessage)
        if experimentalDataValues is None:
            self._experimentalDataValues = []
        elif experimentalDataValues.__class__.__name__ == "list":
            self._experimentalDataValues = experimentalDataValues
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'experimentalDataValues' is not list but %s" % self._experimentalDataValues.__class__.__name__
            raise BaseException(strMessage)
        if experimentalDataIArray is None:
            self._experimentalDataIArray = None
        elif experimentalDataIArray.__class__.__name__ == "XSDataArray":
            self._experimentalDataIArray = experimentalDataIArray
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'experimentalDataIArray' is not XSDataArray but %s" % self._experimentalDataIArray.__class__.__name__
            raise BaseException(strMessage)
        if experimentalDataStdDev is None:
            self._experimentalDataStdDev = []
        elif experimentalDataStdDev.__class__.__name__ == "list":
            self._experimentalDataStdDev = experimentalDataStdDev
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'experimentalDataStdDev' is not list but %s" % self._experimentalDataStdDev.__class__.__name__
            raise BaseException(strMessage)
        if experimentalDataStdArray is None:
            self._experimentalDataStdArray = None
        elif experimentalDataStdArray.__class__.__name__ == "XSDataArray":
            self._experimentalDataStdArray = experimentalDataStdArray
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'experimentalDataStdArray' is not XSDataArray but %s" % self._experimentalDataStdArray.__class__.__name__
            raise BaseException(strMessage)
        if experimentalDataFile is None:
            self._experimentalDataFile = None
        elif experimentalDataFile.__class__.__name__ == "XSDataFile":
            self._experimentalDataFile = experimentalDataFile
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'experimentalDataFile' is not XSDataFile but %s" % self._experimentalDataFile.__class__.__name__
            raise BaseException(strMessage)
        if rMaxSearchSettings is None:
            self._rMaxSearchSettings = None
        elif rMaxSearchSettings.__class__.__name__ == "XSDataSolutionScatteringSettings":
            self._rMaxSearchSettings = rMaxSearchSettings
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'rMaxSearchSettings' is not XSDataSolutionScatteringSettings but %s" % self._rMaxSearchSettings.__class__.__name__
            raise BaseException(strMessage)
        if angularUnits is None:
            self._angularUnits = None
        elif angularUnits.__class__.__name__ == "XSDataInteger":
            self._angularUnits = angularUnits
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'angularUnits' is not XSDataInteger but %s" % self._angularUnits.__class__.__name__
            raise BaseException(strMessage)
        if symmetry is None:
            self._symmetry = None
        elif symmetry.__class__.__name__ == "XSDataString":
            self._symmetry = symmetry
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'symmetry' is not XSDataString but %s" % self._symmetry.__class__.__name__
            raise BaseException(strMessage)
        if mode is None:
            self._mode = None
        elif mode.__class__.__name__ == "XSDataString":
            self._mode = mode
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'mode' is not XSDataString but %s" % self._mode.__class__.__name__
            raise BaseException(strMessage)
        if iNbThreads is None:
            self._iNbThreads = None
        elif iNbThreads.__class__.__name__ == "XSDataInteger":
            self._iNbThreads = iNbThreads
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'iNbThreads' is not XSDataInteger but %s" % self._iNbThreads.__class__.__name__
            raise BaseException(strMessage)
        if onlyGnom is None:
            self._onlyGnom = None
        elif onlyGnom.__class__.__name__ == "XSDataBoolean":
            self._onlyGnom = onlyGnom
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'onlyGnom' is not XSDataBoolean but %s" % self._onlyGnom.__class__.__name__
            raise BaseException(strMessage)
        if plotFit is None:
            self._plotFit = None
        elif plotFit.__class__.__name__ == "XSDataBoolean":
            self._plotFit = plotFit
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'plotFit' is not XSDataBoolean but %s" % self._plotFit.__class__.__name__
            raise BaseException(strMessage)
        if qMin is None:
            self._qMin = None
        elif qMin.__class__.__name__ == "XSDataDouble":
            self._qMin = qMin
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'qMin' is not XSDataDouble but %s" % self._qMin.__class__.__name__
            raise BaseException(strMessage)
        if qMax is None:
            self._qMax = None
        elif qMax.__class__.__name__ == "XSDataDouble":
            self._qMax = qMax
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'qMax' is not XSDataDouble but %s" % self._qMax.__class__.__name__
            raise BaseException(strMessage)
        if autorg is None:
            self._autorg = None
        elif autorg.__class__.__name__ == "XSDataAutoRg":
            self._autorg = autorg
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'autorg' is not XSDataAutoRg but %s" % self._autorg.__class__.__name__
            raise BaseException(strMessage)
        if gnom is None:
            self._gnom = None
        elif gnom.__class__.__name__ == "XSDataGnom":
            self._gnom = gnom
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering constructor argument 'gnom' is not XSDataGnom but %s" % self._gnom.__class__.__name__
            raise BaseException(strMessage)
    # Methods and properties for the 'title' attribute
    def getTitle(self): return self._title
    def setTitle(self, title):
        if title is None:
            self._title = None
        elif title.__class__.__name__ == "XSDataString":
            self._title = title
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setTitle argument is not XSDataString but %s" % title.__class__.__name__
            raise BaseException(strMessage)
    def delTitle(self): self._title = None
    title = property(getTitle, setTitle, delTitle, "Property for title")
    # Methods and properties for the 'experimentalDataQ' attribute
    def getExperimentalDataQ(self): return self._experimentalDataQ
    def setExperimentalDataQ(self, experimentalDataQ):
        if experimentalDataQ is None:
            self._experimentalDataQ = []
        elif experimentalDataQ.__class__.__name__ == "list":
            self._experimentalDataQ = experimentalDataQ
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setExperimentalDataQ argument is not list but %s" % experimentalDataQ.__class__.__name__
            raise BaseException(strMessage)
    def delExperimentalDataQ(self): self._experimentalDataQ = None
    experimentalDataQ = property(getExperimentalDataQ, setExperimentalDataQ, delExperimentalDataQ, "Property for experimentalDataQ")
    def addExperimentalDataQ(self, value):
        if value is None:
            strMessage = "ERROR! XSDataInputSolutionScattering.addExperimentalDataQ argument is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._experimentalDataQ.append(value)
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.addExperimentalDataQ argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    def insertExperimentalDataQ(self, index, value):
        if index is None:
            strMessage = "ERROR! XSDataInputSolutionScattering.insertExperimentalDataQ argument 'index' is None"
            raise BaseException(strMessage)
        if value is None:
            strMessage = "ERROR! XSDataInputSolutionScattering.insertExperimentalDataQ argument 'value' is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._experimentalDataQ[index] = value
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.addExperimentalDataQ argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    # Methods and properties for the 'experimentalDataQArray' attribute
    def getExperimentalDataQArray(self): return self._experimentalDataQArray
    def setExperimentalDataQArray(self, experimentalDataQArray):
        if experimentalDataQArray is None:
            self._experimentalDataQArray = None
        elif experimentalDataQArray.__class__.__name__ == "XSDataArray":
            self._experimentalDataQArray = experimentalDataQArray
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setExperimentalDataQArray argument is not XSDataArray but %s" % experimentalDataQArray.__class__.__name__
            raise BaseException(strMessage)
    def delExperimentalDataQArray(self): self._experimentalDataQArray = None
    experimentalDataQArray = property(getExperimentalDataQArray, setExperimentalDataQArray, delExperimentalDataQArray, "Property for experimentalDataQArray")
    # Methods and properties for the 'experimentalDataValues' attribute
    def getExperimentalDataValues(self): return self._experimentalDataValues
    def setExperimentalDataValues(self, experimentalDataValues):
        if experimentalDataValues is None:
            self._experimentalDataValues = []
        elif experimentalDataValues.__class__.__name__ == "list":
            self._experimentalDataValues = experimentalDataValues
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setExperimentalDataValues argument is not list but %s" % experimentalDataValues.__class__.__name__
            raise BaseException(strMessage)
    def delExperimentalDataValues(self): self._experimentalDataValues = None
    experimentalDataValues = property(getExperimentalDataValues, setExperimentalDataValues, delExperimentalDataValues, "Property for experimentalDataValues")
    def addExperimentalDataValues(self, value):
        if value is None:
            strMessage = "ERROR! XSDataInputSolutionScattering.addExperimentalDataValues argument is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._experimentalDataValues.append(value)
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.addExperimentalDataValues argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    def insertExperimentalDataValues(self, index, value):
        if index is None:
            strMessage = "ERROR! XSDataInputSolutionScattering.insertExperimentalDataValues argument 'index' is None"
            raise BaseException(strMessage)
        if value is None:
            strMessage = "ERROR! XSDataInputSolutionScattering.insertExperimentalDataValues argument 'value' is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._experimentalDataValues[index] = value
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.addExperimentalDataValues argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    # Methods and properties for the 'experimentalDataIArray' attribute
    def getExperimentalDataIArray(self): return self._experimentalDataIArray
    def setExperimentalDataIArray(self, experimentalDataIArray):
        if experimentalDataIArray is None:
            self._experimentalDataIArray = None
        elif experimentalDataIArray.__class__.__name__ == "XSDataArray":
            self._experimentalDataIArray = experimentalDataIArray
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setExperimentalDataIArray argument is not XSDataArray but %s" % experimentalDataIArray.__class__.__name__
            raise BaseException(strMessage)
    def delExperimentalDataIArray(self): self._experimentalDataIArray = None
    experimentalDataIArray = property(getExperimentalDataIArray, setExperimentalDataIArray, delExperimentalDataIArray, "Property for experimentalDataIArray")
    # Methods and properties for the 'experimentalDataStdDev' attribute
    def getExperimentalDataStdDev(self): return self._experimentalDataStdDev
    def setExperimentalDataStdDev(self, experimentalDataStdDev):
        if experimentalDataStdDev is None:
            self._experimentalDataStdDev = []
        elif experimentalDataStdDev.__class__.__name__ == "list":
            self._experimentalDataStdDev = experimentalDataStdDev
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setExperimentalDataStdDev argument is not list but %s" % experimentalDataStdDev.__class__.__name__
            raise BaseException(strMessage)
    def delExperimentalDataStdDev(self): self._experimentalDataStdDev = None
    experimentalDataStdDev = property(getExperimentalDataStdDev, setExperimentalDataStdDev, delExperimentalDataStdDev, "Property for experimentalDataStdDev")
    def addExperimentalDataStdDev(self, value):
        if value is None:
            strMessage = "ERROR! XSDataInputSolutionScattering.addExperimentalDataStdDev argument is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._experimentalDataStdDev.append(value)
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.addExperimentalDataStdDev argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    def insertExperimentalDataStdDev(self, index, value):
        if index is None:
            strMessage = "ERROR! XSDataInputSolutionScattering.insertExperimentalDataStdDev argument 'index' is None"
            raise BaseException(strMessage)
        if value is None:
            strMessage = "ERROR! XSDataInputSolutionScattering.insertExperimentalDataStdDev argument 'value' is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._experimentalDataStdDev[index] = value
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.addExperimentalDataStdDev argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    # Methods and properties for the 'experimentalDataStdArray' attribute
    def getExperimentalDataStdArray(self): return self._experimentalDataStdArray
    def setExperimentalDataStdArray(self, experimentalDataStdArray):
        if experimentalDataStdArray is None:
            self._experimentalDataStdArray = None
        elif experimentalDataStdArray.__class__.__name__ == "XSDataArray":
            self._experimentalDataStdArray = experimentalDataStdArray
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setExperimentalDataStdArray argument is not XSDataArray but %s" % experimentalDataStdArray.__class__.__name__
            raise BaseException(strMessage)
    def delExperimentalDataStdArray(self): self._experimentalDataStdArray = None
    experimentalDataStdArray = property(getExperimentalDataStdArray, setExperimentalDataStdArray, delExperimentalDataStdArray, "Property for experimentalDataStdArray")
    # Methods and properties for the 'experimentalDataFile' attribute
    def getExperimentalDataFile(self): return self._experimentalDataFile
    def setExperimentalDataFile(self, experimentalDataFile):
        if experimentalDataFile is None:
            self._experimentalDataFile = None
        elif experimentalDataFile.__class__.__name__ == "XSDataFile":
            self._experimentalDataFile = experimentalDataFile
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setExperimentalDataFile argument is not XSDataFile but %s" % experimentalDataFile.__class__.__name__
            raise BaseException(strMessage)
    def delExperimentalDataFile(self): self._experimentalDataFile = None
    experimentalDataFile = property(getExperimentalDataFile, setExperimentalDataFile, delExperimentalDataFile, "Property for experimentalDataFile")
    # Methods and properties for the 'rMaxSearchSettings' attribute
    def getRMaxSearchSettings(self): return self._rMaxSearchSettings
    def setRMaxSearchSettings(self, rMaxSearchSettings):
        if rMaxSearchSettings is None:
            self._rMaxSearchSettings = None
        elif rMaxSearchSettings.__class__.__name__ == "XSDataSolutionScatteringSettings":
            self._rMaxSearchSettings = rMaxSearchSettings
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setRMaxSearchSettings argument is not XSDataSolutionScatteringSettings but %s" % rMaxSearchSettings.__class__.__name__
            raise BaseException(strMessage)
    def delRMaxSearchSettings(self): self._rMaxSearchSettings = None
    rMaxSearchSettings = property(getRMaxSearchSettings, setRMaxSearchSettings, delRMaxSearchSettings, "Property for rMaxSearchSettings")
    # Methods and properties for the 'angularUnits' attribute
    def getAngularUnits(self): return self._angularUnits
    def setAngularUnits(self, angularUnits):
        if angularUnits is None:
            self._angularUnits = None
        elif angularUnits.__class__.__name__ == "XSDataInteger":
            self._angularUnits = angularUnits
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setAngularUnits argument is not XSDataInteger but %s" % angularUnits.__class__.__name__
            raise BaseException(strMessage)
    def delAngularUnits(self): self._angularUnits = None
    angularUnits = property(getAngularUnits, setAngularUnits, delAngularUnits, "Property for angularUnits")
    # Methods and properties for the 'symmetry' attribute
    def getSymmetry(self): return self._symmetry
    def setSymmetry(self, symmetry):
        if symmetry is None:
            self._symmetry = None
        elif symmetry.__class__.__name__ == "XSDataString":
            self._symmetry = symmetry
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setSymmetry argument is not XSDataString but %s" % symmetry.__class__.__name__
            raise BaseException(strMessage)
    def delSymmetry(self): self._symmetry = None
    symmetry = property(getSymmetry, setSymmetry, delSymmetry, "Property for symmetry")
    # Methods and properties for the 'mode' attribute
    def getMode(self): return self._mode
    def setMode(self, mode):
        if mode is None:
            self._mode = None
        elif mode.__class__.__name__ == "XSDataString":
            self._mode = mode
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setMode argument is not XSDataString but %s" % mode.__class__.__name__
            raise BaseException(strMessage)
    def delMode(self): self._mode = None
    mode = property(getMode, setMode, delMode, "Property for mode")
    # Methods and properties for the 'iNbThreads' attribute
    def getINbThreads(self): return self._iNbThreads
    def setINbThreads(self, iNbThreads):
        if iNbThreads is None:
            self._iNbThreads = None
        elif iNbThreads.__class__.__name__ == "XSDataInteger":
            self._iNbThreads = iNbThreads
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setINbThreads argument is not XSDataInteger but %s" % iNbThreads.__class__.__name__
            raise BaseException(strMessage)
    def delINbThreads(self): self._iNbThreads = None
    iNbThreads = property(getINbThreads, setINbThreads, delINbThreads, "Property for iNbThreads")
    # Methods and properties for the 'onlyGnom' attribute
    def getOnlyGnom(self): return self._onlyGnom
    def setOnlyGnom(self, onlyGnom):
        if onlyGnom is None:
            self._onlyGnom = None
        elif onlyGnom.__class__.__name__ == "XSDataBoolean":
            self._onlyGnom = onlyGnom
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setOnlyGnom argument is not XSDataBoolean but %s" % onlyGnom.__class__.__name__
            raise BaseException(strMessage)
    def delOnlyGnom(self): self._onlyGnom = None
    onlyGnom = property(getOnlyGnom, setOnlyGnom, delOnlyGnom, "Property for onlyGnom")
    # Methods and properties for the 'plotFit' attribute
    def getPlotFit(self): return self._plotFit
    def setPlotFit(self, plotFit):
        if plotFit is None:
            self._plotFit = None
        elif plotFit.__class__.__name__ == "XSDataBoolean":
            self._plotFit = plotFit
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setPlotFit argument is not XSDataBoolean but %s" % plotFit.__class__.__name__
            raise BaseException(strMessage)
    def delPlotFit(self): self._plotFit = None
    plotFit = property(getPlotFit, setPlotFit, delPlotFit, "Property for plotFit")
    # Methods and properties for the 'qMin' attribute
    def getQMin(self): return self._qMin
    def setQMin(self, qMin):
        if qMin is None:
            self._qMin = None
        elif qMin.__class__.__name__ == "XSDataDouble":
            self._qMin = qMin
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setQMin argument is not XSDataDouble but %s" % qMin.__class__.__name__
            raise BaseException(strMessage)
    def delQMin(self): self._qMin = None
    qMin = property(getQMin, setQMin, delQMin, "Property for qMin")
    # Methods and properties for the 'qMax' attribute
    def getQMax(self): return self._qMax
    def setQMax(self, qMax):
        if qMax is None:
            self._qMax = None
        elif qMax.__class__.__name__ == "XSDataDouble":
            self._qMax = qMax
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setQMax argument is not XSDataDouble but %s" % qMax.__class__.__name__
            raise BaseException(strMessage)
    def delQMax(self): self._qMax = None
    qMax = property(getQMax, setQMax, delQMax, "Property for qMax")
    # Methods and properties for the 'autorg' attribute
    def getAutorg(self): return self._autorg
    def setAutorg(self, autorg):
        if autorg is None:
            self._autorg = None
        elif autorg.__class__.__name__ == "XSDataAutoRg":
            self._autorg = autorg
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setAutorg argument is not XSDataAutoRg but %s" % autorg.__class__.__name__
            raise BaseException(strMessage)
    def delAutorg(self): self._autorg = None
    autorg = property(getAutorg, setAutorg, delAutorg, "Property for autorg")
    # Methods and properties for the 'gnom' attribute
    def getGnom(self): return self._gnom
    def setGnom(self, gnom):
        if gnom is None:
            self._gnom = None
        elif gnom.__class__.__name__ == "XSDataGnom":
            self._gnom = gnom
        else:
            strMessage = "ERROR! XSDataInputSolutionScattering.setGnom argument is not XSDataGnom but %s" % gnom.__class__.__name__
            raise BaseException(strMessage)
    def delGnom(self): self._gnom = None
    gnom = property(getGnom, setGnom, delGnom, "Property for gnom")
    def export(self, outfile, level, name_='XSDataInputSolutionScattering'):
        showIndent(outfile, level)
        outfile.write(unicode('<%s>\n' % name_))
        self.exportChildren(outfile, level + 1, name_)
        showIndent(outfile, level)
        outfile.write(unicode('</%s>\n' % name_))
    def exportChildren(self, outfile, level, name_='XSDataInputSolutionScattering'):
        XSDataInput.exportChildren(self, outfile, level, name_)
        if self._title is not None:
            self.title.export(outfile, level, name_='title')
        for experimentalDataQ_ in self.getExperimentalDataQ():
            experimentalDataQ_.export(outfile, level, name_='experimentalDataQ')
        if self._experimentalDataQArray is not None:
            self.experimentalDataQArray.export(outfile, level, name_='experimentalDataQArray')
        for experimentalDataValues_ in self.getExperimentalDataValues():
            experimentalDataValues_.export(outfile, level, name_='experimentalDataValues')
        if self._experimentalDataIArray is not None:
            self.experimentalDataIArray.export(outfile, level, name_='experimentalDataIArray')
        for experimentalDataStdDev_ in self.getExperimentalDataStdDev():
            experimentalDataStdDev_.export(outfile, level, name_='experimentalDataStdDev')
        if self._experimentalDataStdArray is not None:
            self.experimentalDataStdArray.export(outfile, level, name_='experimentalDataStdArray')
        if self._experimentalDataFile is not None:
            self.experimentalDataFile.export(outfile, level, name_='experimentalDataFile')
        if self._rMaxSearchSettings is not None:
            self.rMaxSearchSettings.export(outfile, level, name_='rMaxSearchSettings')
        if self._angularUnits is not None:
            self.angularUnits.export(outfile, level, name_='angularUnits')
        if self._symmetry is not None:
            self.symmetry.export(outfile, level, name_='symmetry')
        if self._mode is not None:
            self.mode.export(outfile, level, name_='mode')
        if self._iNbThreads is not None:
            self.iNbThreads.export(outfile, level, name_='iNbThreads')
        if self._onlyGnom is not None:
            self.onlyGnom.export(outfile, level, name_='onlyGnom')
        if self._plotFit is not None:
            self.plotFit.export(outfile, level, name_='plotFit')
        if self._qMin is not None:
            self.qMin.export(outfile, level, name_='qMin')
        if self._qMax is not None:
            self.qMax.export(outfile, level, name_='qMax')
        if self._autorg is not None:
            self.autorg.export(outfile, level, name_='autorg')
        if self._gnom is not None:
            self.gnom.export(outfile, level, name_='gnom')
    def build(self, node_):
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'title':
            obj_ = XSDataString()
            obj_.build(child_)
            self.setTitle(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'experimentalDataQ':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.experimentalDataQ.append(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'experimentalDataQArray':
            obj_ = XSDataArray()
            obj_.build(child_)
            self.setExperimentalDataQArray(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'experimentalDataValues':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.experimentalDataValues.append(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'experimentalDataIArray':
            obj_ = XSDataArray()
            obj_.build(child_)
            self.setExperimentalDataIArray(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'experimentalDataStdDev':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.experimentalDataStdDev.append(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'experimentalDataStdArray':
            obj_ = XSDataArray()
            obj_.build(child_)
            self.setExperimentalDataStdArray(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'experimentalDataFile':
            obj_ = XSDataFile()
            obj_.build(child_)
            self.setExperimentalDataFile(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'rMaxSearchSettings':
            obj_ = XSDataSolutionScatteringSettings()
            obj_.build(child_)
            self.setRMaxSearchSettings(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'angularUnits':
            obj_ = XSDataInteger()
            obj_.build(child_)
            self.setAngularUnits(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'symmetry':
            obj_ = XSDataString()
            obj_.build(child_)
            self.setSymmetry(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'mode':
            obj_ = XSDataString()
            obj_.build(child_)
            self.setMode(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'iNbThreads':
            obj_ = XSDataInteger()
            obj_.build(child_)
            self.setINbThreads(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'onlyGnom':
            obj_ = XSDataBoolean()
            obj_.build(child_)
            self.setOnlyGnom(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'plotFit':
            obj_ = XSDataBoolean()
            obj_.build(child_)
            self.setPlotFit(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'qMin':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.setQMin(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'qMax':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.setQMax(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'autorg':
            obj_ = XSDataAutoRg()
            obj_.build(child_)
            self.setAutorg(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'gnom':
            obj_ = XSDataGnom()
            obj_.build(child_)
            self.setGnom(obj_)
        XSDataInput.buildChildren(self, child_, nodeName_)
    #Method for marshalling an object
    def marshal(self):
        oStreamString = StringIO()
        oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
        self.export(oStreamString, 0, name_="XSDataInputSolutionScattering")
        oStringXML = oStreamString.getvalue()
        oStreamString.close()
        return oStringXML
    #Only to export the entire XML tree to a file stream on disk
    def exportToFile(self, _outfileName):
        outfile = open(_outfileName, "w")
        outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
        self.export(outfile, 0, name_='XSDataInputSolutionScattering')
        outfile.close()
    #Deprecated method, replaced by exportToFile
    def outputFile(self, _outfileName):
        print("WARNING: Method outputFile in class XSDataInputSolutionScattering is deprecated, please use instead exportToFile!")
        self.exportToFile(_outfileName)
    #Method for making a copy in a new instance
    def copy(self):
        return XSDataInputSolutionScattering.parseString(self.marshal())
    #Static method for parsing a string
    def parseString(_inString):
        doc = minidom.parseString(_inString)
        rootNode = doc.documentElement
        rootObj = XSDataInputSolutionScattering()
        rootObj.build(rootNode)
        # Check that all minOccurs are obeyed by marshalling the created object
        oStreamString = StringIO()
        rootObj.export(oStreamString, 0, name_="XSDataInputSolutionScattering")
        oStreamString.close()
        return rootObj
    parseString = staticmethod(parseString)
    #Static method for parsing a file
    def parseFile(_inFilePath):
        doc = minidom.parse(_inFilePath)
        rootNode = doc.documentElement
        rootObj = XSDataInputSolutionScattering()
        rootObj.build(rootNode)
        return rootObj
    parseFile = staticmethod(parseFile)
# end class XSDataInputSolutionScattering


class XSDataResultSolutionScattering(XSDataResult):
    def __init__(self, status=None, kratkyPlot=None, guinierPlot=None, scatterPlot=None, variationNSD=None, meanNSD=None, scatteringFitIarray=None, scatteringFitQArray=None, scatteringFitValues=None, scatteringFitQ=None, pdbSolventFile=None, pdbMoleculeFile=None, logFile=None, lineProfileFitQuality=None, fitFile=None, corelationFitValues=None):
        XSDataResult.__init__(self, status)
        if corelationFitValues is None:
            self._corelationFitValues = []
        elif corelationFitValues.__class__.__name__ == "list":
            self._corelationFitValues = corelationFitValues
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'corelationFitValues' is not list but %s" % self._corelationFitValues.__class__.__name__
            raise BaseException(strMessage)
        if fitFile is None:
            self._fitFile = None
        elif fitFile.__class__.__name__ == "XSDataFile":
            self._fitFile = fitFile
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'fitFile' is not XSDataFile but %s" % self._fitFile.__class__.__name__
            raise BaseException(strMessage)
        if lineProfileFitQuality is None:
            self._lineProfileFitQuality = None
        elif lineProfileFitQuality.__class__.__name__ == "XSDataDouble":
            self._lineProfileFitQuality = lineProfileFitQuality
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'lineProfileFitQuality' is not XSDataDouble but %s" % self._lineProfileFitQuality.__class__.__name__
            raise BaseException(strMessage)
        if logFile is None:
            self._logFile = None
        elif logFile.__class__.__name__ == "XSDataFile":
            self._logFile = logFile
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'logFile' is not XSDataFile but %s" % self._logFile.__class__.__name__
            raise BaseException(strMessage)
        if pdbMoleculeFile is None:
            self._pdbMoleculeFile = None
        elif pdbMoleculeFile.__class__.__name__ == "XSDataFile":
            self._pdbMoleculeFile = pdbMoleculeFile
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'pdbMoleculeFile' is not XSDataFile but %s" % self._pdbMoleculeFile.__class__.__name__
            raise BaseException(strMessage)
        if pdbSolventFile is None:
            self._pdbSolventFile = None
        elif pdbSolventFile.__class__.__name__ == "XSDataFile":
            self._pdbSolventFile = pdbSolventFile
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'pdbSolventFile' is not XSDataFile but %s" % self._pdbSolventFile.__class__.__name__
            raise BaseException(strMessage)
        if scatteringFitQ is None:
            self._scatteringFitQ = []
        elif scatteringFitQ.__class__.__name__ == "list":
            self._scatteringFitQ = scatteringFitQ
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'scatteringFitQ' is not list but %s" % self._scatteringFitQ.__class__.__name__
            raise BaseException(strMessage)
        if scatteringFitValues is None:
            self._scatteringFitValues = []
        elif scatteringFitValues.__class__.__name__ == "list":
            self._scatteringFitValues = scatteringFitValues
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'scatteringFitValues' is not list but %s" % self._scatteringFitValues.__class__.__name__
            raise BaseException(strMessage)
        if scatteringFitQArray is None:
            self._scatteringFitQArray = None
        elif scatteringFitQArray.__class__.__name__ == "XSDataArray":
            self._scatteringFitQArray = scatteringFitQArray
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'scatteringFitQArray' is not XSDataArray but %s" % self._scatteringFitQArray.__class__.__name__
            raise BaseException(strMessage)
        if scatteringFitIarray is None:
            self._scatteringFitIarray = None
        elif scatteringFitIarray.__class__.__name__ == "XSDataArray":
            self._scatteringFitIarray = scatteringFitIarray
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'scatteringFitIarray' is not XSDataArray but %s" % self._scatteringFitIarray.__class__.__name__
            raise BaseException(strMessage)
        if meanNSD is None:
            self._meanNSD = None
        elif meanNSD.__class__.__name__ == "XSDataDouble":
            self._meanNSD = meanNSD
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'meanNSD' is not XSDataDouble but %s" % self._meanNSD.__class__.__name__
            raise BaseException(strMessage)
        if variationNSD is None:
            self._variationNSD = None
        elif variationNSD.__class__.__name__ == "XSDataDouble":
            self._variationNSD = variationNSD
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'variationNSD' is not XSDataDouble but %s" % self._variationNSD.__class__.__name__
            raise BaseException(strMessage)
        if scatterPlot is None:
            self._scatterPlot = None
        elif scatterPlot.__class__.__name__ == "XSDataFile":
            self._scatterPlot = scatterPlot
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'scatterPlot' is not XSDataFile but %s" % self._scatterPlot.__class__.__name__
            raise BaseException(strMessage)
        if guinierPlot is None:
            self._guinierPlot = None
        elif guinierPlot.__class__.__name__ == "XSDataFile":
            self._guinierPlot = guinierPlot
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'guinierPlot' is not XSDataFile but %s" % self._guinierPlot.__class__.__name__
            raise BaseException(strMessage)
        if kratkyPlot is None:
            self._kratkyPlot = None
        elif kratkyPlot.__class__.__name__ == "XSDataFile":
            self._kratkyPlot = kratkyPlot
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering constructor argument 'kratkyPlot' is not XSDataFile but %s" % self._kratkyPlot.__class__.__name__
            raise BaseException(strMessage)
    # Methods and properties for the 'corelationFitValues' attribute
    def getCorelationFitValues(self): return self._corelationFitValues
    def setCorelationFitValues(self, corelationFitValues):
        if corelationFitValues is None:
            self._corelationFitValues = []
        elif corelationFitValues.__class__.__name__ == "list":
            self._corelationFitValues = corelationFitValues
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setCorelationFitValues argument is not list but %s" % corelationFitValues.__class__.__name__
            raise BaseException(strMessage)
    def delCorelationFitValues(self): self._corelationFitValues = None
    corelationFitValues = property(getCorelationFitValues, setCorelationFitValues, delCorelationFitValues, "Property for corelationFitValues")
    def addCorelationFitValues(self, value):
        if value is None:
            strMessage = "ERROR! XSDataResultSolutionScattering.addCorelationFitValues argument is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._corelationFitValues.append(value)
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.addCorelationFitValues argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    def insertCorelationFitValues(self, index, value):
        if index is None:
            strMessage = "ERROR! XSDataResultSolutionScattering.insertCorelationFitValues argument 'index' is None"
            raise BaseException(strMessage)
        if value is None:
            strMessage = "ERROR! XSDataResultSolutionScattering.insertCorelationFitValues argument 'value' is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._corelationFitValues[index] = value
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.addCorelationFitValues argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    # Methods and properties for the 'fitFile' attribute
    def getFitFile(self): return self._fitFile
    def setFitFile(self, fitFile):
        if fitFile is None:
            self._fitFile = None
        elif fitFile.__class__.__name__ == "XSDataFile":
            self._fitFile = fitFile
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setFitFile argument is not XSDataFile but %s" % fitFile.__class__.__name__
            raise BaseException(strMessage)
    def delFitFile(self): self._fitFile = None
    fitFile = property(getFitFile, setFitFile, delFitFile, "Property for fitFile")
    # Methods and properties for the 'lineProfileFitQuality' attribute
    def getLineProfileFitQuality(self): return self._lineProfileFitQuality
    def setLineProfileFitQuality(self, lineProfileFitQuality):
        if lineProfileFitQuality is None:
            self._lineProfileFitQuality = None
        elif lineProfileFitQuality.__class__.__name__ == "XSDataDouble":
            self._lineProfileFitQuality = lineProfileFitQuality
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setLineProfileFitQuality argument is not XSDataDouble but %s" % lineProfileFitQuality.__class__.__name__
            raise BaseException(strMessage)
    def delLineProfileFitQuality(self): self._lineProfileFitQuality = None
    lineProfileFitQuality = property(getLineProfileFitQuality, setLineProfileFitQuality, delLineProfileFitQuality, "Property for lineProfileFitQuality")
    # Methods and properties for the 'logFile' attribute
    def getLogFile(self): return self._logFile
    def setLogFile(self, logFile):
        if logFile is None:
            self._logFile = None
        elif logFile.__class__.__name__ == "XSDataFile":
            self._logFile = logFile
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setLogFile argument is not XSDataFile but %s" % logFile.__class__.__name__
            raise BaseException(strMessage)
    def delLogFile(self): self._logFile = None
    logFile = property(getLogFile, setLogFile, delLogFile, "Property for logFile")
    # Methods and properties for the 'pdbMoleculeFile' attribute
    def getPdbMoleculeFile(self): return self._pdbMoleculeFile
    def setPdbMoleculeFile(self, pdbMoleculeFile):
        if pdbMoleculeFile is None:
            self._pdbMoleculeFile = None
        elif pdbMoleculeFile.__class__.__name__ == "XSDataFile":
            self._pdbMoleculeFile = pdbMoleculeFile
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setPdbMoleculeFile argument is not XSDataFile but %s" % pdbMoleculeFile.__class__.__name__
            raise BaseException(strMessage)
    def delPdbMoleculeFile(self): self._pdbMoleculeFile = None
    pdbMoleculeFile = property(getPdbMoleculeFile, setPdbMoleculeFile, delPdbMoleculeFile, "Property for pdbMoleculeFile")
    # Methods and properties for the 'pdbSolventFile' attribute
    def getPdbSolventFile(self): return self._pdbSolventFile
    def setPdbSolventFile(self, pdbSolventFile):
        if pdbSolventFile is None:
            self._pdbSolventFile = None
        elif pdbSolventFile.__class__.__name__ == "XSDataFile":
            self._pdbSolventFile = pdbSolventFile
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setPdbSolventFile argument is not XSDataFile but %s" % pdbSolventFile.__class__.__name__
            raise BaseException(strMessage)
    def delPdbSolventFile(self): self._pdbSolventFile = None
    pdbSolventFile = property(getPdbSolventFile, setPdbSolventFile, delPdbSolventFile, "Property for pdbSolventFile")
    # Methods and properties for the 'scatteringFitQ' attribute
    def getScatteringFitQ(self): return self._scatteringFitQ
    def setScatteringFitQ(self, scatteringFitQ):
        if scatteringFitQ is None:
            self._scatteringFitQ = []
        elif scatteringFitQ.__class__.__name__ == "list":
            self._scatteringFitQ = scatteringFitQ
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setScatteringFitQ argument is not list but %s" % scatteringFitQ.__class__.__name__
            raise BaseException(strMessage)
    def delScatteringFitQ(self): self._scatteringFitQ = None
    scatteringFitQ = property(getScatteringFitQ, setScatteringFitQ, delScatteringFitQ, "Property for scatteringFitQ")
    def addScatteringFitQ(self, value):
        if value is None:
            strMessage = "ERROR! XSDataResultSolutionScattering.addScatteringFitQ argument is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._scatteringFitQ.append(value)
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.addScatteringFitQ argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    def insertScatteringFitQ(self, index, value):
        if index is None:
            strMessage = "ERROR! XSDataResultSolutionScattering.insertScatteringFitQ argument 'index' is None"
            raise BaseException(strMessage)
        if value is None:
            strMessage = "ERROR! XSDataResultSolutionScattering.insertScatteringFitQ argument 'value' is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._scatteringFitQ[index] = value
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.addScatteringFitQ argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    # Methods and properties for the 'scatteringFitValues' attribute
    def getScatteringFitValues(self): return self._scatteringFitValues
    def setScatteringFitValues(self, scatteringFitValues):
        if scatteringFitValues is None:
            self._scatteringFitValues = []
        elif scatteringFitValues.__class__.__name__ == "list":
            self._scatteringFitValues = scatteringFitValues
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setScatteringFitValues argument is not list but %s" % scatteringFitValues.__class__.__name__
            raise BaseException(strMessage)
    def delScatteringFitValues(self): self._scatteringFitValues = None
    scatteringFitValues = property(getScatteringFitValues, setScatteringFitValues, delScatteringFitValues, "Property for scatteringFitValues")
    def addScatteringFitValues(self, value):
        if value is None:
            strMessage = "ERROR! XSDataResultSolutionScattering.addScatteringFitValues argument is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._scatteringFitValues.append(value)
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.addScatteringFitValues argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    def insertScatteringFitValues(self, index, value):
        if index is None:
            strMessage = "ERROR! XSDataResultSolutionScattering.insertScatteringFitValues argument 'index' is None"
            raise BaseException(strMessage)
        if value is None:
            strMessage = "ERROR! XSDataResultSolutionScattering.insertScatteringFitValues argument 'value' is None"
            raise BaseException(strMessage)
        elif value.__class__.__name__ == "XSDataDouble":
            self._scatteringFitValues[index] = value
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.addScatteringFitValues argument is not XSDataDouble but %s" % value.__class__.__name__
            raise BaseException(strMessage)
    # Methods and properties for the 'scatteringFitQArray' attribute
    def getScatteringFitQArray(self): return self._scatteringFitQArray
    def setScatteringFitQArray(self, scatteringFitQArray):
        if scatteringFitQArray is None:
            self._scatteringFitQArray = None
        elif scatteringFitQArray.__class__.__name__ == "XSDataArray":
            self._scatteringFitQArray = scatteringFitQArray
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setScatteringFitQArray argument is not XSDataArray but %s" % scatteringFitQArray.__class__.__name__
            raise BaseException(strMessage)
    def delScatteringFitQArray(self): self._scatteringFitQArray = None
    scatteringFitQArray = property(getScatteringFitQArray, setScatteringFitQArray, delScatteringFitQArray, "Property for scatteringFitQArray")
    # Methods and properties for the 'scatteringFitIarray' attribute
    def getScatteringFitIarray(self): return self._scatteringFitIarray
    def setScatteringFitIarray(self, scatteringFitIarray):
        if scatteringFitIarray is None:
            self._scatteringFitIarray = None
        elif scatteringFitIarray.__class__.__name__ == "XSDataArray":
            self._scatteringFitIarray = scatteringFitIarray
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setScatteringFitIarray argument is not XSDataArray but %s" % scatteringFitIarray.__class__.__name__
            raise BaseException(strMessage)
    def delScatteringFitIarray(self): self._scatteringFitIarray = None
    scatteringFitIarray = property(getScatteringFitIarray, setScatteringFitIarray, delScatteringFitIarray, "Property for scatteringFitIarray")
    # Methods and properties for the 'meanNSD' attribute
    def getMeanNSD(self): return self._meanNSD
    def setMeanNSD(self, meanNSD):
        if meanNSD is None:
            self._meanNSD = None
        elif meanNSD.__class__.__name__ == "XSDataDouble":
            self._meanNSD = meanNSD
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setMeanNSD argument is not XSDataDouble but %s" % meanNSD.__class__.__name__
            raise BaseException(strMessage)
    def delMeanNSD(self): self._meanNSD = None
    meanNSD = property(getMeanNSD, setMeanNSD, delMeanNSD, "Property for meanNSD")
    # Methods and properties for the 'variationNSD' attribute
    def getVariationNSD(self): return self._variationNSD
    def setVariationNSD(self, variationNSD):
        if variationNSD is None:
            self._variationNSD = None
        elif variationNSD.__class__.__name__ == "XSDataDouble":
            self._variationNSD = variationNSD
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setVariationNSD argument is not XSDataDouble but %s" % variationNSD.__class__.__name__
            raise BaseException(strMessage)
    def delVariationNSD(self): self._variationNSD = None
    variationNSD = property(getVariationNSD, setVariationNSD, delVariationNSD, "Property for variationNSD")
    # Methods and properties for the 'scatterPlot' attribute
    def getScatterPlot(self): return self._scatterPlot
    def setScatterPlot(self, scatterPlot):
        if scatterPlot is None:
            self._scatterPlot = None
        elif scatterPlot.__class__.__name__ == "XSDataFile":
            self._scatterPlot = scatterPlot
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setScatterPlot argument is not XSDataFile but %s" % scatterPlot.__class__.__name__
            raise BaseException(strMessage)
    def delScatterPlot(self): self._scatterPlot = None
    scatterPlot = property(getScatterPlot, setScatterPlot, delScatterPlot, "Property for scatterPlot")
    # Methods and properties for the 'guinierPlot' attribute
    def getGuinierPlot(self): return self._guinierPlot
    def setGuinierPlot(self, guinierPlot):
        if guinierPlot is None:
            self._guinierPlot = None
        elif guinierPlot.__class__.__name__ == "XSDataFile":
            self._guinierPlot = guinierPlot
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setGuinierPlot argument is not XSDataFile but %s" % guinierPlot.__class__.__name__
            raise BaseException(strMessage)
    def delGuinierPlot(self): self._guinierPlot = None
    guinierPlot = property(getGuinierPlot, setGuinierPlot, delGuinierPlot, "Property for guinierPlot")
    # Methods and properties for the 'kratkyPlot' attribute
    def getKratkyPlot(self): return self._kratkyPlot
    def setKratkyPlot(self, kratkyPlot):
        if kratkyPlot is None:
            self._kratkyPlot = None
        elif kratkyPlot.__class__.__name__ == "XSDataFile":
            self._kratkyPlot = kratkyPlot
        else:
            strMessage = "ERROR! XSDataResultSolutionScattering.setKratkyPlot argument is not XSDataFile but %s" % kratkyPlot.__class__.__name__
            raise BaseException(strMessage)
    def delKratkyPlot(self): self._kratkyPlot = None
    kratkyPlot = property(getKratkyPlot, setKratkyPlot, delKratkyPlot, "Property for kratkyPlot")
    def export(self, outfile, level, name_='XSDataResultSolutionScattering'):
        showIndent(outfile, level)
        outfile.write(unicode('<%s>\n' % name_))
        self.exportChildren(outfile, level + 1, name_)
        showIndent(outfile, level)
        outfile.write(unicode('</%s>\n' % name_))
    def exportChildren(self, outfile, level, name_='XSDataResultSolutionScattering'):
        XSDataResult.exportChildren(self, outfile, level, name_)
        for corelationFitValues_ in self.getCorelationFitValues():
            corelationFitValues_.export(outfile, level, name_='corelationFitValues')
        if self._fitFile is not None:
            self.fitFile.export(outfile, level, name_='fitFile')
        else:
            warnEmptyAttribute("fitFile", "XSDataFile")
        if self._lineProfileFitQuality is not None:
            self.lineProfileFitQuality.export(outfile, level, name_='lineProfileFitQuality')
        else:
            warnEmptyAttribute("lineProfileFitQuality", "XSDataDouble")
        if self._logFile is not None:
            self.logFile.export(outfile, level, name_='logFile')
        else:
            warnEmptyAttribute("logFile", "XSDataFile")
        if self._pdbMoleculeFile is not None:
            self.pdbMoleculeFile.export(outfile, level, name_='pdbMoleculeFile')
        else:
            warnEmptyAttribute("pdbMoleculeFile", "XSDataFile")
        if self._pdbSolventFile is not None:
            self.pdbSolventFile.export(outfile, level, name_='pdbSolventFile')
        else:
            warnEmptyAttribute("pdbSolventFile", "XSDataFile")
        for scatteringFitQ_ in self.getScatteringFitQ():
            scatteringFitQ_.export(outfile, level, name_='scatteringFitQ')
        for scatteringFitValues_ in self.getScatteringFitValues():
            scatteringFitValues_.export(outfile, level, name_='scatteringFitValues')
        if self._scatteringFitQArray is not None:
            self.scatteringFitQArray.export(outfile, level, name_='scatteringFitQArray')
        if self._scatteringFitIarray is not None:
            self.scatteringFitIarray.export(outfile, level, name_='scatteringFitIarray')
        if self._meanNSD is not None:
            self.meanNSD.export(outfile, level, name_='meanNSD')
        if self._variationNSD is not None:
            self.variationNSD.export(outfile, level, name_='variationNSD')
        if self._scatterPlot is not None:
            self.scatterPlot.export(outfile, level, name_='scatterPlot')
        if self._guinierPlot is not None:
            self.guinierPlot.export(outfile, level, name_='guinierPlot')
        if self._kratkyPlot is not None:
            self.kratkyPlot.export(outfile, level, name_='kratkyPlot')
    def build(self, node_):
        for child_ in node_.childNodes:
            nodeName_ = child_.nodeName.split(':')[-1]
            self.buildChildren(child_, nodeName_)
    def buildChildren(self, child_, nodeName_):
        if child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'corelationFitValues':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.corelationFitValues.append(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'fitFile':
            obj_ = XSDataFile()
            obj_.build(child_)
            self.setFitFile(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'lineProfileFitQuality':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.setLineProfileFitQuality(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'logFile':
            obj_ = XSDataFile()
            obj_.build(child_)
            self.setLogFile(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'pdbMoleculeFile':
            obj_ = XSDataFile()
            obj_.build(child_)
            self.setPdbMoleculeFile(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'pdbSolventFile':
            obj_ = XSDataFile()
            obj_.build(child_)
            self.setPdbSolventFile(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'scatteringFitQ':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.scatteringFitQ.append(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'scatteringFitValues':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.scatteringFitValues.append(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'scatteringFitQArray':
            obj_ = XSDataArray()
            obj_.build(child_)
            self.setScatteringFitQArray(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'scatteringFitIarray':
            obj_ = XSDataArray()
            obj_.build(child_)
            self.setScatteringFitIarray(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'meanNSD':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.setMeanNSD(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'variationNSD':
            obj_ = XSDataDouble()
            obj_.build(child_)
            self.setVariationNSD(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'scatterPlot':
            obj_ = XSDataFile()
            obj_.build(child_)
            self.setScatterPlot(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'guinierPlot':
            obj_ = XSDataFile()
            obj_.build(child_)
            self.setGuinierPlot(obj_)
        elif child_.nodeType == Node.ELEMENT_NODE and \
            nodeName_ == 'kratkyPlot':
            obj_ = XSDataFile()
            obj_.build(child_)
            self.setKratkyPlot(obj_)
        XSDataResult.buildChildren(self, child_, nodeName_)
    #Method for marshalling an object
    def marshal(self):
        oStreamString = StringIO()
        oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
        self.export(oStreamString, 0, name_="XSDataResultSolutionScattering")
        oStringXML = oStreamString.getvalue()
        oStreamString.close()
        return oStringXML
    #Only to export the entire XML tree to a file stream on disk
    def exportToFile(self, _outfileName):
        outfile = open(_outfileName, "w")
        outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
        self.export(outfile, 0, name_='XSDataResultSolutionScattering')
        outfile.close()
    #Deprecated method, replaced by exportToFile
    def outputFile(self, _outfileName):
        print("WARNING: Method outputFile in class XSDataResultSolutionScattering is deprecated, please use instead exportToFile!")
        self.exportToFile(_outfileName)
    #Method for making a copy in a new instance
    def copy(self):
        return XSDataResultSolutionScattering.parseString(self.marshal())
    #Static method for parsing a string
    def parseString(_inString):
        doc = minidom.parseString(_inString)
        rootNode = doc.documentElement
        rootObj = XSDataResultSolutionScattering()
        rootObj.build(rootNode)
        # Check that all minOccurs are obeyed by marshalling the created object
        oStreamString = StringIO()
        rootObj.export(oStreamString, 0, name_="XSDataResultSolutionScattering")
        oStreamString.close()
        return rootObj
    parseString = staticmethod(parseString)
    #Static method for parsing a file
    def parseFile(_inFilePath):
        doc = minidom.parse(_inFilePath)
        rootNode = doc.documentElement
        rootObj = XSDataResultSolutionScattering()
        rootObj.build(rootNode)
        return rootObj
    parseFile = staticmethod(parseFile)
# end class XSDataResultSolutionScattering



# End of data representation classes.


