# coding: utf8
# 
#    Project: BioSaxs
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) ESRF
#
#    Principal author:        Jérôme Kieffer
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
from __future__ import with_statement

__author__ = "Jérôme Kieffer"
__license__ = "GPLv3+"
__copyright__ = "ESRF"
__date__ = "20130110"
__status__ = "development"

import os, sys, threading
from EDVerbose              import EDVerbose
from EDPluginControl        import EDPluginControl
from EDUtilsPlatform        import EDUtilsPlatform
from EDFactoryPlugin        import edFactoryPlugin
from EDThreading            import Semaphore
edFactoryPlugin.loadModule("XSDataEdnaSaxs")
edFactoryPlugin.loadModule("XSDataBioSaxsv1_0")
edFactoryPlugin.loadModule("XSDataWaitFilev1_0")
from XSDataWaitFilev1_0     import XSDataInputWaitFile
from XSDataBioSaxsv1_0      import XSDataInputBioSaxsProcessOneFilev1_0, XSDataResultBioSaxsProcessOneFilev1_0, \
                            XSDataInputBioSaxsNormalizev1_0, XSDataInputBioSaxsAzimutIntv1_0
from XSDataCommon           import XSDataStatus, XSDataString, XSDataFile, XSDataImage, XSDataInteger, XSDataTime

import numpy
import pyFAI

if pyFAI.version <= "0.8":
    EDVerbose.ERROR("Too old version of pyFAI detected ... expect to fail !")


class EDPluginBioSaxsProcessOneFilev1_3(EDPluginControl):
    """
    Control plugin that does the same as previously without sub-plugin call ...
    except WaitFile which is still called.
    
    Nota normalization is done AFTER integration not before as previously
    
    TODO: configuration for device selection
    """
#    __strControlledPluginNormalize = "EDPluginBioSaxsNormalizev1_1"
#    __strControlledPluginIntegrate = "EDPluginBioSaxsAzimutIntv1_3"
    cpWaitFile = "EDPluginWaitFile"
    integrator = pyFAI.AzimuthalIntegrator()
    CONF_DUMMY_PIXEL_VALUE = "DummyPixelValue"
    CONF_DUMMY_PIXEL_DELTA = "DummyPixelDelta"
    __configured = False
    dummy = -2
    delta_dummy = 1.1
    semaphore = Semaphore()

    if pyFAI.opencl.ocl is None:
        METHOD = "lut"
    else:
        METHOD = "lut_ocl_gpu"

    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsProcessOneFilev1_0)
#        self.__edPluginNormalize = None
#        self.__edPluginIntegrate = None
        self.__edPluginWaitFile = None

        self.rawImageSize = XSDataInteger(1024)
        self.normalizedImage = None
        self.integratedCurve = None
        self.integratedImage = None
        self.lstExecutiveSummary = []
        self.sample = None
        self.experimentSetup = None
        self.integrator_config = {}
        self.scale = None


    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_3.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.rawImage, "No raw image provided")
        self.checkMandatoryParameters(self.dataInput.sample, "No sample information provided")
        self.checkMandatoryParameters(self.dataInput.experimentSetup, "No experimental setup provided")
        self.checkMandatoryParameters(self.dataInput.integratedCurve, "Missing integratedCurve")

    def configure(self):
        """
        Configures the plugin from the configuration file with the following parameters:
         - DummyPixelValue: the value be assigned to dummy pixels.
         - DummyPixelDelta: the value be assigned to delta dummy.
        """
        EDPluginControl.configure(self)
        if not self.__configured:
            with self.semaphore:
                if not self.__configured:
                    self.DEBUG("EDPluginBioSaxsProcessOneFilev1_3.configure")
                    dummy = self.config.get(self.CONF_DUMMY_PIXEL_VALUE)
                    if dummy is None:
                        strMessage = 'EDPluginBioSaxsProcessOneFilev1_3.configure: %s Configuration parameter missing: \
            %s, defaulting to "%s"' % (self.getBaseName(), self.CONF_DUMMY_PIXEL_VALUE, self.dummy)
                        self.WARNING(strMessage)
                        self.addErrorWarningMessagesToExecutiveSummary(strMessage)
                    else:
                        self.__class__.dummy = dummy
                    ddummy = self.config.get(self.CONF_DUMMY_PIXEL_DELTA)
                    if ddummy is None:
                        strMessage = 'EDPluginBioSaxsProcessOneFilev1_3.configure: %s Configuration parameter missing: \
            %s, defaulting to "%s"' % (self.getBaseName(), self.CONF_DUMMY_PIXEL_DELTA, self.delta_dummy)
                        self.WARNING(strMessage)
                        self.addErrorWarningMessagesToExecutiveSummary(strMessage)
                    else:
                        self.__class__.delta_dummy = ddummy
                    self.__class__.__configured = True


    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_3.preProcess")
        self.__edPluginWaitFile = self.loadPlugin(self.cpWaitFile)
        if self.dataInput.rawImageSize is not None:
            self.rawImageSize = self.dataInput.rawImageSize
        if self.dataInput.rawImage is not None:
            self.rawImage = self.dataInput.rawImage.path.value
        self.integratedCurve = self.dataInput.integratedCurve.path.value
        curveDir = os.path.dirname(self.integratedCurve)
        if not os.path.isdir(curveDir):
            try:
                os.mkdir(curveDir)
            except OSError:
                #could occure in race condition ...  
                pass

        self.sample = self.dataInput.sample
        self.experimentSetup = self.dataInput.experimentSetup
        self.integrator_config = {'dist': self.experimentSetup.detectorDistance.value,
                                  'pixel1': self.experimentSetup.pixelSize_2.value, # flip X,Y
                                  'pixel2': self.experimentSetup.pixelSize_1.value, # flip X,Y
                                  'poni1': self.experimentSetup.beamCenter_2.value * self.experimentSetup.pixelSize_2.value,
                                  'poni2': self.experimentSetup.beamCenter_1.value * self.experimentSetup.pixelSize_1.value,
                                  'rot1': 0.0,
                                  'rot2': 0.0,
                                  'rot3': 0.0,
                                  'splineFile': None}
        i0 = self.experimentSetup.beamStopDiode.value
        if i0 == 0:
            warn = "beamStopDiode is Null --> If we are testing, this is OK, else investigate !!!"
            self.lstProcessLog.append(warn)
            self.warning(warn)
            self.scale = self.experimentSetup.normalizationFactor.value
        else:
            self.scale = self.experimentSetup.normalizationFactor.value / i0


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_3.process")

        xsd = XSDataInputWaitFile(expectedFile=XSDataFile(XSDataString(self.rawImage)),
                                           expectedSize=self.rawImageSize,
                                           timeOut=XSDataTime(30))
        self.__edPluginWaitFile.setDataInput(xsd)
        self.__edPluginWaitFile.connectSUCCESS(self.doSuccessWaitFile)
        self.__edPluginWaitFile.connectFAILURE(self.doFailureWaitFile)
        self.__edPluginWaitFile.executeSynchronous()
        if self.isFailure():
            return

        q, I, std = self.integrate()
        I = self.normalize(I)
        std = self.normalize(std)
        self.write3ColumnAscii(q, I, std, self.integratedCurve)

    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_3.postProcess")
        # Create some output data
        xsDataResult = XSDataResultBioSaxsProcessOneFilev1_0()
        if os.path.exists(self.integratedCurve):
            xsDataResult.integratedCurve = XSDataFile(XSDataString(self.integratedCurve))
        xsDataResult.sample = self.sample
        xsDataResult.experimentSetup = self.experimentSetup

        xsDataResult.status = XSDataStatus(executiveSummary=XSDataString(os.linesep.join(self.lstExecutiveSummary)))
        self.setDataOutput(xsDataResult)

    def integrate(self):
        img = fabio.open(self.rawImage)
        with self.__class__.semaphore:
            if (self.integrator.getPyFAI() != self.integrator_config) or \
               (self.integrator.wavelength != self.experimentSetup.wavelength.value) or\
               (self.integrator.maskfile != self.experimentSetup.maskFile.path.value):
                self.screen("Resetting PyFAI integrator")
                self.integrator.setPyFAI(**self.integrator_config)
                self.integrator.wavelength = self.experimentSetup.wavelength.value
                self.integrator.detector.mask = self.calc_mask()

#            with EDUtilsParallel.getSemaphoreNbThreads():


            #todo: go to integrate1d
            q, I, std = self.integrator.integrate1d(data=img.data, nbPt=max(img.dim1, img.dim2),
                                       correctSolidAngle=True,
#                                       variance=variance.data,
                                       dummy=self.dummy, delta_dummy=self.delta_dummy,
                                       filename=None,
                                       error_model="poisson",
                                       radial_range=None, azimuth_range=None,
                                       polarization_factor=0, dark=None, flat=None,
                                       method=self.METHOD, unit="q_nm^-1", safe=False)
        self.lstExecutiveSummary.append("Azimuthal integration of raw image '%s'-->'%s'." % (self.rawImage, self.integratedCurve))
        return q, I, std

    def normalize(self, data):
        """
        Perform the normalization of some data 
        @return: normalized data
        """
        maskedData = numpy.ma.masked_array(data, abs(data - self.dummy) < self.delta_dummy)
        return numpy.ma.filled(maskedData * self.scale, self.dummy)

    def calc_mask(self):
        """
        Merge the natural mask from the detector with the user proided one.
        @return: numpy array with the mask
        """

        mask = fabio.open(self.experimentSetup.maskFile.path.value).data
        detector_name = self.experimentSetup.detector.value
        if detector_name == "pilatus":
            detector_name += "1m"
        detector_mask = pyFAI.detectors.detector_factory(detector_name).calc_mask()
        shape0, shape1 = detector_mask.shape
        if detector_mask.shape == mask.shape:
            mask = numpy.logical_or(mask, detector_mask)
        else:
            #crop the user defined mask
            mask = numpy.logical_or(mask[:shape0, :shape1], detector_mask)
        return mask

    def write3ColumnAscii(self, npaQ, npaI, npaStd=None, outputCurve="output.dat", hdr="#", linesep=os.linesep):
        """
        @param npaQ,npaI,npaStd: 3x 1d numpy array containing Scattering vector, Intensity and deviation
        @param outputCurve: name of the 3-column ascii file to be written
        @param hdr: header mark, usually '#'


Adam Round explicitelly asked for (email from Date: Tue, 04 Oct 2011 15:22:29 +0200) :
Modification from:

# BSA buffer
# Sample c= 0.0 mg/ml (these two lines are required for current DOS pipeline and can be cleaned up once we use EDNA to get to ab-initio models)
#
# Sample environment:
# Detector = Pilatus 1M
# PixelSize_1 = 0.000172
# PixelSize_2 = 6.283185 (I think it could avoid confusion if we give teh actual pixel size as 0.000172 for X and Y and not to give the integrated sizes. Also could there also be a modification for PixelSize_1 as on the diagonal wont it be the hypotenuse (0.000243)? and thus will be on average a bit bigger than 0.000172)
#
# title = BSA buffer
# Frame 7 of 10
# Time per frame (s) = 10
# SampleDistance = 2.43
# WaveLength = 9.31e-11
# Normalization = 0.0004885
# History-1 = saxs_angle +pass -omod n -rsys normal -da 360_deg -odim = 1 /data/id14eh3/inhouse/saxs_pilatus/Adam/EDNAtests/2d/dumdum_008_07.edf/data/id14eh3/inhouse/saxs_pilatus/Adam/EDNAtests/misc/dumdum_008_07.ang
# DiodeCurr = 0.0001592934
# MachCurr = 163.3938
# Mask = /data/id14eh3/archive/CALIBRATION/MASK/Pcon_01Jun_msk.edf
# SaxsDataVersion = 2.40
#
# N 3
# L q*nm  I_BSA buffer  stddev
#
# Sample Information:
# Storage Temperature (degrees C): 4
# Measurement Temperature (degrees C): 10
# Concentration: 0.0
# Code: BSA
s-vector Intensity Error
s-vector Intensity Error
s-vector Intensity Error
s-vector Intensity Error
        """
        hdr = str(hdr)
        headers = []
        if self.sample.comments is not None:
            headers.append(hdr + " " + self.sample.comments.value)
        else:
            headers.append(hdr)
        if self.sample.concentration is not None:
            headers.append(hdr + " Sample c= %s mg/ml" % self.sample.concentration.value)
        else:
            headers.append(hdr + " Sample c= -1  mg/ml")
        headers += [hdr,
                   hdr + " Sample environment:"]
        if self.experimentSetup.detector is not None:
            headers.append(hdr + " Detector = %s" % self.experimentSetup.detector.value)
        if self.experimentSetup.pixelSize_1 is not None:
            headers.append(hdr + " PixelSize_1 = %s" % self.experimentSetup.pixelSize_1.value)
        if self.experimentSetup.pixelSize_2 is not None:
            headers.append(hdr + " PixelSize_2 = %s" % self.experimentSetup.pixelSize_2.value)
        headers.append(hdr)
        if self.sample.comments is not None:
            headers.append(hdr + " title = %s" % self.sample.comments.value)
        if (self.experimentSetup.frameNumber is not None) and\
           (self.experimentSetup.frameMax is not None):
            headers.append(hdr + " Frame %s of %s" % (self.experimentSetup.frameNumber.value, self.experimentSetup.frameMax.value))
        if self.experimentSetup.exposureTime is not None:
            headers.append(hdr + " Time per frame (s) = %s" % self.experimentSetup.exposureTime.value)
        if self.experimentSetup.detectorDistance is not None:
            headers.append(hdr + " SampleDistance = %s" % self.experimentSetup.detectorDistance.value)
        if self.experimentSetup.wavelength is not None:
            headers.append(hdr + " WaveLength = %s" % self.experimentSetup.wavelength.value)
        if self.experimentSetup.normalizationFactor is not None:
            headers.append(hdr + " Normalization = %s" % self.experimentSetup.normalizationFactor.value)
        if self.experimentSetup.beamStopDiode is not None:
            headers.append(hdr + " DiodeCurr = %s" % self.experimentSetup.beamStopDiode.value)
        if self.experimentSetup.machineCurrent is not None:
            headers.append(hdr + " MachCurr = %s" % self.experimentSetup.machineCurrent.value)
        if self.experimentSetup.maskFile is not None:
            headers.append(hdr + " Mask = %s" % self.experimentSetup.maskFile.path.value)
        headers.append(hdr)
        headers.append(hdr + " N 3")
        if self.sample.comments is not None:
            headers.append(hdr + " L q*nm  I_%s  stddev" % self.sample.comments.value)
        else:
            headers.append(hdr + " L q*nm  I_  stddev")
        headers.append(hdr)
        headers.append(hdr + " Sample Information:")
        if self.experimentSetup.storageTemperature is not None:
            headers.append(hdr + " Storage Temperature (degrees C): %s" % self.experimentSetup.storageTemperature.value)
        if self.experimentSetup.exposureTemperature is not None:
            headers.append(hdr + " Measurement Temperature (degrees C): %s" % self.experimentSetup.exposureTemperature.value)

        if self.sample.concentration is not None:
            headers.append(hdr + " Concentration: %s" % self.sample.concentration.value)
        else:
            headers.append(hdr + " Concentration: -1")
        if self.sample.code is not None:
            headers.append(hdr + " Code: %s" % self.sample.code.value)
        else:
            headers.append(hdr + " Code: ")

        with open(outputCurve, "w") as f:
            f.writelines(linesep.join(headers))
            f.write(linesep)
            if npaStd is None:
                data = ["%14.6e %14.6e " % (q, I)
                        for q, I in zip(npaQ, npaI)
                        if abs(I - self.dummy) > self.delta_dummy]
            else:
                data = ["%14.6e %14.6e %14.6e" % (q, I, std)
                        for q, I, std in zip(npaQ, npaI, npaStd)
                        if abs(I - self.dummy) > self.delta_dummy]
            data.append("")
            f.writelines(linesep.join(data))
            f.flush()

    def doSuccessWaitFile(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_3.doSuccessWaitFile")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginBioSaxsProcessOneFilev1_3.doSuccessWaitFile")

    def doFailureWaitFile(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_3.doFailureWaitFile")
        self.retrieveFailureMessages(_edPlugin, "EDPluginBioSaxsProcessOneFilev1_3.doFailureWaitFile")
        self.lstProcessLog.append("Timeout in waiting for file '%s'" % (self.rawImage))
        self.setFailure()


################################################################################
# EDPluginBioSaxsNormalizev1_1
################################################################################
class EDPluginBioSaxsNormalizev1_1(EDPluginControl):
    """
    Wait for the file to appear then apply mask ;  
    do the normalization of the raw data by ring current and BeamStopDiode 
    and finally append all metadata to the file EDF.
    
    All "processing" are done with Numpy, Input/Output is handled by Fabio
    """
    __maskfiles = {} #key=filename, value=numpy.ndarray
    __semaphore = threading.Semaphore()
    CONF_DUMMY_PIXEL_VALUE = "DummyPixelValue"

    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsNormalizev1_0)
        self.__strPluginNameWaitFile = "EDPluginWaitFile"
        self.__edPluginExecWaitFile = None

        self.dummy = None
        self.strLogFile = None
        self.strRawImage = None
        self.strRawImageSize = None
        self.strNormalizedImage = None
        self.lstProcessLog = [] #comments to be returned

        self.xsdInput = None
        self.sample = None
        self.experimentSetup = None
        self.xsdResult = XSDataResultBioSaxsNormalizev1_0()
        self.dictOutputHeader = {}

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginBioSaxsNormalizev1_1.checkParameters")
        self.xsdInput = self.dataInput
        self.checkMandatoryParameters(self.xsdInput, "Data Input is None")
        self.checkMandatoryParameters(self.xsdInput.rawImage, "Raw File is None")
        self.checkMandatoryParameters(self.xsdInput.normalizedImage, "No normalized output image provided")
        self.checkMandatoryParameters(self.xsdInput.sample, "No sample provided")
        self.checkMandatoryParameters(self.xsdInput.experimentSetup, "No experiment setup provided")


    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        self.DEBUG("EDPluginBioSaxsNormalizev1_1.preProcess")
        self.sample = self.xsdInput.sample
        self.experimentSetup = self.xsdInput.experimentSetup
#        self.strLogFile = self.xsdInput.getLogFile().path.value
        self.strRawImage = self.xsdInput.rawImage.path.value
        self.strNormalizedImage = self.xsdInput.normalizedImage.path.value
        outDir = os.path.dirname(self.strNormalizedImage)
        if outDir and not os.path.exists(outDir):
            os.mkdir(outDir)
        self.strRawImageSize = self.xsdInput.getRawImageSize().value
        self.dictOutputHeader["DiodeCurr"] = self.experimentSetup.beamStopDiode.value
        self.dictOutputHeader["Normalization"] = self.experimentSetup.normalizationFactor.value
        self.dictOutputHeader["MachCurr"] = self.experimentSetup.machineCurrent.value
        self.dictOutputHeader["Mask"] = str(self.experimentSetup.maskFile.path.value)
        self.dictOutputHeader["SampleDistance"] = self.experimentSetup.detectorDistance.value
        self.dictOutputHeader["WaveLength"] = self.experimentSetup.wavelength.value
        self.dictOutputHeader["PSize_1"] = self.experimentSetup.pixelSize_1.value
        self.dictOutputHeader["PSize_2"] = self.experimentSetup.pixelSize_2.value
        self.dictOutputHeader["Center_1"] = self.experimentSetup.beamCenter_1.value
        self.dictOutputHeader["Center_2"] = self.experimentSetup.beamCenter_2.value
        if self.experimentSetup.storageTemperature is not None:
            self.dictOutputHeader["storageTemperature"] = self.experimentSetup.storageTemperature.value
        if self.experimentSetup.exposureTemperature is not None:
            self.dictOutputHeader["exposureTemperature"] = self.experimentSetup.exposureTemperature.value
        if self.experimentSetup.exposureTime is not None:
            self.dictOutputHeader["exposureTime"] = self.experimentSetup.exposureTime.value
        if self.experimentSetup.frameNumber is not None:
            self.dictOutputHeader["frameNumber"] = self.experimentSetup.frameNumber.value
        if self.experimentSetup.frameMax is not None:
            self.dictOutputHeader["frameMax"] = self.experimentSetup.frameMax.value

        if self.sample.comments is not None:
            self.dictOutputHeader["Comments"] = str(self.sample.comments.value)
            self.dictOutputHeader["title"] = str(self.sample.comments.value)

        if self.sample.concentration is not None:
            self.dictOutputHeader["Concentration"] = str(self.sample.concentration.value)
        if self.sample.code is not None:
            self.dictOutputHeader["Code"] = str(self.sample.code.value)

        # Load the execution plugin
        self.__edPluginExecWaitFile = self.loadPlugin(self.__strPluginNameWaitFile)


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginBioSaxsNormalizev1_1.process")
        xsdiWaitFile = XSDataInputWaitFile(expectedFile=XSDataFile(self.xsdInput.rawImage.path),
                                           expectedSize=self.xsdInput.rawImageSize,
                                           timeOut=XSDataTime(value=30))
        self.__edPluginExecWaitFile.setDataInput(xsdiWaitFile)
        self.__edPluginExecWaitFile.connectSUCCESS(self.doSuccessExecWaitFile)
        self.__edPluginExecWaitFile.connectFAILURE(self.doFailureExecWaitFile)
        self.__edPluginExecWaitFile.executeSynchronous()
        if self.isFailure():
            return
#        Small Numpy processing:
        fabIn = fabio.open(self.strRawImage)
        if "time_of_day" in fabIn.header:
            self.dictOutputHeader["time_of_day"] = fabIn.header["time_of_day"]
        if "Mask" in self.dictOutputHeader:
            mask = self.getMask(self.dictOutputHeader["Mask"])
            npaMaskedData = numpy.ma.masked_array(fabIn.data.astype("float32"),
                                                  ((fabIn.data < 0) + (mask[:fabIn.dim2, :fabIn.dim1 ] < 0)))
        else:
            npaMaskedData = numpy.ma.masked_array(fabIn.data.astype("float32"), (fabIn.data < 0))
        if self.dictOutputHeader["DiodeCurr"] == 0:
            warn = "DiodeCurr is Null --> I Guess we are testing and take it as one"
            self.lstProcessLog.append(warn)
            self.warning(warn)
            scale = self.dictOutputHeader["Normalization"]
        else:
            scale = self.dictOutputHeader["Normalization"] / self.dictOutputHeader["DiodeCurr"]
        self.dictOutputHeader["Dummy"] = str(self.dummy)
        self.dictOutputHeader["DDummy"] = "0.1"
        self.dictOutputHeader["EDF_DataBlockID"] = "1.Image.Psd"
        header_keys = self.dictOutputHeader.keys()
        header_keys.sort()
        fabioOut = fabio.edfimage.edfimage(header=self.dictOutputHeader, header_keys=header_keys,
                             data=numpy.ma.filled(npaMaskedData * scale, float(self.dummy)))
        fabioOut.appendFrame(header={"Dummy": str(self.dummy), "DDummy":"0.1", "EDF_DataBlockID":"1.Image.Error"},
                              data=(numpy.ma.filled(npaMaskedData * (scale ** 2), float(self.dummy))))
        fabioOut.write(self.strNormalizedImage)
        self.lstProcessLog.append("Normalized image by factor %.3f " % (scale))


    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginBioSaxsNormalizev1_1.postProcess")

        if os.path.isfile(self.strNormalizedImage):
            xsNormFile = XSDataImage()
            xsNormFile.setPath(XSDataString(self.strNormalizedImage))
            self.xsdResult.setNormalizedImage(xsNormFile)
        self.xsdResult.status = XSDataStatus(executiveSummary=XSDataString(os.linesep.join(self.lstProcessLog)))
        # Create some output data
        self.setDataOutput(self.xsdResult)


    def doSuccessExecWaitFile(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsNormalizev1_1.doSuccessExecWaitFile")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginBioSaxsNormalizev1_1.doSuccessExecWaitFile")
        xsdOut = _edPlugin.getDataOutput()
        if (xsdOut.timedOut is not None) and (xsdOut.timedOut.value):
            strErr = "Timeout (%s s) in waiting for file %s" % (_edPlugin.getTimeOut(), self.strRawImage)
            self.ERROR(strErr)
            self.lstProcessLog.append(strErr)
            self.setFailure()
        else:
            self.log("EDPluginBioSaxsNormalizev1_1.WaitFile took %.3fs" % self.getRunTime())
            self.lstProcessLog.append("Normalizing EDF frame '%s' -> '%s'" % (self.strRawImage, self.strNormalizedImage))


    def doFailureExecWaitFile(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsNormalizev1_1.doFailureExecWaitFile")
        self.retrieveFailureMessages(_edPlugin, "EDPluginBioSaxsNormalizev1_1.doFailureExecWaitFile")
        self.lstProcessLog.append("Timeout in waiting for file '%s'.\n" % (self.strRawImage))
        self.setFailure()


    def configure(self):
        """
        Configures the plugin from the configuration file with the following parameters:
         - DummyPixelValue: the value to be assigned to dummy pixels.
        """
        EDPluginControl.configure(self)
        self.DEBUG("EDPluginBioSaxsNormalizev1_1.configure")
        xsPluginItem = self.getConfiguration()
        if (xsPluginItem == None):
            self.warning("EDPluginBioSaxsNormalizev1_1.configure: No plugin item defined.")
            xsPluginItem = XSPluginItem()
        self.dummy = EDConfiguration.getStringParamValue(xsPluginItem, self.CONF_DUMMY_PIXEL_VALUE)
        if self.dummy is None:
            strMessage = 'EDPluginBioSaxsNormalizev1_1.configure: %s Configuration parameter missing: \
%s, defaulting to "-1"' % (self.getBaseName(), self.CONF_DUMMY_PIXEL_VALUE)
            self.WARNING(strMessage)
            self.addErrorWarningMessagesToExecutiveSummary(strMessage)
            self.dummy = -1
#
#    @classmethod
#    def getMask(cls, _strFilename):
#        """
#        Retrieve the data from a file, featuring caching.
#        
#        @param _strFilename: name of the file
#        @return: numpy ndarray
#        
#        /!\ This is a class method (for the cache part)
#        """
#        if _strFilename not in cls.__maskfiles:
#            cls.__semaphore.acquire()
#            maskFile = fabio.open(_strFilename)
#            cls.__maskfiles[_strFilename] = maskFile.data
#            cls.__semaphore.release()
#        return cls.__maskfiles[_strFilename]


################################################################################
# EDPluginBioSaxsAzimutIntv1_3
################################################################################

import os
from EDUtilsArray           import EDUtilsArray
from EDPluginControl        import EDPluginControl
from EDFactoryPluginStatic  import EDFactoryPluginStatic
from EDUtilsPlatform        import EDUtilsPlatform
from EDUtilsPath            import EDUtilsPath
from XSDataCommon           import XSDataString, XSDataStatus, XSDataTime, XSDataFile, XSDataAngle, \
                                    XSDataDouble, XSDataInteger
from XSDataBioSaxsv1_0      import XSDataInputBioSaxsAzimutIntv1_0, XSDataResultBioSaxsAzimutIntv1_0, \
                                XSDataInputBioSaxsMetadatav1_0
EDFactoryPluginStatic.loadModule("XSDataWaitFilev1_0")
EDFactoryPluginStatic.loadModule("XSDataPyFAIv1_0")
from XSDataWaitFilev1_0     import XSDataInputWaitFile
from XSDataPyFAIv1_0        import XSDataInputPyFAI, XSDataDetector, XSDataGeometryFit2D
from EDUtilsParallel        import EDUtilsParallel
architecture = EDUtilsPlatform.architecture
fabioPath = os.path.join(EDUtilsPath.EDNA_HOME, "libraries", "FabIO-0.0.7", architecture)
imagingPath = os.path.join(EDUtilsPath.EDNA_HOME, "libraries", "20091115-PIL-1.1.7", architecture)
numpyPath = os.path.join(EDUtilsPath.EDNA_HOME, "libraries", "20090405-Numpy-1.3", architecture)

numpy = EDFactoryPluginStatic.preImport("numpy", numpyPath)
Image = EDFactoryPluginStatic.preImport("Image", imagingPath)
fabio = EDFactoryPluginStatic.preImport("fabio", fabioPath)
import pyFAI

class EDPluginBioSaxsAzimutIntv1_3(EDPluginControl):
    """
    Control for Bio Saxs azimuthal integration; suppose the mask is already applied by BioSaxsNormalizev1.1 :
    * wait for normalized file to arrive  (EDPluginWaitFile)
    * retrieve and update metadata (EDPluginBioSaxsMetadatav1_0)
    * integrate (directly vi pyFAI)
    * export as 3-column ascii-file is done here to allow more precise header
    Changelog since v1.2: use PyFAI instead of saxs_angle from Peter Boesecke
    """
    cpWaitFile = "EDPluginWaitFile"
    cpGetMetadata = "EDPluginBioSaxsMetadatav1_1"
    integrator = pyFAI.AzimuthalIntegrator()
    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsAzimutIntv1_0)
        self.__edPluginWaitFile = None
        self.__edPluginMetadata = None
        self.xsdMetadata = None
        self.sample = None
        self.experimentSetup = None
        self.normalizedImage = None
        self.integratedCurve = None
        self.normalizationFactor = None

        self.lstProcessLog = []
        self.npaOut = None
        self.xsdResult = XSDataResultBioSaxsAzimutIntv1_0()

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginBioSaxsAzimutIntv1_3.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.normalizedImage, "Missing normalizedImage")
        self.checkMandatoryParameters(self.dataInput.normalizedImageSize, "Missing normalizedImageSize")
        self.checkMandatoryParameters(self.dataInput.integratedCurve, "Missing integratedCurve")
        self.checkMandatoryParameters(self.dataInput.sample, "Missing a sample description")
        self.checkMandatoryParameters(self.dataInput.experimentSetup, "Missing an experiment setup")


    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        self.DEBUG("EDPluginBioSaxsAzimutIntv1_3.preProcess")
        # Load the execution plugins
        self.sample = self.dataInput.sample
        self.experimentSetup = self.dataInput.experimentSetup
        self.__edPluginWaitFile = self.loadPlugin(self.cpWaitFile)
        self.__edPluginMetadata = self.loadPlugin(self.cpGetMetadata)
        self.normalizedImage = self.dataInput.normalizedImage.path.value
        self.integratedCurve = self.dataInput.integratedCurve.path.value




