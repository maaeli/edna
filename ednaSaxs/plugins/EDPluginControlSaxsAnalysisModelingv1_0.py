# coding: utf8
#
#    Project: Edna Saxs
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) 2012 ESRF
#
#    Principal author: Jerome Kieffer
#
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

__authors__ = ["Jérôme Kieffer"]
__license__ = "GPLv3+"
__copyright__ = "ESRF"
__date__ = "2013-04-16"
__status__ = "Development"

import os
from EDPluginControl import EDPluginControl
from XSDataEdnaSaxs import XSDataInputSaxsAnalysisModeling, XSDataResultSaxsAnalysisModeling, \
                           XSDataInputSaxsAnalysis, XSDataInputSaxsModeling
from XSDataCommon import XSDataString, XSDataStatus


class EDPluginControlSaxsAnalysisModelingv1_0(EDPluginControl):
    """
    Executes the pipeline:
    - Saxs Analysis
        * AutoRg -> Extract the Guinier region and measure Rg, I0
        * DatGnom -> transformation from reciprocal to direct space. measure Dmax.
        * DatPorod -> calculates the volume of the protein using the porod formula.
    - Saxs Modeling
        * Dammif
        * Supcomb
        * Damaver
        * Damfilt
        * Damstart
        * Dammin
    """
    cpAnalysis = "EDPluginControlSaxsAnalysisv1_0"
    cpModeling = "EDPluginControlSaxsModelingv1_0"

    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputSaxsAnalysisModeling)
        self.edPluginAnalysis = None
        self.edPluginModeling = None
        self.scatterFile = None
        self.gnomFile = None
        self.autoRg = None
        self.gnom = None
        self.xVolume = None
        self.xsDataResult = XSDataResultSaxsAnalysisModeling()

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginControlSaxsAnalysisModelingv1_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.scatterCurve, "No scattering curve provided")


    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        self.DEBUG("EDPluginControlSaxsAnalysisModelingv1_0.preProcess")
        self.scatterFile = self.dataInput.scatterCurve.path.value
        if self.dataInput.gnomFile is not None:
            self.gnomFile = self.dataInput.gnomFile.path.value
        else:
            self.gnomFile = os.path.join(self.getWorkingDirectory(), os.path.basename(self.scatterFile).split(".")[0] + ".out")
        self.autoRg = self.dataInput.autoRg


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginControlSaxsAnalysisModelingv1_0.process")
        if (self.autoRg is None) or (self.gnomFile is None):
            self.edPluginAnalysis = self.loadPlugin(self.cpAnalysis)
            self.edPluginAnalysis.dataInput = XSDataInputSaxsAnalysis(scatterCurve=self.dataInput.scatterCurve,
                                                                    autoRg=self.dataInput.autoRg,
                                                                    gnomFile=self.dataInput.gnomFile,
                                                                    graphFormat=self.dataInput.graphFormat)
            self.edPluginAnalysis.connectSUCCESS(self.doSuccessAnalysis)
            self.edPluginAnalysis.connectFAILURE(self.doFailureAnalysis)
            self.edPluginAnalysis.executeSynchronous()

        if self.isFailure():
            return
        else:
            strLog = """Rg   =   %.2f +/- %2f
I(0) =   %.2e +/- %.2e
Points   %i to %i
Quality: %4.2f%%     Aggregated: %s""" % (self.autoRg.rg.value, self.autoRg.rgStdev.value,
                        self.autoRg.i0.value, self.autoRg.i0Stdev.value,
                        self.autoRg.firstPointUsed.value, self.autoRg.lastPointUsed.value,
                        self.autoRg.quality.value * 100., self.autoRg.isagregated.value)
        if self.gnom is None:
            strLog += """
datGnom failed"""
        else:
            strLog += """
Dmax    =    %12.2f       Total =   %12.2f
Guinier =    %12.2f       Gnom =    %12.2f""" % (self.gnom.dmax.value, self.gnom.total.value,
                        self.gnom.rgGuinier.value, self.gnom.rgGnom.value)
        if self.xVolume is None:
            strLog += """
datPorod failed"""
        else:
            strLog += """
Volume  =    %12.2f""" % (self.xVolume.value)

            self.addExecutiveSummaryLine(strLog)

        self.edPluginModeling = self.loadPlugin(self.cpModeling)
        self.edPluginModeling.dataInput = XSDataInputSaxsModeling(gnomFile=self.gnom.gnomFile,
                                                                  graphFormat=self.dataInput.graphFormat)
        self.edPluginModeling.connectSUCCESS(self.doSuccessModeling)
        self.edPluginModeling.connectFAILURE(self.doFailureModeling)
        self.edPluginModeling.executeSynchronous()


    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginControlSaxsAnalysisModelingv1_0.postProcess")
        # Create some output data

        self.xsDataResult.autoRg = self.autoRg
        self.xsDataResult.gnom = self.gnom
        self.xsDataResult.volume = self.xVolume
        self.xsDataResult.status = XSDataStatus(message=self.getXSDataMessage(),
                                          executiveSummary=XSDataString(os.linesep.join(self.getListExecutiveSummaryLines())))

        self.setDataOutput(self.xsDataResult)


    def doSuccessAnalysis(self, _edPlugin=None):
        self.DEBUG("EDPluginControlSaxsAnalysisModelingv1_0.doSuccessAnalysis")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginControlSaxsAnalysisModelingv1_0.doSuccessAnalysis")
        self.retrieveMessages(_edPlugin)
        try:
            self.autoRg = _edPlugin.dataOutput.autoRg
            self.gnom = _edPlugin.dataOutput.gnom
            self.gnomFile = self.gnom.gnomFile.path.value
            self.xVolume = _edPlugin.dataOutput.volume
            self.xsDataResult.scatterPlot= _edPlugin.dataOutput.scatterPlot
            self.xsDataResult.guinierPlot= _edPlugin.dataOutput.guinierPlot
            self.xsDataResult.kratkyPlot= _edPlugin.dataOutput.kratkyPlot
            self.xsDataResult.densityPlot=_edPlugin.dataOutput.densityPlot

        except Exception as error:
            self.ERROR("Error in doSuccessAnalysis: %s" % error)
            if self.gnomFile is None:
                self.setFailure()


    def doFailureAnalysis(self, _edPlugin=None):
        self.DEBUG("EDPluginControlSaxsAnalysisModelingv1_0.doFailureAnalysis")
        self.retrieveFailureMessages(_edPlugin, "EDPluginControlSaxsAnalysisModelingv1_0.doFailureAnalysis")
        self.retrieveMessages(_edPlugin)
        self.setFailure()

    def doSuccessModeling(self, _edPlugin=None):
        self.DEBUG("EDPluginControlSaxsAnalysisModelingv1_0.doSuccessModeling")
        self.retrieveSuccessMessages(_edPlugin, "EDPluginControlSaxsAnalysisModelingv1_0.doSuccessModeling")
        self.retrieveMessages(_edPlugin)
        try:    
            self.xsDataResult.dammifModels = _edPlugin.dataOutput.dammifModels
            self.xsDataResult.damaverModel = _edPlugin.dataOutput.damaverModel
            self.xsDataResult.damfiltModel = _edPlugin.dataOutput.damfiltModel
            self.xsDataResult.damstartModel = _edPlugin.dataOutput.damstartModel
            self.xsDataResult.damminModel = _edPlugin.dataOutput.damminModel
            self.xsDataResult.chiRfactorPlot = _edPlugin.dataOutput.chiRfactorPlot
            self.xsDataResult.nsdPlot = _edPlugin.dataOutput.nsdPlot

            self.xsDataResult.fitFile = _edPlugin.dataOutput.fitFile
            self.xsDataResult.logFile = _edPlugin.dataOutput.logFile
            self.xsDataResult.pdbMoleculeFile = _edPlugin.dataOutput.pdbMoleculeFile
            self.xsDataResult.pdbSolventFile = _edPlugin.dataOutput.pdbSolventFile

        except Exception as error:
            self.ERROR("Error in doSuccessModeling: %s" % error)

    def doFailureModeling(self, _edPlugin=None):
        self.DEBUG("EDPluginControlSaxsAnalysisModelingv1_0.doFailureModeling")
        self.retrieveFailureMessages(_edPlugin, "EDPluginControlSaxsAnalysisModelingv1_0.doFailureModeling")
        self.retrieveMessages(_edPlugin)
        self.setFailure()
