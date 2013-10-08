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
__date__ = "20130701"
__status__ = "development"

import os, time
from EDVerbose              import EDVerbose
from EDPluginControl        import EDPluginControl
from EDFactoryPlugin        import edFactoryPlugin
from EDThreading            import Semaphore
from EDUtilsUnit            import EDUtilsUnit
from EDUtilsArray           import EDUtilsArray
edFactoryPlugin.loadModule("XSDataEdnaSaxs")
edFactoryPlugin.loadModule("XSDataBioSaxsv1_0")
edFactoryPlugin.loadModule("XSDataWaitFilev1_0")
from XSDataWaitFilev1_0     import XSDataInputWaitFile
from XSDataBioSaxsv1_0      import XSDataInputBioSaxsProcessOneFilev1_0, XSDataResultBioSaxsProcessOneFilev1_0
from XSDataCommon           import XSDataStatus, XSDataString, XSDataFile, XSDataInteger, XSDataTime
import fabio
import numpy
import pyFAI

if pyFAI.version <= "0.8":
    EDVerbose.ERROR("Too old version of pyFAI detected ... expect to fail !")


class EDPluginBioSaxsProcessOneFilev1_4(EDPluginControl):
    """
    Control plugin that does the same as previously without sub-plugin call ...
    except WaitFile which is still called.

    Nota normalization is done AFTER integration not before as previously
    
    New in version 1.4: return I/Q/stderr via XSDataArrays 
    """
    cpWaitFile = "EDPluginWaitFile"
    integrator = pyFAI.AzimuthalIntegrator()
    integrator.wavelength = 1e-10
    CONF_DUMMY_PIXEL_VALUE = "DummyPixelValue"
    CONF_DUMMY_PIXEL_DELTA = "DummyPixelDelta"
    CONF_OPENCL_DEVICE = "DeviceType"
    __configured = False
    dummy = -2
    delta_dummy = 1.1
    semaphore = Semaphore()
    maskfile = None
    if pyFAI.opencl.ocl is None:
        METHOD = "lut"
    else:
        METHOD = "lut_ocl_gpu"

    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsProcessOneFilev1_0)
        self.__edPluginWaitFile = None
        self.rawImage = None
        self.rawImageSize = XSDataInteger(1024)
        self.normalizedImage = None
        self.integratedCurve = None
        self.integratedImage = None
        self.lstExecutiveSummary = []
        self.sample = None
        self.experimentSetup = None
        self.integrator_config = {}
        self.scale = None
        self.detector = None
        self.xsDataResult = XSDataResultBioSaxsProcessOneFilev1_0()


    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_4.checkParameters")
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
         - DeviceType: "lut_ocl_1,3" will select device #3 on first platform #1 
        """
        EDPluginControl.configure(self)
        if not self.__configured:
            with self.semaphore:
                if not self.__configured:
                    self.DEBUG("EDPluginBioSaxsProcessOneFilev1_4.configure")
                    dummy = self.config.get(self.CONF_DUMMY_PIXEL_VALUE)
                    if dummy is None:
                        strMessage = 'EDPluginBioSaxsProcessOneFilev1_4.configure: %s Configuration parameter missing: \
            %s, defaulting to "%s"' % (self.getBaseName(), self.CONF_DUMMY_PIXEL_VALUE, self.dummy)
                        self.WARNING(strMessage)
                        self.addErrorWarningMessagesToExecutiveSummary(strMessage)
                    else:
                        self.__class__.dummy = float(dummy)
                    ddummy = self.config.get(self.CONF_DUMMY_PIXEL_DELTA)
                    if ddummy is None:
                        strMessage = 'EDPluginBioSaxsProcessOneFilev1_4.configure: %s Configuration parameter missing: \
            %s, defaulting to "%s"' % (self.getBaseName(), self.CONF_DUMMY_PIXEL_DELTA, self.delta_dummy)
                        self.WARNING(strMessage)
                        self.addErrorWarningMessagesToExecutiveSummary(strMessage)
                    else:
                        self.__class__.delta_dummy = float(ddummy)
                    method = self.config.get(self.CONF_OPENCL_DEVICE)
                    if method is None:
                        strMessage = 'EDPluginBioSaxsProcessOneFilev1_4.configure: %s Configuration parameter missing: \
            %s, defaulting to "%s"' % (self.getBaseName(), self.CONF_OPENCL_DEVICE, self.METHOD)
                        self.WARNING(strMessage)
                        self.addErrorWarningMessagesToExecutiveSummary(strMessage)
                    else:
                        self.__class__.METHOD = method
                    self.__class__.__configured = True


    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_4.preProcess")
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
                # could occur in race condition ...
                pass

        self.sample = self.dataInput.sample
        self.experimentSetup = self.dataInput.experimentSetup
        self.detector = self.experimentSetup.detector.value
        if self.detector.lower() == "pilatus":
            self.detector = "Pilatus1M"
        else:
            self.detector = self.detector.capitalize()
        self.integrator_config = {'dist': self.experimentSetup.detectorDistance.value,
                                  'pixel1': self.experimentSetup.pixelSize_2.value, # flip X,Y
                                  'pixel2': self.experimentSetup.pixelSize_1.value, # flip X,Y
                                  'poni1': self.experimentSetup.beamCenter_2.value * self.experimentSetup.pixelSize_2.value,
                                  'poni2': self.experimentSetup.beamCenter_1.value * self.experimentSetup.pixelSize_1.value,
                                  'rot1': 0.0,
                                  'rot2': 0.0,
                                  'rot3': 0.0,
                                  'splineFile': None,
                                  'detector': self.detector
                                  }
        i0 = self.experimentSetup.beamStopDiode.value
        if i0 == 0:
            warn = "beamStopDiode is Null --> If we are testing, this is OK, else investigate !!!"
            self.lstExecutiveSummary.append(warn)
            self.warning(warn)
            self.scale = self.experimentSetup.normalizationFactor.value
        else:
            self.scale = self.experimentSetup.normalizationFactor.value / i0


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_4.process")

        xsd = XSDataInputWaitFile(expectedFile=XSDataFile(XSDataString(self.rawImage)),
                                           expectedSize=self.rawImageSize,
                                           timeOut=XSDataTime(30))
        self.__edPluginWaitFile.setDataInput(xsd)
        self.__edPluginWaitFile.connectSUCCESS(self.doSuccessWaitFile)
        self.__edPluginWaitFile.connectFAILURE(self.doFailureWaitFile)
        self.__edPluginWaitFile.executeSynchronous()
        if self.isFailure():
            return

        self.xsDataResult.sample = self.sample
        self.xsDataResult.experimentSetup = self.experimentSetup

        q, I, std = self.integrate()
        I = self.normalize(I)
        std = self.normalize(std)
        self.write3ColumnAscii(q, I, std, self.integratedCurve)
        self.xsDataResult.dataQ = EDUtilsArray.arrayToXSData(q)
        self.xsDataResult.dataI = EDUtilsArray.arrayToXSData(I)
        self.xsDataResult.dataStdErr = EDUtilsArray.arrayToXSData(std)

    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_4.postProcess")
        # Create some output data
        if os.path.exists(self.integratedCurve):
            self.xsDataResult.integratedCurve = XSDataFile(XSDataString(self.integratedCurve))

        self.xsDataResult.status = XSDataStatus(executiveSummary=XSDataString(os.linesep.join(self.lstExecutiveSummary)))
        self.setDataOutput(self.xsDataResult)

    def integrate(self):
        img = fabio.open(self.rawImage)
        if "Date" in img.header:
            self.experimentSetup.timeOfFrame = XSDataTime(time.mktime(time.strptime(img.header["Date"], "%a %b %d %H:%M:%S %Y")))
        wavelength = EDUtilsUnit.getSIValue(self.experimentSetup.wavelength)
        current_config = self.integrator.getPyFAI()
        short_config = {}
        for key in self.integrator_config:
            short_config[key] = current_config[key]

        with self.__class__.semaphore:
            if (short_config != self.integrator_config) or \
               (self.integrator.wavelength != wavelength) or\
               (self.maskfile != self.experimentSetup.maskFile.path.value):
                self.screen("Resetting PyFAI integrator")
                self.integrator.setPyFAI(**self.integrator_config)
                self.integrator.wavelength = wavelength
                self.integrator.detector.mask = self.calc_mask()

            q, I, std = self.integrator.integrate1d(data=img.data, nbPt=max(img.dim1, img.dim2),
                                       correctSolidAngle=True,
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

        detector_mask = pyFAI.detectors.detector_factory(self.detector).calc_mask()
        shape0, shape1 = detector_mask.shape
        if detector_mask.shape == mask.shape:
            mask = numpy.logical_or(mask, detector_mask)
        else:
            # crop the user defined mask
            mask = numpy.logical_or(mask[:shape0, :shape1], detector_mask)
        self.__class__.maskfile = self.experimentSetup.maskFile.path.value
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
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_4.doSuccessWaitFile")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginBioSaxsProcessOneFilev1_4.doSuccessWaitFile")

    def doFailureWaitFile(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsProcessOneFilev1_4.doFailureWaitFile")
        self.retrieveFailureMessages(_edPlugin, "EDPluginBioSaxsProcessOneFilev1_4.doFailureWaitFile")
        self.lstExecutiveSummary.append("Timeout in waiting for file '%s'" % (self.rawImage))
        self.setFailure()



