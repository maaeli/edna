#!/usr/bin/env python

#
# Generated Tue Jun 14 12:10::12 2011 by EDGenerateDS.
#

import sys
from xml.dom import minidom
from xml.dom import Node

from XSDataCommon import XSData
from XSDataCommon import XSDataAngle
from XSDataCommon import XSDataBoolean
from XSDataCommon import XSDataDouble
from XSDataCommon import XSDataInput
from XSDataCommon import XSDataInteger
from XSDataCommon import XSDataMatrixDouble
from XSDataCommon import XSDataResult
from XSDataCommon import XSDataString
from XSDataCommon import XSDataImage
from XSDataCommon import XSDataLength




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


def checkType(_strClassName, _strMethodName, _value, _strExpectedType):
	if not _strExpectedType in ["float", "double", "string", "boolean", "integer"]:
		if _value != None:
			if _value.__class__.__name__ != _strExpectedType:
				strMessage = "ERROR! %s.%s argument is not %s but %s" % (_strClassName, _strMethodName, _strExpectedType, _value.__class__.__name__)
				print(strMessage)
				#raise BaseException(strMessage)
#	elif _value is None:
#		strMessage = "ERROR! %s.%s argument which should be %s is None" % (_strClassName, _strMethodName, _strExpectedType)
#		print(strMessage)
#		#raise BaseException(strMessage)


def warnEmptyAttribute(_strName, _strTypeName):
	pass
	#if not _strTypeName in ["float", "double", "string", "boolean", "integer"]:
	#		print("Warning! Non-optional attribute %s of type %s is None!" % (_strName, _strTypeName))

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
		else:	 # category == MixedContainer.CategoryComplex
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


class XSDataCell(object):
	def __init__(self, length_c=None, length_b=None, length_a=None, angle_gamma=None, angle_beta=None, angle_alpha=None):
		checkType("XSDataCell", "Constructor of XSDataCell", angle_alpha, "XSDataAngle")
		self.__angle_alpha = angle_alpha
		checkType("XSDataCell", "Constructor of XSDataCell", angle_beta, "XSDataAngle")
		self.__angle_beta = angle_beta
		checkType("XSDataCell", "Constructor of XSDataCell", angle_gamma, "XSDataAngle")
		self.__angle_gamma = angle_gamma
		checkType("XSDataCell", "Constructor of XSDataCell", length_a, "XSDataLength")
		self.__length_a = length_a
		checkType("XSDataCell", "Constructor of XSDataCell", length_b, "XSDataLength")
		self.__length_b = length_b
		checkType("XSDataCell", "Constructor of XSDataCell", length_c, "XSDataLength")
		self.__length_c = length_c
	def getAngle_alpha(self): return self.__angle_alpha
	def setAngle_alpha(self, angle_alpha):
		checkType("XSDataCell", "setAngle_alpha", angle_alpha, "XSDataAngle")
		self.__angle_alpha = angle_alpha
	def delAngle_alpha(self): self.__angle_alpha = None
	# Properties
	angle_alpha = property(getAngle_alpha, setAngle_alpha, delAngle_alpha, "Property for angle_alpha")
	def getAngle_beta(self): return self.__angle_beta
	def setAngle_beta(self, angle_beta):
		checkType("XSDataCell", "setAngle_beta", angle_beta, "XSDataAngle")
		self.__angle_beta = angle_beta
	def delAngle_beta(self): self.__angle_beta = None
	# Properties
	angle_beta = property(getAngle_beta, setAngle_beta, delAngle_beta, "Property for angle_beta")
	def getAngle_gamma(self): return self.__angle_gamma
	def setAngle_gamma(self, angle_gamma):
		checkType("XSDataCell", "setAngle_gamma", angle_gamma, "XSDataAngle")
		self.__angle_gamma = angle_gamma
	def delAngle_gamma(self): self.__angle_gamma = None
	# Properties
	angle_gamma = property(getAngle_gamma, setAngle_gamma, delAngle_gamma, "Property for angle_gamma")
	def getLength_a(self): return self.__length_a
	def setLength_a(self, length_a):
		checkType("XSDataCell", "setLength_a", length_a, "XSDataLength")
		self.__length_a = length_a
	def delLength_a(self): self.__length_a = None
	# Properties
	length_a = property(getLength_a, setLength_a, delLength_a, "Property for length_a")
	def getLength_b(self): return self.__length_b
	def setLength_b(self, length_b):
		checkType("XSDataCell", "setLength_b", length_b, "XSDataLength")
		self.__length_b = length_b
	def delLength_b(self): self.__length_b = None
	# Properties
	length_b = property(getLength_b, setLength_b, delLength_b, "Property for length_b")
	def getLength_c(self): return self.__length_c
	def setLength_c(self, length_c):
		checkType("XSDataCell", "setLength_c", length_c, "XSDataLength")
		self.__length_c = length_c
	def delLength_c(self): self.__length_c = None
	# Properties
	length_c = property(getLength_c, setLength_c, delLength_c, "Property for length_c")
	def export(self, outfile, level, name_='XSDataCell'):
		showIndent(outfile, level)
		outfile.write(unicode('<%s>\n' % name_))
		self.exportChildren(outfile, level + 1, name_)
		showIndent(outfile, level)
		outfile.write(unicode('</%s>\n' % name_))
	def exportChildren(self, outfile, level, name_='XSDataCell'):
		pass
		if self.__angle_alpha is not None:
			self.angle_alpha.export(outfile, level, name_='angle_alpha')
		else:
			warnEmptyAttribute("angle_alpha", "XSDataAngle")
		if self.__angle_beta is not None:
			self.angle_beta.export(outfile, level, name_='angle_beta')
		else:
			warnEmptyAttribute("angle_beta", "XSDataAngle")
		if self.__angle_gamma is not None:
			self.angle_gamma.export(outfile, level, name_='angle_gamma')
		else:
			warnEmptyAttribute("angle_gamma", "XSDataAngle")
		if self.__length_a is not None:
			self.length_a.export(outfile, level, name_='length_a')
		else:
			warnEmptyAttribute("length_a", "XSDataLength")
		if self.__length_b is not None:
			self.length_b.export(outfile, level, name_='length_b')
		else:
			warnEmptyAttribute("length_b", "XSDataLength")
		if self.__length_c is not None:
			self.length_c.export(outfile, level, name_='length_c')
		else:
			warnEmptyAttribute("length_c", "XSDataLength")
	def build(self, node_):
		for child_ in node_.childNodes:
			nodeName_ = child_.nodeName.split(':')[-1]
			self.buildChildren(child_, nodeName_)
	def buildChildren(self, child_, nodeName_):
		if child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'angle_alpha':
			obj_ = XSDataAngle()
			obj_.build(child_)
			self.setAngle_alpha(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'angle_beta':
			obj_ = XSDataAngle()
			obj_.build(child_)
			self.setAngle_beta(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'angle_gamma':
			obj_ = XSDataAngle()
			obj_.build(child_)
			self.setAngle_gamma(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'length_a':
			obj_ = XSDataLength()
			obj_.build(child_)
			self.setLength_a(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'length_b':
			obj_ = XSDataLength()
			obj_.build(child_)
			self.setLength_b(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'length_c':
			obj_ = XSDataLength()
			obj_.build(child_)
			self.setLength_c(obj_)
	#Method for marshalling an object
	def marshal( self ):
		oStreamString = StringIO()
		oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
		self.export( oStreamString, 0, name_="XSDataCell" )
		oStringXML = oStreamString.getvalue()
		oStreamString.close()
		return oStringXML
	#Only to export the entire XML tree to a file stream on disk
	def exportToFile( self, _outfileName ):
		outfile = open( _outfileName, "w" )
		outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
		self.export( outfile, 0, name_='XSDataCell' )
		outfile.close()
	#Deprecated method, replaced by exportToFile
	def outputFile( self, _outfileName ):
		print("WARNING: Method outputFile in class XSDataCell is deprecated, please use instead exportToFile!")
		self.exportToFile(_outfileName)
	#Method for making a copy in a new instance
	def copy( self ):
		return XSDataCell.parseString(self.marshal())
	#Static method for parsing a string
	def parseString( _inString ):
		doc = minidom.parseString(_inString)
		rootNode = doc.documentElement
		rootObj = XSDataCell()
		rootObj.build(rootNode)
		# Check that all minOccurs are obeyed by marshalling the created object
		oStreamString = StringIO()
		rootObj.export( oStreamString, 0, name_="XSDataCell" )
		oStreamString.close()
		return rootObj
	parseString = staticmethod( parseString )
	#Static method for parsing a file
	def parseFile( _inFilePath ):
		doc = minidom.parse(_inFilePath)
		rootNode = doc.documentElement
		rootObj = XSDataCell()
		rootObj.build(rootNode)
		return rootObj
	parseFile = staticmethod( parseFile )
# end class XSDataCell

class XSDataImageQualityIndicators(XSData):
	def __init__(self, totalIntegratedSignal=None, spotTotal=None, signalRangeMin=None, signalRangeMax=None, signalRangeAverage=None, saturationRangeMin=None, saturationRangeMax=None, saturationRangeAverage=None, pctSaturationTop50Peaks=None, method2Res=None, method1Res=None, maxUnitCell=None, inResolutionOvrlSpots=None, inResTotal=None, image=None, iceRings=None, goodBraggCandidates=None, binPopCutOffMethod2Res=None):
		XSData.__init__(self, )
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", binPopCutOffMethod2Res, "XSDataDouble")
		self.__binPopCutOffMethod2Res = binPopCutOffMethod2Res
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", goodBraggCandidates, "XSDataInteger")
		self.__goodBraggCandidates = goodBraggCandidates
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", iceRings, "XSDataInteger")
		self.__iceRings = iceRings
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", image, "XSDataImage")
		self.__image = image
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", inResTotal, "XSDataInteger")
		self.__inResTotal = inResTotal
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", inResolutionOvrlSpots, "XSDataInteger")
		self.__inResolutionOvrlSpots = inResolutionOvrlSpots
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", maxUnitCell, "XSDataDouble")
		self.__maxUnitCell = maxUnitCell
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", method1Res, "XSDataDouble")
		self.__method1Res = method1Res
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", method2Res, "XSDataDouble")
		self.__method2Res = method2Res
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", pctSaturationTop50Peaks, "XSDataDouble")
		self.__pctSaturationTop50Peaks = pctSaturationTop50Peaks
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", saturationRangeAverage, "XSDataDouble")
		self.__saturationRangeAverage = saturationRangeAverage
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", saturationRangeMax, "XSDataDouble")
		self.__saturationRangeMax = saturationRangeMax
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", saturationRangeMin, "XSDataDouble")
		self.__saturationRangeMin = saturationRangeMin
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", signalRangeAverage, "XSDataDouble")
		self.__signalRangeAverage = signalRangeAverage
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", signalRangeMax, "XSDataDouble")
		self.__signalRangeMax = signalRangeMax
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", signalRangeMin, "XSDataDouble")
		self.__signalRangeMin = signalRangeMin
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", spotTotal, "XSDataInteger")
		self.__spotTotal = spotTotal
		checkType("XSDataImageQualityIndicators", "Constructor of XSDataImageQualityIndicators", totalIntegratedSignal, "XSDataDouble")
		self.__totalIntegratedSignal = totalIntegratedSignal
	def getBinPopCutOffMethod2Res(self): return self.__binPopCutOffMethod2Res
	def setBinPopCutOffMethod2Res(self, binPopCutOffMethod2Res):
		checkType("XSDataImageQualityIndicators", "setBinPopCutOffMethod2Res", binPopCutOffMethod2Res, "XSDataDouble")
		self.__binPopCutOffMethod2Res = binPopCutOffMethod2Res
	def delBinPopCutOffMethod2Res(self): self.__binPopCutOffMethod2Res = None
	# Properties
	binPopCutOffMethod2Res = property(getBinPopCutOffMethod2Res, setBinPopCutOffMethod2Res, delBinPopCutOffMethod2Res, "Property for binPopCutOffMethod2Res")
	def getGoodBraggCandidates(self): return self.__goodBraggCandidates
	def setGoodBraggCandidates(self, goodBraggCandidates):
		checkType("XSDataImageQualityIndicators", "setGoodBraggCandidates", goodBraggCandidates, "XSDataInteger")
		self.__goodBraggCandidates = goodBraggCandidates
	def delGoodBraggCandidates(self): self.__goodBraggCandidates = None
	# Properties
	goodBraggCandidates = property(getGoodBraggCandidates, setGoodBraggCandidates, delGoodBraggCandidates, "Property for goodBraggCandidates")
	def getIceRings(self): return self.__iceRings
	def setIceRings(self, iceRings):
		checkType("XSDataImageQualityIndicators", "setIceRings", iceRings, "XSDataInteger")
		self.__iceRings = iceRings
	def delIceRings(self): self.__iceRings = None
	# Properties
	iceRings = property(getIceRings, setIceRings, delIceRings, "Property for iceRings")
	def getImage(self): return self.__image
	def setImage(self, image):
		checkType("XSDataImageQualityIndicators", "setImage", image, "XSDataImage")
		self.__image = image
	def delImage(self): self.__image = None
	# Properties
	image = property(getImage, setImage, delImage, "Property for image")
	def getInResTotal(self): return self.__inResTotal
	def setInResTotal(self, inResTotal):
		checkType("XSDataImageQualityIndicators", "setInResTotal", inResTotal, "XSDataInteger")
		self.__inResTotal = inResTotal
	def delInResTotal(self): self.__inResTotal = None
	# Properties
	inResTotal = property(getInResTotal, setInResTotal, delInResTotal, "Property for inResTotal")
	def getInResolutionOvrlSpots(self): return self.__inResolutionOvrlSpots
	def setInResolutionOvrlSpots(self, inResolutionOvrlSpots):
		checkType("XSDataImageQualityIndicators", "setInResolutionOvrlSpots", inResolutionOvrlSpots, "XSDataInteger")
		self.__inResolutionOvrlSpots = inResolutionOvrlSpots
	def delInResolutionOvrlSpots(self): self.__inResolutionOvrlSpots = None
	# Properties
	inResolutionOvrlSpots = property(getInResolutionOvrlSpots, setInResolutionOvrlSpots, delInResolutionOvrlSpots, "Property for inResolutionOvrlSpots")
	def getMaxUnitCell(self): return self.__maxUnitCell
	def setMaxUnitCell(self, maxUnitCell):
		checkType("XSDataImageQualityIndicators", "setMaxUnitCell", maxUnitCell, "XSDataDouble")
		self.__maxUnitCell = maxUnitCell
	def delMaxUnitCell(self): self.__maxUnitCell = None
	# Properties
	maxUnitCell = property(getMaxUnitCell, setMaxUnitCell, delMaxUnitCell, "Property for maxUnitCell")
	def getMethod1Res(self): return self.__method1Res
	def setMethod1Res(self, method1Res):
		checkType("XSDataImageQualityIndicators", "setMethod1Res", method1Res, "XSDataDouble")
		self.__method1Res = method1Res
	def delMethod1Res(self): self.__method1Res = None
	# Properties
	method1Res = property(getMethod1Res, setMethod1Res, delMethod1Res, "Property for method1Res")
	def getMethod2Res(self): return self.__method2Res
	def setMethod2Res(self, method2Res):
		checkType("XSDataImageQualityIndicators", "setMethod2Res", method2Res, "XSDataDouble")
		self.__method2Res = method2Res
	def delMethod2Res(self): self.__method2Res = None
	# Properties
	method2Res = property(getMethod2Res, setMethod2Res, delMethod2Res, "Property for method2Res")
	def getPctSaturationTop50Peaks(self): return self.__pctSaturationTop50Peaks
	def setPctSaturationTop50Peaks(self, pctSaturationTop50Peaks):
		checkType("XSDataImageQualityIndicators", "setPctSaturationTop50Peaks", pctSaturationTop50Peaks, "XSDataDouble")
		self.__pctSaturationTop50Peaks = pctSaturationTop50Peaks
	def delPctSaturationTop50Peaks(self): self.__pctSaturationTop50Peaks = None
	# Properties
	pctSaturationTop50Peaks = property(getPctSaturationTop50Peaks, setPctSaturationTop50Peaks, delPctSaturationTop50Peaks, "Property for pctSaturationTop50Peaks")
	def getSaturationRangeAverage(self): return self.__saturationRangeAverage
	def setSaturationRangeAverage(self, saturationRangeAverage):
		checkType("XSDataImageQualityIndicators", "setSaturationRangeAverage", saturationRangeAverage, "XSDataDouble")
		self.__saturationRangeAverage = saturationRangeAverage
	def delSaturationRangeAverage(self): self.__saturationRangeAverage = None
	# Properties
	saturationRangeAverage = property(getSaturationRangeAverage, setSaturationRangeAverage, delSaturationRangeAverage, "Property for saturationRangeAverage")
	def getSaturationRangeMax(self): return self.__saturationRangeMax
	def setSaturationRangeMax(self, saturationRangeMax):
		checkType("XSDataImageQualityIndicators", "setSaturationRangeMax", saturationRangeMax, "XSDataDouble")
		self.__saturationRangeMax = saturationRangeMax
	def delSaturationRangeMax(self): self.__saturationRangeMax = None
	# Properties
	saturationRangeMax = property(getSaturationRangeMax, setSaturationRangeMax, delSaturationRangeMax, "Property for saturationRangeMax")
	def getSaturationRangeMin(self): return self.__saturationRangeMin
	def setSaturationRangeMin(self, saturationRangeMin):
		checkType("XSDataImageQualityIndicators", "setSaturationRangeMin", saturationRangeMin, "XSDataDouble")
		self.__saturationRangeMin = saturationRangeMin
	def delSaturationRangeMin(self): self.__saturationRangeMin = None
	# Properties
	saturationRangeMin = property(getSaturationRangeMin, setSaturationRangeMin, delSaturationRangeMin, "Property for saturationRangeMin")
	def getSignalRangeAverage(self): return self.__signalRangeAverage
	def setSignalRangeAverage(self, signalRangeAverage):
		checkType("XSDataImageQualityIndicators", "setSignalRangeAverage", signalRangeAverage, "XSDataDouble")
		self.__signalRangeAverage = signalRangeAverage
	def delSignalRangeAverage(self): self.__signalRangeAverage = None
	# Properties
	signalRangeAverage = property(getSignalRangeAverage, setSignalRangeAverage, delSignalRangeAverage, "Property for signalRangeAverage")
	def getSignalRangeMax(self): return self.__signalRangeMax
	def setSignalRangeMax(self, signalRangeMax):
		checkType("XSDataImageQualityIndicators", "setSignalRangeMax", signalRangeMax, "XSDataDouble")
		self.__signalRangeMax = signalRangeMax
	def delSignalRangeMax(self): self.__signalRangeMax = None
	# Properties
	signalRangeMax = property(getSignalRangeMax, setSignalRangeMax, delSignalRangeMax, "Property for signalRangeMax")
	def getSignalRangeMin(self): return self.__signalRangeMin
	def setSignalRangeMin(self, signalRangeMin):
		checkType("XSDataImageQualityIndicators", "setSignalRangeMin", signalRangeMin, "XSDataDouble")
		self.__signalRangeMin = signalRangeMin
	def delSignalRangeMin(self): self.__signalRangeMin = None
	# Properties
	signalRangeMin = property(getSignalRangeMin, setSignalRangeMin, delSignalRangeMin, "Property for signalRangeMin")
	def getSpotTotal(self): return self.__spotTotal
	def setSpotTotal(self, spotTotal):
		checkType("XSDataImageQualityIndicators", "setSpotTotal", spotTotal, "XSDataInteger")
		self.__spotTotal = spotTotal
	def delSpotTotal(self): self.__spotTotal = None
	# Properties
	spotTotal = property(getSpotTotal, setSpotTotal, delSpotTotal, "Property for spotTotal")
	def getTotalIntegratedSignal(self): return self.__totalIntegratedSignal
	def setTotalIntegratedSignal(self, totalIntegratedSignal):
		checkType("XSDataImageQualityIndicators", "setTotalIntegratedSignal", totalIntegratedSignal, "XSDataDouble")
		self.__totalIntegratedSignal = totalIntegratedSignal
	def delTotalIntegratedSignal(self): self.__totalIntegratedSignal = None
	# Properties
	totalIntegratedSignal = property(getTotalIntegratedSignal, setTotalIntegratedSignal, delTotalIntegratedSignal, "Property for totalIntegratedSignal")
	def export(self, outfile, level, name_='XSDataImageQualityIndicators'):
		showIndent(outfile, level)
		outfile.write(unicode('<%s>\n' % name_))
		self.exportChildren(outfile, level + 1, name_)
		showIndent(outfile, level)
		outfile.write(unicode('</%s>\n' % name_))
	def exportChildren(self, outfile, level, name_='XSDataImageQualityIndicators'):
		XSData.exportChildren(self, outfile, level, name_)
		if self.__binPopCutOffMethod2Res is not None:
			self.binPopCutOffMethod2Res.export(outfile, level, name_='binPopCutOffMethod2Res')
		else:
			warnEmptyAttribute("binPopCutOffMethod2Res", "XSDataDouble")
		if self.__goodBraggCandidates is not None:
			self.goodBraggCandidates.export(outfile, level, name_='goodBraggCandidates')
		else:
			warnEmptyAttribute("goodBraggCandidates", "XSDataInteger")
		if self.__iceRings is not None:
			self.iceRings.export(outfile, level, name_='iceRings')
		else:
			warnEmptyAttribute("iceRings", "XSDataInteger")
		if self.__image is not None:
			self.image.export(outfile, level, name_='image')
		else:
			warnEmptyAttribute("image", "XSDataImage")
		if self.__inResTotal is not None:
			self.inResTotal.export(outfile, level, name_='inResTotal')
		else:
			warnEmptyAttribute("inResTotal", "XSDataInteger")
		if self.__inResolutionOvrlSpots is not None:
			self.inResolutionOvrlSpots.export(outfile, level, name_='inResolutionOvrlSpots')
		else:
			warnEmptyAttribute("inResolutionOvrlSpots", "XSDataInteger")
		if self.__maxUnitCell is not None:
			self.maxUnitCell.export(outfile, level, name_='maxUnitCell')
		else:
			warnEmptyAttribute("maxUnitCell", "XSDataDouble")
		if self.__method1Res is not None:
			self.method1Res.export(outfile, level, name_='method1Res')
		else:
			warnEmptyAttribute("method1Res", "XSDataDouble")
		if self.__method2Res is not None:
			self.method2Res.export(outfile, level, name_='method2Res')
		else:
			warnEmptyAttribute("method2Res", "XSDataDouble")
		if self.__pctSaturationTop50Peaks is not None:
			self.pctSaturationTop50Peaks.export(outfile, level, name_='pctSaturationTop50Peaks')
		else:
			warnEmptyAttribute("pctSaturationTop50Peaks", "XSDataDouble")
		if self.__saturationRangeAverage is not None:
			self.saturationRangeAverage.export(outfile, level, name_='saturationRangeAverage')
		if self.__saturationRangeMax is not None:
			self.saturationRangeMax.export(outfile, level, name_='saturationRangeMax')
		if self.__saturationRangeMin is not None:
			self.saturationRangeMin.export(outfile, level, name_='saturationRangeMin')
		if self.__signalRangeAverage is not None:
			self.signalRangeAverage.export(outfile, level, name_='signalRangeAverage')
		if self.__signalRangeMax is not None:
			self.signalRangeMax.export(outfile, level, name_='signalRangeMax')
		if self.__signalRangeMin is not None:
			self.signalRangeMin.export(outfile, level, name_='signalRangeMin')
		if self.__spotTotal is not None:
			self.spotTotal.export(outfile, level, name_='spotTotal')
		else:
			warnEmptyAttribute("spotTotal", "XSDataInteger")
		if self.__totalIntegratedSignal is not None:
			self.totalIntegratedSignal.export(outfile, level, name_='totalIntegratedSignal')
	def build(self, node_):
		for child_ in node_.childNodes:
			nodeName_ = child_.nodeName.split(':')[-1]
			self.buildChildren(child_, nodeName_)
	def buildChildren(self, child_, nodeName_):
		if child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'binPopCutOffMethod2Res':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setBinPopCutOffMethod2Res(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'goodBraggCandidates':
			obj_ = XSDataInteger()
			obj_.build(child_)
			self.setGoodBraggCandidates(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'iceRings':
			obj_ = XSDataInteger()
			obj_.build(child_)
			self.setIceRings(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'image':
			obj_ = XSDataImage()
			obj_.build(child_)
			self.setImage(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'inResTotal':
			obj_ = XSDataInteger()
			obj_.build(child_)
			self.setInResTotal(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'inResolutionOvrlSpots':
			obj_ = XSDataInteger()
			obj_.build(child_)
			self.setInResolutionOvrlSpots(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'maxUnitCell':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setMaxUnitCell(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'method1Res':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setMethod1Res(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'method2Res':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setMethod2Res(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'pctSaturationTop50Peaks':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setPctSaturationTop50Peaks(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'saturationRangeAverage':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setSaturationRangeAverage(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'saturationRangeMax':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setSaturationRangeMax(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'saturationRangeMin':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setSaturationRangeMin(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'signalRangeAverage':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setSignalRangeAverage(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'signalRangeMax':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setSignalRangeMax(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'signalRangeMin':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setSignalRangeMin(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'spotTotal':
			obj_ = XSDataInteger()
			obj_.build(child_)
			self.setSpotTotal(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'totalIntegratedSignal':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setTotalIntegratedSignal(obj_)
		XSData.buildChildren(self, child_, nodeName_)
	#Method for marshalling an object
	def marshal( self ):
		oStreamString = StringIO()
		oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
		self.export( oStreamString, 0, name_="XSDataImageQualityIndicators" )
		oStringXML = oStreamString.getvalue()
		oStreamString.close()
		return oStringXML
	#Only to export the entire XML tree to a file stream on disk
	def exportToFile( self, _outfileName ):
		outfile = open( _outfileName, "w" )
		outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
		self.export( outfile, 0, name_='XSDataImageQualityIndicators' )
		outfile.close()
	#Deprecated method, replaced by exportToFile
	def outputFile( self, _outfileName ):
		print("WARNING: Method outputFile in class XSDataImageQualityIndicators is deprecated, please use instead exportToFile!")
		self.exportToFile(_outfileName)
	#Method for making a copy in a new instance
	def copy( self ):
		return XSDataImageQualityIndicators.parseString(self.marshal())
	#Static method for parsing a string
	def parseString( _inString ):
		doc = minidom.parseString(_inString)
		rootNode = doc.documentElement
		rootObj = XSDataImageQualityIndicators()
		rootObj.build(rootNode)
		# Check that all minOccurs are obeyed by marshalling the created object
		oStreamString = StringIO()
		rootObj.export( oStreamString, 0, name_="XSDataImageQualityIndicators" )
		oStreamString.close()
		return rootObj
	parseString = staticmethod( parseString )
	#Static method for parsing a file
	def parseFile( _inFilePath ):
		doc = minidom.parse(_inFilePath)
		rootNode = doc.documentElement
		rootObj = XSDataImageQualityIndicators()
		rootObj.build(rootNode)
		return rootObj
	parseFile = staticmethod( parseFile )
# end class XSDataImageQualityIndicators

class XSDataLabelitMosflmScriptsOutput(XSData):
	def __init__(self, uMatrix=None, aMatrix=None):
		XSData.__init__(self, )
		checkType("XSDataLabelitMosflmScriptsOutput", "Constructor of XSDataLabelitMosflmScriptsOutput", aMatrix, "XSDataMatrixDouble")
		self.__aMatrix = aMatrix
		checkType("XSDataLabelitMosflmScriptsOutput", "Constructor of XSDataLabelitMosflmScriptsOutput", uMatrix, "XSDataMatrixDouble")
		self.__uMatrix = uMatrix
	def getAMatrix(self): return self.__aMatrix
	def setAMatrix(self, aMatrix):
		checkType("XSDataLabelitMosflmScriptsOutput", "setAMatrix", aMatrix, "XSDataMatrixDouble")
		self.__aMatrix = aMatrix
	def delAMatrix(self): self.__aMatrix = None
	# Properties
	aMatrix = property(getAMatrix, setAMatrix, delAMatrix, "Property for aMatrix")
	def getUMatrix(self): return self.__uMatrix
	def setUMatrix(self, uMatrix):
		checkType("XSDataLabelitMosflmScriptsOutput", "setUMatrix", uMatrix, "XSDataMatrixDouble")
		self.__uMatrix = uMatrix
	def delUMatrix(self): self.__uMatrix = None
	# Properties
	uMatrix = property(getUMatrix, setUMatrix, delUMatrix, "Property for uMatrix")
	def export(self, outfile, level, name_='XSDataLabelitMosflmScriptsOutput'):
		showIndent(outfile, level)
		outfile.write(unicode('<%s>\n' % name_))
		self.exportChildren(outfile, level + 1, name_)
		showIndent(outfile, level)
		outfile.write(unicode('</%s>\n' % name_))
	def exportChildren(self, outfile, level, name_='XSDataLabelitMosflmScriptsOutput'):
		XSData.exportChildren(self, outfile, level, name_)
		if self.__aMatrix is not None:
			self.aMatrix.export(outfile, level, name_='aMatrix')
		else:
			warnEmptyAttribute("aMatrix", "XSDataMatrixDouble")
		if self.__uMatrix is not None:
			self.uMatrix.export(outfile, level, name_='uMatrix')
		else:
			warnEmptyAttribute("uMatrix", "XSDataMatrixDouble")
	def build(self, node_):
		for child_ in node_.childNodes:
			nodeName_ = child_.nodeName.split(':')[-1]
			self.buildChildren(child_, nodeName_)
	def buildChildren(self, child_, nodeName_):
		if child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'aMatrix':
			obj_ = XSDataMatrixDouble()
			obj_.build(child_)
			self.setAMatrix(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'uMatrix':
			obj_ = XSDataMatrixDouble()
			obj_.build(child_)
			self.setUMatrix(obj_)
		XSData.buildChildren(self, child_, nodeName_)
	#Method for marshalling an object
	def marshal( self ):
		oStreamString = StringIO()
		oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
		self.export( oStreamString, 0, name_="XSDataLabelitMosflmScriptsOutput" )
		oStringXML = oStreamString.getvalue()
		oStreamString.close()
		return oStringXML
	#Only to export the entire XML tree to a file stream on disk
	def exportToFile( self, _outfileName ):
		outfile = open( _outfileName, "w" )
		outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
		self.export( outfile, 0, name_='XSDataLabelitMosflmScriptsOutput' )
		outfile.close()
	#Deprecated method, replaced by exportToFile
	def outputFile( self, _outfileName ):
		print("WARNING: Method outputFile in class XSDataLabelitMosflmScriptsOutput is deprecated, please use instead exportToFile!")
		self.exportToFile(_outfileName)
	#Method for making a copy in a new instance
	def copy( self ):
		return XSDataLabelitMosflmScriptsOutput.parseString(self.marshal())
	#Static method for parsing a string
	def parseString( _inString ):
		doc = minidom.parseString(_inString)
		rootNode = doc.documentElement
		rootObj = XSDataLabelitMosflmScriptsOutput()
		rootObj.build(rootNode)
		# Check that all minOccurs are obeyed by marshalling the created object
		oStreamString = StringIO()
		rootObj.export( oStreamString, 0, name_="XSDataLabelitMosflmScriptsOutput" )
		oStreamString.close()
		return rootObj
	parseString = staticmethod( parseString )
	#Static method for parsing a file
	def parseFile( _inFilePath ):
		doc = minidom.parse(_inFilePath)
		rootNode = doc.documentElement
		rootObj = XSDataLabelitMosflmScriptsOutput()
		rootObj.build(rootNode)
		return rootObj
	parseFile = staticmethod( parseFile )
# end class XSDataLabelitMosflmScriptsOutput

class XSDataLabelitScreenSolution(XSData):
	def __init__(self, volume=None, unitCell=None, solutionNumber=None, rmsd=None, numberOfSpots=None, metricFitValue=None, metricFitCode=None, happy=None, crystalSystem=None, bravaisLattice=None):
		XSData.__init__(self, )
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", bravaisLattice, "XSDataString")
		self.__bravaisLattice = bravaisLattice
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", crystalSystem, "XSDataString")
		self.__crystalSystem = crystalSystem
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", happy, "XSDataBoolean")
		self.__happy = happy
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", metricFitCode, "XSDataString")
		self.__metricFitCode = metricFitCode
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", metricFitValue, "XSDataDouble")
		self.__metricFitValue = metricFitValue
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", numberOfSpots, "XSDataInteger")
		self.__numberOfSpots = numberOfSpots
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", rmsd, "XSDataLength")
		self.__rmsd = rmsd
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", solutionNumber, "XSDataInteger")
		self.__solutionNumber = solutionNumber
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", unitCell, "XSDataCell")
		self.__unitCell = unitCell
		checkType("XSDataLabelitScreenSolution", "Constructor of XSDataLabelitScreenSolution", volume, "XSDataInteger")
		self.__volume = volume
	def getBravaisLattice(self): return self.__bravaisLattice
	def setBravaisLattice(self, bravaisLattice):
		checkType("XSDataLabelitScreenSolution", "setBravaisLattice", bravaisLattice, "XSDataString")
		self.__bravaisLattice = bravaisLattice
	def delBravaisLattice(self): self.__bravaisLattice = None
	# Properties
	bravaisLattice = property(getBravaisLattice, setBravaisLattice, delBravaisLattice, "Property for bravaisLattice")
	def getCrystalSystem(self): return self.__crystalSystem
	def setCrystalSystem(self, crystalSystem):
		checkType("XSDataLabelitScreenSolution", "setCrystalSystem", crystalSystem, "XSDataString")
		self.__crystalSystem = crystalSystem
	def delCrystalSystem(self): self.__crystalSystem = None
	# Properties
	crystalSystem = property(getCrystalSystem, setCrystalSystem, delCrystalSystem, "Property for crystalSystem")
	def getHappy(self): return self.__happy
	def setHappy(self, happy):
		checkType("XSDataLabelitScreenSolution", "setHappy", happy, "XSDataBoolean")
		self.__happy = happy
	def delHappy(self): self.__happy = None
	# Properties
	happy = property(getHappy, setHappy, delHappy, "Property for happy")
	def getMetricFitCode(self): return self.__metricFitCode
	def setMetricFitCode(self, metricFitCode):
		checkType("XSDataLabelitScreenSolution", "setMetricFitCode", metricFitCode, "XSDataString")
		self.__metricFitCode = metricFitCode
	def delMetricFitCode(self): self.__metricFitCode = None
	# Properties
	metricFitCode = property(getMetricFitCode, setMetricFitCode, delMetricFitCode, "Property for metricFitCode")
	def getMetricFitValue(self): return self.__metricFitValue
	def setMetricFitValue(self, metricFitValue):
		checkType("XSDataLabelitScreenSolution", "setMetricFitValue", metricFitValue, "XSDataDouble")
		self.__metricFitValue = metricFitValue
	def delMetricFitValue(self): self.__metricFitValue = None
	# Properties
	metricFitValue = property(getMetricFitValue, setMetricFitValue, delMetricFitValue, "Property for metricFitValue")
	def getNumberOfSpots(self): return self.__numberOfSpots
	def setNumberOfSpots(self, numberOfSpots):
		checkType("XSDataLabelitScreenSolution", "setNumberOfSpots", numberOfSpots, "XSDataInteger")
		self.__numberOfSpots = numberOfSpots
	def delNumberOfSpots(self): self.__numberOfSpots = None
	# Properties
	numberOfSpots = property(getNumberOfSpots, setNumberOfSpots, delNumberOfSpots, "Property for numberOfSpots")
	def getRmsd(self): return self.__rmsd
	def setRmsd(self, rmsd):
		checkType("XSDataLabelitScreenSolution", "setRmsd", rmsd, "XSDataLength")
		self.__rmsd = rmsd
	def delRmsd(self): self.__rmsd = None
	# Properties
	rmsd = property(getRmsd, setRmsd, delRmsd, "Property for rmsd")
	def getSolutionNumber(self): return self.__solutionNumber
	def setSolutionNumber(self, solutionNumber):
		checkType("XSDataLabelitScreenSolution", "setSolutionNumber", solutionNumber, "XSDataInteger")
		self.__solutionNumber = solutionNumber
	def delSolutionNumber(self): self.__solutionNumber = None
	# Properties
	solutionNumber = property(getSolutionNumber, setSolutionNumber, delSolutionNumber, "Property for solutionNumber")
	def getUnitCell(self): return self.__unitCell
	def setUnitCell(self, unitCell):
		checkType("XSDataLabelitScreenSolution", "setUnitCell", unitCell, "XSDataCell")
		self.__unitCell = unitCell
	def delUnitCell(self): self.__unitCell = None
	# Properties
	unitCell = property(getUnitCell, setUnitCell, delUnitCell, "Property for unitCell")
	def getVolume(self): return self.__volume
	def setVolume(self, volume):
		checkType("XSDataLabelitScreenSolution", "setVolume", volume, "XSDataInteger")
		self.__volume = volume
	def delVolume(self): self.__volume = None
	# Properties
	volume = property(getVolume, setVolume, delVolume, "Property for volume")
	def export(self, outfile, level, name_='XSDataLabelitScreenSolution'):
		showIndent(outfile, level)
		outfile.write(unicode('<%s>\n' % name_))
		self.exportChildren(outfile, level + 1, name_)
		showIndent(outfile, level)
		outfile.write(unicode('</%s>\n' % name_))
	def exportChildren(self, outfile, level, name_='XSDataLabelitScreenSolution'):
		XSData.exportChildren(self, outfile, level, name_)
		if self.__bravaisLattice is not None:
			self.bravaisLattice.export(outfile, level, name_='bravaisLattice')
		else:
			warnEmptyAttribute("bravaisLattice", "XSDataString")
		if self.__crystalSystem is not None:
			self.crystalSystem.export(outfile, level, name_='crystalSystem')
		else:
			warnEmptyAttribute("crystalSystem", "XSDataString")
		if self.__happy is not None:
			self.happy.export(outfile, level, name_='happy')
		else:
			warnEmptyAttribute("happy", "XSDataBoolean")
		if self.__metricFitCode is not None:
			self.metricFitCode.export(outfile, level, name_='metricFitCode')
		else:
			warnEmptyAttribute("metricFitCode", "XSDataString")
		if self.__metricFitValue is not None:
			self.metricFitValue.export(outfile, level, name_='metricFitValue')
		else:
			warnEmptyAttribute("metricFitValue", "XSDataDouble")
		if self.__numberOfSpots is not None:
			self.numberOfSpots.export(outfile, level, name_='numberOfSpots')
		else:
			warnEmptyAttribute("numberOfSpots", "XSDataInteger")
		if self.__rmsd is not None:
			self.rmsd.export(outfile, level, name_='rmsd')
		else:
			warnEmptyAttribute("rmsd", "XSDataLength")
		if self.__solutionNumber is not None:
			self.solutionNumber.export(outfile, level, name_='solutionNumber')
		else:
			warnEmptyAttribute("solutionNumber", "XSDataInteger")
		if self.__unitCell is not None:
			self.unitCell.export(outfile, level, name_='unitCell')
		else:
			warnEmptyAttribute("unitCell", "XSDataCell")
		if self.__volume is not None:
			self.volume.export(outfile, level, name_='volume')
		else:
			warnEmptyAttribute("volume", "XSDataInteger")
	def build(self, node_):
		for child_ in node_.childNodes:
			nodeName_ = child_.nodeName.split(':')[-1]
			self.buildChildren(child_, nodeName_)
	def buildChildren(self, child_, nodeName_):
		if child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'bravaisLattice':
			obj_ = XSDataString()
			obj_.build(child_)
			self.setBravaisLattice(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'crystalSystem':
			obj_ = XSDataString()
			obj_.build(child_)
			self.setCrystalSystem(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'happy':
			obj_ = XSDataBoolean()
			obj_.build(child_)
			self.setHappy(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'metricFitCode':
			obj_ = XSDataString()
			obj_.build(child_)
			self.setMetricFitCode(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'metricFitValue':
			obj_ = XSDataDouble()
			obj_.build(child_)
			self.setMetricFitValue(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'numberOfSpots':
			obj_ = XSDataInteger()
			obj_.build(child_)
			self.setNumberOfSpots(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'rmsd':
			obj_ = XSDataLength()
			obj_.build(child_)
			self.setRmsd(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'solutionNumber':
			obj_ = XSDataInteger()
			obj_.build(child_)
			self.setSolutionNumber(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'unitCell':
			obj_ = XSDataCell()
			obj_.build(child_)
			self.setUnitCell(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'volume':
			obj_ = XSDataInteger()
			obj_.build(child_)
			self.setVolume(obj_)
		XSData.buildChildren(self, child_, nodeName_)
	#Method for marshalling an object
	def marshal( self ):
		oStreamString = StringIO()
		oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
		self.export( oStreamString, 0, name_="XSDataLabelitScreenSolution" )
		oStringXML = oStreamString.getvalue()
		oStreamString.close()
		return oStringXML
	#Only to export the entire XML tree to a file stream on disk
	def exportToFile( self, _outfileName ):
		outfile = open( _outfileName, "w" )
		outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
		self.export( outfile, 0, name_='XSDataLabelitScreenSolution' )
		outfile.close()
	#Deprecated method, replaced by exportToFile
	def outputFile( self, _outfileName ):
		print("WARNING: Method outputFile in class XSDataLabelitScreenSolution is deprecated, please use instead exportToFile!")
		self.exportToFile(_outfileName)
	#Method for making a copy in a new instance
	def copy( self ):
		return XSDataLabelitScreenSolution.parseString(self.marshal())
	#Static method for parsing a string
	def parseString( _inString ):
		doc = minidom.parseString(_inString)
		rootNode = doc.documentElement
		rootObj = XSDataLabelitScreenSolution()
		rootObj.build(rootNode)
		# Check that all minOccurs are obeyed by marshalling the created object
		oStreamString = StringIO()
		rootObj.export( oStreamString, 0, name_="XSDataLabelitScreenSolution" )
		oStreamString.close()
		return rootObj
	parseString = staticmethod( parseString )
	#Static method for parsing a file
	def parseFile( _inFilePath ):
		doc = minidom.parse(_inFilePath)
		rootNode = doc.documentElement
		rootObj = XSDataLabelitScreenSolution()
		rootObj.build(rootNode)
		return rootObj
	parseFile = staticmethod( parseFile )
# end class XSDataLabelitScreenSolution

class XSDataLabelitScreenOutput(XSData):
	def __init__(self, selectedSolutionNumber=None, mosaicity=None, labelitScreenSolution=None, distance=None, beamCentreY=None, beamCentreX=None):
		XSData.__init__(self, )
		checkType("XSDataLabelitScreenOutput", "Constructor of XSDataLabelitScreenOutput", beamCentreX, "XSDataLength")
		self.__beamCentreX = beamCentreX
		checkType("XSDataLabelitScreenOutput", "Constructor of XSDataLabelitScreenOutput", beamCentreY, "XSDataLength")
		self.__beamCentreY = beamCentreY
		checkType("XSDataLabelitScreenOutput", "Constructor of XSDataLabelitScreenOutput", distance, "XSDataLength")
		self.__distance = distance
		if labelitScreenSolution is None:
			self.__labelitScreenSolution = []
		else:
			checkType("XSDataLabelitScreenOutput", "Constructor of XSDataLabelitScreenOutput", labelitScreenSolution, "XSDataLabelitScreenSolution")
			self.__labelitScreenSolution = labelitScreenSolution
		checkType("XSDataLabelitScreenOutput", "Constructor of XSDataLabelitScreenOutput", mosaicity, "XSDataAngle")
		self.__mosaicity = mosaicity
		checkType("XSDataLabelitScreenOutput", "Constructor of XSDataLabelitScreenOutput", selectedSolutionNumber, "XSDataInteger")
		self.__selectedSolutionNumber = selectedSolutionNumber
	def getBeamCentreX(self): return self.__beamCentreX
	def setBeamCentreX(self, beamCentreX):
		checkType("XSDataLabelitScreenOutput", "setBeamCentreX", beamCentreX, "XSDataLength")
		self.__beamCentreX = beamCentreX
	def delBeamCentreX(self): self.__beamCentreX = None
	# Properties
	beamCentreX = property(getBeamCentreX, setBeamCentreX, delBeamCentreX, "Property for beamCentreX")
	def getBeamCentreY(self): return self.__beamCentreY
	def setBeamCentreY(self, beamCentreY):
		checkType("XSDataLabelitScreenOutput", "setBeamCentreY", beamCentreY, "XSDataLength")
		self.__beamCentreY = beamCentreY
	def delBeamCentreY(self): self.__beamCentreY = None
	# Properties
	beamCentreY = property(getBeamCentreY, setBeamCentreY, delBeamCentreY, "Property for beamCentreY")
	def getDistance(self): return self.__distance
	def setDistance(self, distance):
		checkType("XSDataLabelitScreenOutput", "setDistance", distance, "XSDataLength")
		self.__distance = distance
	def delDistance(self): self.__distance = None
	# Properties
	distance = property(getDistance, setDistance, delDistance, "Property for distance")
	def getLabelitScreenSolution(self): return self.__labelitScreenSolution
	def setLabelitScreenSolution(self, labelitScreenSolution):
		checkType("XSDataLabelitScreenOutput", "setLabelitScreenSolution", labelitScreenSolution, "list")
		self.__labelitScreenSolution = labelitScreenSolution
	def delLabelitScreenSolution(self): self.__labelitScreenSolution = None
	# Properties
	labelitScreenSolution = property(getLabelitScreenSolution, setLabelitScreenSolution, delLabelitScreenSolution, "Property for labelitScreenSolution")
	def addLabelitScreenSolution(self, value):
		checkType("XSDataLabelitScreenOutput", "setLabelitScreenSolution", value, "XSDataLabelitScreenSolution")
		self.__labelitScreenSolution.append(value)
	def insertLabelitScreenSolution(self, index, value):
		checkType("XSDataLabelitScreenOutput", "setLabelitScreenSolution", value, "XSDataLabelitScreenSolution")
		self.__labelitScreenSolution[index] = value
	def getMosaicity(self): return self.__mosaicity
	def setMosaicity(self, mosaicity):
		checkType("XSDataLabelitScreenOutput", "setMosaicity", mosaicity, "XSDataAngle")
		self.__mosaicity = mosaicity
	def delMosaicity(self): self.__mosaicity = None
	# Properties
	mosaicity = property(getMosaicity, setMosaicity, delMosaicity, "Property for mosaicity")
	def getSelectedSolutionNumber(self): return self.__selectedSolutionNumber
	def setSelectedSolutionNumber(self, selectedSolutionNumber):
		checkType("XSDataLabelitScreenOutput", "setSelectedSolutionNumber", selectedSolutionNumber, "XSDataInteger")
		self.__selectedSolutionNumber = selectedSolutionNumber
	def delSelectedSolutionNumber(self): self.__selectedSolutionNumber = None
	# Properties
	selectedSolutionNumber = property(getSelectedSolutionNumber, setSelectedSolutionNumber, delSelectedSolutionNumber, "Property for selectedSolutionNumber")
	def export(self, outfile, level, name_='XSDataLabelitScreenOutput'):
		showIndent(outfile, level)
		outfile.write(unicode('<%s>\n' % name_))
		self.exportChildren(outfile, level + 1, name_)
		showIndent(outfile, level)
		outfile.write(unicode('</%s>\n' % name_))
	def exportChildren(self, outfile, level, name_='XSDataLabelitScreenOutput'):
		XSData.exportChildren(self, outfile, level, name_)
		if self.__beamCentreX is not None:
			self.beamCentreX.export(outfile, level, name_='beamCentreX')
		else:
			warnEmptyAttribute("beamCentreX", "XSDataLength")
		if self.__beamCentreY is not None:
			self.beamCentreY.export(outfile, level, name_='beamCentreY')
		else:
			warnEmptyAttribute("beamCentreY", "XSDataLength")
		if self.__distance is not None:
			self.distance.export(outfile, level, name_='distance')
		else:
			warnEmptyAttribute("distance", "XSDataLength")
		for labelitScreenSolution_ in self.getLabelitScreenSolution():
			labelitScreenSolution_.export(outfile, level, name_='labelitScreenSolution')
		if self.__mosaicity is not None:
			self.mosaicity.export(outfile, level, name_='mosaicity')
		else:
			warnEmptyAttribute("mosaicity", "XSDataAngle")
		if self.__selectedSolutionNumber is not None:
			self.selectedSolutionNumber.export(outfile, level, name_='selectedSolutionNumber')
		else:
			warnEmptyAttribute("selectedSolutionNumber", "XSDataInteger")
	def build(self, node_):
		for child_ in node_.childNodes:
			nodeName_ = child_.nodeName.split(':')[-1]
			self.buildChildren(child_, nodeName_)
	def buildChildren(self, child_, nodeName_):
		if child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'beamCentreX':
			obj_ = XSDataLength()
			obj_.build(child_)
			self.setBeamCentreX(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'beamCentreY':
			obj_ = XSDataLength()
			obj_.build(child_)
			self.setBeamCentreY(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'distance':
			obj_ = XSDataLength()
			obj_.build(child_)
			self.setDistance(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'labelitScreenSolution':
			obj_ = XSDataLabelitScreenSolution()
			obj_.build(child_)
			self.labelitScreenSolution.append(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'mosaicity':
			obj_ = XSDataAngle()
			obj_.build(child_)
			self.setMosaicity(obj_)
		elif child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'selectedSolutionNumber':
			obj_ = XSDataInteger()
			obj_.build(child_)
			self.setSelectedSolutionNumber(obj_)
		XSData.buildChildren(self, child_, nodeName_)
	#Method for marshalling an object
	def marshal( self ):
		oStreamString = StringIO()
		oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
		self.export( oStreamString, 0, name_="XSDataLabelitScreenOutput" )
		oStringXML = oStreamString.getvalue()
		oStreamString.close()
		return oStringXML
	#Only to export the entire XML tree to a file stream on disk
	def exportToFile( self, _outfileName ):
		outfile = open( _outfileName, "w" )
		outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
		self.export( outfile, 0, name_='XSDataLabelitScreenOutput' )
		outfile.close()
	#Deprecated method, replaced by exportToFile
	def outputFile( self, _outfileName ):
		print("WARNING: Method outputFile in class XSDataLabelitScreenOutput is deprecated, please use instead exportToFile!")
		self.exportToFile(_outfileName)
	#Method for making a copy in a new instance
	def copy( self ):
		return XSDataLabelitScreenOutput.parseString(self.marshal())
	#Static method for parsing a string
	def parseString( _inString ):
		doc = minidom.parseString(_inString)
		rootNode = doc.documentElement
		rootObj = XSDataLabelitScreenOutput()
		rootObj.build(rootNode)
		# Check that all minOccurs are obeyed by marshalling the created object
		oStreamString = StringIO()
		rootObj.export( oStreamString, 0, name_="XSDataLabelitScreenOutput" )
		oStreamString.close()
		return rootObj
	parseString = staticmethod( parseString )
	#Static method for parsing a file
	def parseFile( _inFilePath ):
		doc = minidom.parse(_inFilePath)
		rootNode = doc.documentElement
		rootObj = XSDataLabelitScreenOutput()
		rootObj.build(rootNode)
		return rootObj
	parseFile = staticmethod( parseFile )
# end class XSDataLabelitScreenOutput

class XSDataInputDistlSignalStrength(XSDataInput):
	def __init__(self, configuration=None, referenceImage=None):
		XSDataInput.__init__(self, configuration)
		checkType("XSDataInputDistlSignalStrength", "Constructor of XSDataInputDistlSignalStrength", referenceImage, "XSDataImage")
		self.__referenceImage = referenceImage
	def getReferenceImage(self): return self.__referenceImage
	def setReferenceImage(self, referenceImage):
		checkType("XSDataInputDistlSignalStrength", "setReferenceImage", referenceImage, "XSDataImage")
		self.__referenceImage = referenceImage
	def delReferenceImage(self): self.__referenceImage = None
	# Properties
	referenceImage = property(getReferenceImage, setReferenceImage, delReferenceImage, "Property for referenceImage")
	def export(self, outfile, level, name_='XSDataInputDistlSignalStrength'):
		showIndent(outfile, level)
		outfile.write(unicode('<%s>\n' % name_))
		self.exportChildren(outfile, level + 1, name_)
		showIndent(outfile, level)
		outfile.write(unicode('</%s>\n' % name_))
	def exportChildren(self, outfile, level, name_='XSDataInputDistlSignalStrength'):
		XSDataInput.exportChildren(self, outfile, level, name_)
		if self.__referenceImage is not None:
			self.referenceImage.export(outfile, level, name_='referenceImage')
		else:
			warnEmptyAttribute("referenceImage", "XSDataImage")
	def build(self, node_):
		for child_ in node_.childNodes:
			nodeName_ = child_.nodeName.split(':')[-1]
			self.buildChildren(child_, nodeName_)
	def buildChildren(self, child_, nodeName_):
		if child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'referenceImage':
			obj_ = XSDataImage()
			obj_.build(child_)
			self.setReferenceImage(obj_)
		XSDataInput.buildChildren(self, child_, nodeName_)
	#Method for marshalling an object
	def marshal( self ):
		oStreamString = StringIO()
		oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
		self.export( oStreamString, 0, name_="XSDataInputDistlSignalStrength" )
		oStringXML = oStreamString.getvalue()
		oStreamString.close()
		return oStringXML
	#Only to export the entire XML tree to a file stream on disk
	def exportToFile( self, _outfileName ):
		outfile = open( _outfileName, "w" )
		outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
		self.export( outfile, 0, name_='XSDataInputDistlSignalStrength' )
		outfile.close()
	#Deprecated method, replaced by exportToFile
	def outputFile( self, _outfileName ):
		print("WARNING: Method outputFile in class XSDataInputDistlSignalStrength is deprecated, please use instead exportToFile!")
		self.exportToFile(_outfileName)
	#Method for making a copy in a new instance
	def copy( self ):
		return XSDataInputDistlSignalStrength.parseString(self.marshal())
	#Static method for parsing a string
	def parseString( _inString ):
		doc = minidom.parseString(_inString)
		rootNode = doc.documentElement
		rootObj = XSDataInputDistlSignalStrength()
		rootObj.build(rootNode)
		# Check that all minOccurs are obeyed by marshalling the created object
		oStreamString = StringIO()
		rootObj.export( oStreamString, 0, name_="XSDataInputDistlSignalStrength" )
		oStreamString.close()
		return rootObj
	parseString = staticmethod( parseString )
	#Static method for parsing a file
	def parseFile( _inFilePath ):
		doc = minidom.parse(_inFilePath)
		rootNode = doc.documentElement
		rootObj = XSDataInputDistlSignalStrength()
		rootObj.build(rootNode)
		return rootObj
	parseFile = staticmethod( parseFile )
# end class XSDataInputDistlSignalStrength

class XSDataResultDistlSignalStrength(XSDataResult):
	def __init__(self, status=None, imageQualityIndicators=None):
		XSDataResult.__init__(self, status)
		checkType("XSDataResultDistlSignalStrength", "Constructor of XSDataResultDistlSignalStrength", imageQualityIndicators, "XSDataImageQualityIndicators")
		self.__imageQualityIndicators = imageQualityIndicators
	def getImageQualityIndicators(self): return self.__imageQualityIndicators
	def setImageQualityIndicators(self, imageQualityIndicators):
		checkType("XSDataResultDistlSignalStrength", "setImageQualityIndicators", imageQualityIndicators, "XSDataImageQualityIndicators")
		self.__imageQualityIndicators = imageQualityIndicators
	def delImageQualityIndicators(self): self.__imageQualityIndicators = None
	# Properties
	imageQualityIndicators = property(getImageQualityIndicators, setImageQualityIndicators, delImageQualityIndicators, "Property for imageQualityIndicators")
	def export(self, outfile, level, name_='XSDataResultDistlSignalStrength'):
		showIndent(outfile, level)
		outfile.write(unicode('<%s>\n' % name_))
		self.exportChildren(outfile, level + 1, name_)
		showIndent(outfile, level)
		outfile.write(unicode('</%s>\n' % name_))
	def exportChildren(self, outfile, level, name_='XSDataResultDistlSignalStrength'):
		XSDataResult.exportChildren(self, outfile, level, name_)
		if self.__imageQualityIndicators is not None:
			self.imageQualityIndicators.export(outfile, level, name_='imageQualityIndicators')
		else:
			warnEmptyAttribute("imageQualityIndicators", "XSDataImageQualityIndicators")
	def build(self, node_):
		for child_ in node_.childNodes:
			nodeName_ = child_.nodeName.split(':')[-1]
			self.buildChildren(child_, nodeName_)
	def buildChildren(self, child_, nodeName_):
		if child_.nodeType == Node.ELEMENT_NODE and \
			nodeName_ == 'imageQualityIndicators':
			obj_ = XSDataImageQualityIndicators()
			obj_.build(child_)
			self.setImageQualityIndicators(obj_)
		XSDataResult.buildChildren(self, child_, nodeName_)
	#Method for marshalling an object
	def marshal( self ):
		oStreamString = StringIO()
		oStreamString.write(unicode('<?xml version="1.0" ?>\n'))
		self.export( oStreamString, 0, name_="XSDataResultDistlSignalStrength" )
		oStringXML = oStreamString.getvalue()
		oStreamString.close()
		return oStringXML
	#Only to export the entire XML tree to a file stream on disk
	def exportToFile( self, _outfileName ):
		outfile = open( _outfileName, "w" )
		outfile.write(unicode('<?xml version=\"1.0\" ?>\n'))
		self.export( outfile, 0, name_='XSDataResultDistlSignalStrength' )
		outfile.close()
	#Deprecated method, replaced by exportToFile
	def outputFile( self, _outfileName ):
		print("WARNING: Method outputFile in class XSDataResultDistlSignalStrength is deprecated, please use instead exportToFile!")
		self.exportToFile(_outfileName)
	#Method for making a copy in a new instance
	def copy( self ):
		return XSDataResultDistlSignalStrength.parseString(self.marshal())
	#Static method for parsing a string
	def parseString( _inString ):
		doc = minidom.parseString(_inString)
		rootNode = doc.documentElement
		rootObj = XSDataResultDistlSignalStrength()
		rootObj.build(rootNode)
		# Check that all minOccurs are obeyed by marshalling the created object
		oStreamString = StringIO()
		rootObj.export( oStreamString, 0, name_="XSDataResultDistlSignalStrength" )
		oStreamString.close()
		return rootObj
	parseString = staticmethod( parseString )
	#Static method for parsing a file
	def parseFile( _inFilePath ):
		doc = minidom.parse(_inFilePath)
		rootNode = doc.documentElement
		rootObj = XSDataResultDistlSignalStrength()
		rootObj.build(rootNode)
		return rootObj
	parseFile = staticmethod( parseFile )
# end class XSDataResultDistlSignalStrength



# End of data representation classes.


