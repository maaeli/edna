# coding: utf-8
#
#    Project:BioSaxs
#             http://www.edna-site.org
#
#    Copyright (C) 2014 ESRF
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
__copyright__ = "2014 ESRF"
__date__ = "20140903"
__status__ = "development"

import os
import fabio
import numpy
from EDPluginControl import EDPluginControl
from EDThreading import Semaphore

from EDFactoryPlugin import edFactoryPlugin
edFactoryPlugin.loadModule("XSDataBioSaxsv1_0")
edFactoryPlugin.loadModule("XSDataEdnaSaxs")
from XSDataBioSaxsv1_0 import XSDataInputBioSaxsHPLCv1_0, XSDataResultBioSaxsHPLCv1_0, \
                            XSDataInputBioSaxsProcessOneFilev1_0, XSDataRamboTainer
from XSDataEdnaSaxs import XSDataInputDatcmp, XSDataInputDataver, XSDataInputDatop, XSDataInputAutoRg
from XSDataCommon import XSDataFile, XSDataString, XSDataStatus, XSDataTime, \
    XSDataDouble

from EDUtilsBioSaxs import HPLCframe, HPLCrun, RamboTainerInvariant




class EDPluginBioSaxsHPLCv1_3(EDPluginControl):
    """
    plugin for processing Saxs data coming from HPLC

    runs subsequently:
    *ProcessOneFile,
    *subtraction of buffer
    *AutoRg

    todo:
    only store references: Wait for flush to construct HDF5 file and (possibly) web pages with PNG graphs
    
    Changes since v1.0:
    * do not perfom Gnom not Porod analysis
    * return Summed Intensity and time stamp
    * fix issue with timestamp.
    Changes since v1.1:
    * Read configuration for a buffer threshold 
    Changes since v1.2:
    lock during buffer curve creation.
    """

    strControlledPluginProcessOneFile = "EDPluginBioSaxsProcessOneFilev1_4"
    strControlledPluginDatop = "EDPluginExecDatopv2_0"
    strControlledPluginAutoRg = "EDPluginExecAutoRgv1_0"
    strControlledPluginDatCmp = "EDPluginExecDatcmpv2_0
    strControlledPluginDatAver = "EDPluginExecDataverv2_0"
    dictHPLC = {}  # key=runId, value= HPLCrun instance
    _sem = Semaphore()
    buffer_sem = Semaphore()
    SIMILARITY_THRESHOLD_SAMPLE_KEY = "similaritySample"
    SIMILARITY_THRESHOLD_BUFFER_KEY = "similarityBuffer"
    SIMILARITY_THRESHOLD_SAMPLE_DEFAULT = 0.0
    SIMILARITY_THRESHOLD_BUFFER_DEFAULT = 0.1
    SIMILARITY_THRESHOLD_SAMPLE = None
    SIMILARITY_THRESHOLD_BUFFER = None

    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsHPLCv1_0)
        self.edPluginProcessOneFile = None
        self.edPluginSubtract = None
        self.edPluginAutoRg = None
        self.edPluginDatCmp = None
        self.xsDataResult = XSDataResultBioSaxsHPLCv1_0()
        self.runId = None
        self.frameId = None
        self.frame = None
        self.hplc_run = None
        self.curve = None
        self.subtracted = None
        self.lstExecutiveSummary = []
        self.isBuffer = False
        self.scatter_data = None

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.rawImage, "No raw image")
        self.checkMandatoryParameters(self.dataInput.sample, "no Sample parameter")
        self.checkMandatoryParameters(self.dataInput.experimentSetup, "No experimental setup parameter")

    def configure(self):
        """
        Configures the HPLC plugin by reading from the configuration file 
         - The threshold for similarity with sample & buffer
        """
        EDPluginControl.configure(self)
        if self.__class__.SIMILARITY_THRESHOLD_SAMPLE is None:
            with self._sem:
                if self.__class__.SIMILARITY_THRESHOLD_SAMPLE is None:
                    self.DEBUG("EDPluginBioSaxsHPLCv1_3.configure")
                    self.__class__.SIMILARITY_THRESHOLD_BUFFER = float(self.config.get(self.SIMILARITY_THRESHOLD_BUFFER_KEY, self.SIMILARITY_THRESHOLD_BUFFER_DEFAULT))
                    self.__class__.SIMILARITY_THRESHOLD_SAMPLE = float(self.config.get(self.SIMILARITY_THRESHOLD_SAMPLE_KEY, self.SIMILARITY_THRESHOLD_SAMPLE_DEFAULT))

    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.preProcess")
        sdi = self.dataInput
        if sdi.runId is not None:
            self.runId = sdi.runId.value
        else:
            path = sdi.rawImage.path.value
            if "_" in path:
                self.runId = path[::-1].split("_", 1)[1][::-1]
            else:
                self.runId = path
        with self._sem:
            if self.runId not in self.dictHPLC:
                self.dictHPLC[self.runId] = HPLCrun(self.runId)
        self.hplc_run = self.dictHPLC[self.runId]
        if sdi.frameId is not None:
            self.frameId = sdi.frameId.value
        else:
            path = sdi.rawImage.path.value
            if "_" in path:
                digits = os.path.splitext(os.path.basename(path))[0].split("_")[-1]
                try:
                    self.frameId = int(digits)
                except ValueError:
                    self.WARNING("frameId is supposed to be an integer, I got %s" % digits)
                    self.frameId = digits
            else:
                self.warning("using frameID=0 in tests, only")
                self.frameId = 0
        with self._sem:
            self.frame = HPLCframe(self.runId, self.frameId)
            self.hplc_run.frames[self.frameId] = self.frame

        if sdi.bufferCurve and os.path.exists(sdi.bufferCurve.path.value):
            with self._sem:
                self.hplc_run.buffer = sdi.bufferCurve.path.value

        if self.hplc_run.hdf5_filename:
            hplc = self.hplc_run.hdf5_filename
        elif sdi.hplcFile:
            hplc = sdi.hplcFile.path.value
        else:
            path = sdi.rawImage.path.value
            dirname = os.path.dirname(os.path.dirname(path))
            hplc_dir = os.path.join(dirname, "HPLC")
            if not os.path.exists(hplc_dir):
                try:
                    os.mkdir(hplc_dir)
                except:
                    pass  # I don't care

            if "_" in path:
                hplc = "_".join(os.path.splitext(os.path.basename(path))[0].split("_")[:-1]) + ".h5"
            else:
                hplc = os.path.splitext(os.path.basename(path))[0] + ".h5"
            hplc = os.path.join(hplc_dir, hplc)
        if not self.hplc_run.hdf5_filename:
            with self._sem:
                self.hplc_run.init_hdf5(hplc)
#        self.xsDataResult.hplcFile = XSDataFile(XSDataString(hplc))

    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.process")

        xsdIn = XSDataInputBioSaxsProcessOneFilev1_0(rawImage=self.dataInput.rawImage,
                                                     sample=self.dataInput.sample,
                                                     experimentSetup=self.dataInput.experimentSetup,
                                                     rawImageSize=self.dataInput.rawImageSize,
                                                     normalizedImage=self.dataInput.normalizedImage,
                                                     integratedCurve=self.dataInput.integratedCurve,
                                                     runId=self.dataInput.runId,
                                                     frameId=self.dataInput.frameId)
        self.edPluginProcessOneFile = self.loadPlugin(self.strControlledPluginProcessOneFile)
        self.edPluginProcessOneFile.dataInput = xsdIn
        self.edPluginProcessOneFile.connectSUCCESS(self.doSuccessProcessOneFile)
        self.edPluginProcessOneFile.connectFAILURE(self.doFailureProcessOneFile)
        self.edPluginProcessOneFile.executeSynchronous()

        if self.isFailure():
            return

        xsdIn = XSDataInputDatcmp(inputCurve=[XSDataFile(XSDataString(self.hplc_run.first_curve)),
                                              XSDataFile(XSDataString(self.curve))])
        self.edPluginDatCmp = self.loadPlugin(self.strControlledPluginDatCmp)
        self.edPluginDatCmp.dataInput = xsdIn
        self.edPluginDatCmp.connectSUCCESS(self.doSuccessDatCmp)
        self.edPluginDatCmp.connectFAILURE(self.doFailureDatCmp)
        self.edPluginDatCmp.executeSynchronous()

        if self.isFailure() or self.isBuffer:
            return

        if self.dataInput.subtractedCurve is not None:
            subtracted = self.dataInput.subtractedCurve.path.value
        else:
            subtracted = os.path.splitext(self.curve)[0] + "_sub.dat"
        if self.hplc_run.buffer is not None:
            xsdIn = XSDataInputDatop(inputCurve=[XSDataFile(XSDataString(self.curve)),
                                                  XSDataFile(XSDataString(self.hplc_run.buffer))],
                                     outputCurve=XSDataFile(XSDataString(subtracted)),
                                     operation=XSDataString("sub"))
        else:
            xsdIn = XSDataInputDatop(inputCurve=[XSDataFile(XSDataString(self.curve)),
                                                  XSDataFile(XSDataString(self.hplc_run.first_curve))],
                                     outputCurve=XSDataFile(XSDataString(subtracted)),
                                     operation=XSDataString("sub"))
        self.edPluginDatop = self.loadPlugin(self.strControlledPluginDatop)
        self.edPluginDatop.dataInput = xsdIn
        self.edPluginDatop.connectSUCCESS(self.doSuccessDatop)
        self.edPluginDatop.connectFAILURE(self.doFailureDatop)
        self.edPluginDatop.executeSynchronous()

        if self.subtracted and os.path.exists(self.subtracted):
            self.edPluginAutoRg = self.loadPlugin(self.strControlledPluginAutoRg)
            self.edPluginAutoRg.dataInput = XSDataInputAutoRg(inputCurve=[XSDataFile(XSDataString(self.subtracted))])
            self.edPluginAutoRg.connectSUCCESS(self.doSuccessAutoRg)
            self.edPluginAutoRg.connectFAILURE(self.doFailureAutoRg)
            self.edPluginAutoRg.executeSynchronous()

    def postProcess(self, _edObject=None):
        """
        after process
        """
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.postProcess")
        if self.hplc_run.buffer:
            self.xsDataResult.bufferCurve = XSDataFile(XSDataString(self.hplc_run.buffer))
        if self.curve:
            self.xsDataResult.integratedCurve = XSDataFile(XSDataString(self.curve))
        if self.subtracted:
            self.xsDataResult.subtractedCurve = XSDataFile(XSDataString(self.subtracted))

    def finallyProcess(self, _edObject=None):
        EDPluginControl.finallyProcess(self)
        executiveSummary = os.linesep.join(self.lstExecutiveSummary)
        self.xsDataResult.status = XSDataStatus(executiveSummary=XSDataString(executiveSummary))
        self.dataOutput = self.xsDataResult
        if self.frame:
            self.frame.processing = False

    def average_buffers(self):
        """
        Average out all buffers
        """
        self.lstExecutiveSummary.append("Averaging out buffer files: " + ", ".join(self.hplc_run.for_buffer))
        xsdIn = XSDataInputDataver(inputCurve=[XSDataFile(XSDataString(i)) for i in self.hplc_run.for_buffer])
        if self.dataInput.bufferCurve:
            xsdIn.outputCurve = self.dataInput.bufferCurve
        else:
            xsdIn.outputCurve = XSDataFile(XSDataString(self.hplc_run.first_curve[::-1].split("_", 1)[1][::-1] + "_buffer_aver_%04i.dat" % len(self.hplc_run.for_buffer)))
        self.edPluginDatAver = self.loadPlugin(self.strControlledPluginDatAver)
        self.edPluginDatAver.dataInput = xsdIn
        self.edPluginDatAver.connectSUCCESS(self.doSuccessDatAver)
        self.edPluginDatAver.connectFAILURE(self.doFailureDatAver)
        self.edPluginDatAver.executeSynchronous()

    def doSuccessProcessOneFile(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doSuccessProcessOneFile")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doSuccessProcessOneFile")
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.status and _edPlugin.dataOutput.status.executiveSummary:
            self.lstExecutiveSummary.append(_edPlugin.dataOutput.status.executiveSummary.value)
        output = _edPlugin.dataOutput
        if not output.integratedCurve:
            strErr = "Edna plugin ProcessOneFile did not produce integrated curve"
            self.ERROR(strErr)
            self.lstExecutiveSummary.append(strErr)
            self.setFailure()
            return
        self.curve = output.integratedCurve.path.value
        if not os.path.exists(self.curve):
            strErr = "Edna plugin ProcessOneFile: integrated curve not on disk !!"
            self.ERROR(strErr)
            self.lstExecutiveSummary.append(strErr)
            self.setFailure()
            return
        self.xsDataResult.integratedCurve = output.integratedCurve
        self.xsDataResult.normalizedImage = output.normalizedImage
        self.xsDataResult.dataI = output.dataI
        self.xsDataResult.dataQ = output.dataQ
        self.xsDataResult.dataStdErr = output.dataStdErr
        if output.experimentSetup and output.experimentSetup.timeOfFrame:
            startTime = output.experimentSetup.timeOfFrame.value
        else:
            try:
                startTime = float(fabio.openheader(self.dataInput.rawImage.path.value).header["time_of_day"])
            except Exception:
                self.ERROR("Unable to read time_of_day in header of %s" % self.dataInput.rawImage.path.value)
                startTime = 0

        with self._sem:
            if not self.hplc_run.first_curve:
                self.hplc_run.first_curve = self.curve
                self.hplc_run.start_time = startTime
        self.frame.curve = self.curve
        self.frame.time = startTime
        self.xsDataResult.timeStamp = XSDataTime(value=(startTime - self.hplc_run.start_time))
        self.calcIntensity()

    def doFailureProcessOneFile(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doFailureProcessOneFile")
        self.retrieveFailureMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doFailureProcessOneFile")
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.status and _edPlugin.dataOutput.status.executiveSummary:
            self.lstExecutiveSummary.append(_edPlugin.dataOutput.status.executiveSummary.value)
        else:
            self.lstExecutiveSummary.append("Edna plugin ProcessOneFile failed.")
        self.setFailure()

    def doSuccessDatop(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doSuccessDatop")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doSuccessDatop")
        if _edPlugin and _edPlugin.dataOutput:
            output = _edPlugin.dataOutput
            if output.status and output.status.executiveSummary:
                self.lstExecutiveSummary.append(output.status.executiveSummary.value)
            if output.outputCurve:
                self.subtracted = output.outputCurve.path.value
                if os.path.exists(self.subtracted):
                    self.xsDataResult.subtractedCurve = output.outputCurve
                    self.frame.subtracted = self.subtracted
                else:
                    strErr = "Edna plugin datop did not produce subtracted file %s" % self.subtracted
                    self.ERROR(strErr)
                    self.lstExecutiveSummary.append(strErr)
                    self.setFailure()

    def doFailureDatop(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doFailureDatop")
        self.retrieveFailureMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doFailureDatop")
        strErr = "Edna plugin datop failed."
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.status and _edPlugin.dataOutput.status.executiveSummary:
            self.lstExecutiveSummary.append(_edPlugin.dataOutput.status.executiveSummary.value)
        else:
            self.lstExecutiveSummary.append(strErr)
        self.ERROR(strErr)
        self.setFailure()

    def doSuccessAutoRg(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doSuccessAutoRg")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doSuccessAutoRg")
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.status and _edPlugin.dataOutput.status.executiveSummary:
            self.lstExecutiveSummary.append(_edPlugin.dataOutput.status.executiveSummary.value)
        try:
            rg = _edPlugin.dataOutput.autoRgOut[0]
        except:
            self.ERROR("AutoRg returned nothing !")
        else:
            if rg.rg:
                self.frame.Rg = rg.rg.value
            if rg.rgStdev:
                self.frame.Rg_Stdev = rg.rgStdev.value
            if rg.i0:
                self.frame.I0 = rg.i0.value
            if rg.i0Stdev:
                self.frame.I0_Stdev = rg.i0Stdev.value
            if rg.quality:
                self.frame.quality = rg.quality.value
            self.xsDataResult.autoRg = rg

        """
        Calculate the invariants Vc and Qr from the Rambo&Tainer 2013 Paper,
        also the the mass estimate based on Qr for proteins
        """
        if self.subtracted and os.path.exists(self.subtracted):
            self.subtracted_data = numpy.loadtxt(self.subtracted)
            if self.subtracted_data is not None and\
                self.frame.Rg and self.frame.Rg_Stdev and self.frame.I0 and self.frame.I0_Stdev:
                dictRTI = RamboTainerInvariant(self.subtracted_data, self.frame.Rg,
                                               self.frame.Rg_Stdev, self.frame.I0,
                                               self.frame.I0_Stdev, rg.firstPointUsed.value)
#             {'Vc': vc[0], 'dVc': vc[1], 'Qr': qr, 'dQr': dqr, 'mass': mass, 'dmass': dmass}
                self.frame.Vc = dictRTI.get("Vc")
                self.frame.Vc_Stdev = dictRTI.get("dVc")
                self.frame.Qr = dictRTI.get("Qr")
                self.frame.Qr_Stdev = dictRTI.get("dQ")
                self.frame.mass = dictRTI.get("mass")
                self.frame.mass_Stdev = dictRTI.get("dmass")
                xsdRTI = XSDataRamboTainer(vc=XSDataDouble(self.frame.Vc),
                                           qr=XSDataDouble(self.frame.Qr),
                                           mass=XSDataDouble(self.frame.mass),
                                           dvc=XSDataDouble(self.frame.Vc_Stdev),
                                           dqr=XSDataDouble(self.frame.Qr_Stdev),
                                           dmass=XSDataDouble(self.frame.mass_Stdev))
                self.xsDataResult.rti = xsdRTI

    def doFailureAutoRg(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doFailureAutoRg")
        self.retrieveFailureMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doFailureAutoRg")
        strErr = "Edna plugin AutoRg failed."
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.status and _edPlugin.dataOutput.status.executiveSummary:
            self.lstExecutiveSummary.append(_edPlugin.dataOutput.status.executiveSummary.value)
            self.lstExecutiveSummary.append(strErr)
        else:
            self.lstExecutiveSummary.append(strErr)
        self.setFailure()

    def doSuccessDatCmp(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doSuccessDatCmp")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doSuccessDatCmp")
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.status and _edPlugin.dataOutput.status.executiveSummary:
            self.lstExecutiveSummary.append(_edPlugin.dataOutput.status.executiveSummary.value)
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.fidelity:
            fidelity = _edPlugin.dataOutput.fidelity.value
        else:
            strErr = "No fidelity in output of datcmp"
            self.error(strErr)
            self.lstExecutiveSummary.append(strErr)
            #  self.setFailure()
            fidelity = 0
        if self.hplc_run.buffer is None:
            if fidelity > self.SIMILARITY_THRESHOLD_SAMPLE:
                self.isBuffer = True
                if fidelity > self.SIMILARITY_THRESHOLD_BUFFER:
                    self.hplc_run.for_buffer.append(self.curve)
            else:
                with self.buffer_sem:
                    if self.hplc_run.buffer is None:
                        self.average_buffers()
        elif fidelity > self.SIMILARITY_THRESHOLD_SAMPLE:
            self.isBuffer = True

    def doFailureDatCmp(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doFailureDatCmp")
        self.retrieveFailureMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doFailureDatCmp")
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.status and _edPlugin.dataOutput.status.executiveSummary:
            self.lstExecutiveSummary.append(_edPlugin.dataOutput.status.executiveSummary.value)
        else:
            self.lstExecutiveSummary.append("Edna plugin DatCmp failed.")
        self.setFailure()

    def doSuccessDatAver(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doSuccessDatAver")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doSuccessDatAver")
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.outputCurve:
            bufferCurve = _edPlugin.dataOutput.outputCurve.path.value
            if os.path.exists(bufferCurve):
                with self._sem:
                    self.hplc_run.buffer = bufferCurve
            else:
                strErr = "DatAver claimed buffer is in %s but no such file !!!" % bufferCurve
                self.ERROR(strErr)
                self.lstExecutiveSummary.append(strErr)
                self.setFailure()

    def doFailureDatAver(self, _edPlugin=None):
        self.DEBUG("EDPluginBioSaxsHPLCv1_3.doFailureDatAver")
        self.retrieveFailureMessages(_edPlugin, "EDPluginBioSaxsHPLCv1_3.doFailureDatAver")
        if _edPlugin and _edPlugin.dataOutput and _edPlugin.dataOutput.status and _edPlugin.dataOutput.status.executiveSummary:
            self.lstExecutiveSummary.append(_edPlugin.dataOutput.status.executiveSummary.value)
        else:
            self.lstExecutiveSummary.append("Edna plugin DatAver failed.")
        self.setFailure()

    def calcIntensity(self):
        """
        Calculate invarients like:
        Sum(I),
        and set output datastructure.
        
        """
        self.scatter_data = numpy.loadtxt(self.xsDataResult.integratedCurve.path.value)
        self.frame.sum_I = self.scatter_data[:, 1].sum()
        self.xsDataResult.summedIntensity = XSDataDouble(value=self.frame.sum_I)

