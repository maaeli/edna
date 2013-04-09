# coding: utf8
#
#    Project: PROJECT
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
__status__ = "developement"

import os
from EDThreading import Semaphore
from EDPluginControl import EDPluginControl
from XSDataCommon import XSDataStatus, XSDataString
from XSDataEdnaSaxs import XSDataInputSaxsModeling, XSDataResultSaxsModeling, XSDataInputDammif
#from EDFactoryPlugin import edFactoryPlugin
#edFactoryPlugin.loadModule('XSDataBioSaxsv1_0')
#from XSDataBioSaxsv1_0 import XSDataInputBioSaxsReduceFileSeriev1_0


class EDPluginControlSaxsModelingv1_0(EDPluginControl):
    """
    Basically this is a re-implementation of EDPluginControlSolutionScattering starting after Gnom and withou web page generation
    """
    classlock = Semaphore()
    configured = False
    dammif_jobs = 10     # number of dammif job to run
    unit = "NANOMETER"   # unit of the GNOM file
    symmetry = "P1"      #
    mode = "fast"        #
    # constants:  plugin names
    strPluginExecDammif = "EDPluginExecDammifv0_1"
    strPluginExecSupcomb = "EDPluginExecSupcombv0_1"
    strPluginExecDamaver = "EDPluginExecDamaverv0_1"
    strPluginExecDamfilt = "EDPluginExecDamfiltv0_1"
    strPluginExecDamstart = "EDPluginExecDamstartv0_1"

    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputSaxsModeling)
        self.edPlugin = None
        self.edPlugin = None
        self.xsGnomFile = None
        self.result = XSDataResultSaxsModeling()
        self.summary = []
        self.graph_format = "png"
        self.damif_plugins = []


    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginControlSaxsModelingv1_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.gnomFile, "gnom output is missing")

    def configure(self):
        if not self.configured:
            with self.classlock:
                if not self.configured:
                    EDPluginControl.configure(self)
                    dammif_jobs = self.config.get("dammifJobs", None)
                    if (dammif_jobs != None):
                        self.__class__.dammif_jobs = int(dammif_jobs)
                        self.DEBUG("EDPluginControlSaxsModelingv1_0.configure: setting number of dammif jobs to %d" % self.dammif_jobs)
                    unit = self.config.get("unit", None)
                    if (unit != None):
                        self.__class__.unit = unit.upper()
                        self.DEBUG("EDPluginControlSaxsModelingv1_0.configure: setting input units to %s" % self.unit)
                    symmetry = self.config.get("symmetry", None)
                    if (symmetry != None):
                        self.__class__.symmetry = symmetry
                        self.DEBUG("EDPluginControlSaxsModelingv1_0.configure: setting symmetry to %s" % self.symmetry)
                    mode = self.config.get("mode", None)
                    if (mode != None):
                        self.__class__.mode = mode
                        self.DEBUG("EDPluginControlSaxsModelingv1_0.configure: setting dammif mode to %s" % self.mode)

                    self.__class__.configured = True

    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        self.DEBUG("EDPluginControlSaxsModelingv1_0.preProcess")
        self.xsGnomFile = self.dataInput.gnomFile
        if self.dataInput.graphFormat:
            self.graph_format = self.dataInput.graphFormat.value
        # Load the execution plugin
#        self.__edPluginBioSaxsReduce = self.loadPlugin(self.__strControlledPluginReduce)
#        self.__edPluginExecAutoRg = self.loadPlugin(self.__strControlledPluginAutoRg)


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginControlSaxsModelingv1_0.process")
        xsDataInputDammif = XSDataInputDammif(gnomOutputFile=self.xsGnomFile,
                                              unit=XSDataString(self.unit),
                                              symmetry=XSDataString(self.symmetry),
                                              mode=XSDataString(self.mode))
        for i in range(self.dammif_jobs):
            damif = self.loadPlugin(self.strPluginExecDammif)
            damif.setDataInput(xsDataInputDammif)
            self.addPluginToActionCluster(damif)
            self.damif_plugins.append(damif)
        self.executeActionCluster()
        self.synchronizeActionCluster()
        for plugin in self.damif_plugins:
            if plugin.isFailure():
                self.setFailure()
            self.retrieveMessages(plugin)
        if self.isFailure():
            return
        damif = self.bestDammif()
        print damif.dataOutput.marshal()


    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginControlSaxsModelingv1_0.postProcess")
        # clean up memory
        self.damif_plugins = []
        # Create some output data


    def finallyProcess(self, _edObject=None):
        EDPluginControl.finallyProcess(self, _edObject=_edObject)
        self.result.status = XSDataStatus(message=self.getXSDataMessage(),
                                          executiveSummary=XSDataString(os.linesep.join(self.summary)))
        self.setDataOutput(self.result)

#    def doSuccessReduce(self, _edPlugin=None):
#        self.DEBUG("EDPluginControlSaxsModelingv1_0.doSuccessReduce")
#        self.retrieveSuccessMessages(_edPlugin, "EDPluginControlSaxsModelingv1_0.doSuccessReduce")
#        self.inputautorg = XSDataInputAutoRg(inputCurve=[_edPlugin.dataOutput.mergedCurve])
#        self.inputautorg.sample = self.dataInput.sample
#
#
#    def doFailureReduce(self, _edPlugin=None):
#        self.DEBUG("EDPluginControlSaxsModelingv1_0.doFailureReduce")
#        self.retrieveFailureMessages(_edPlugin, "EDPluginControlSaxsModelingv1_0.doFailureReduce")
#        self.setFailure()
#
#    def doSuccessAutoRg(self, _edPlugin=None):
#        self.DEBUG("EDPluginControlSaxsModelingv1_0.doSuccessAutoRg")
#        self.retrieveSuccessMessages(_edPlugin, "EDPluginControlSaxsModelingv1_0.doSuccessAutoRg")
#
#
#    def doFailureAutoRg(self, _edPlugin=None):
#        self.DEBUG("EDPluginControlSaxsModelingv1_0.doFailureAutoRg")
#        self.retrieveFailureMessages(_edPlugin, "EDPluginControlSaxsModelingv1_0.doFailureAutoRg")
#        self.setFailure()

    def bestDammif(self):
        """
        Find DAMMIF run with best chi-square value
        """
        fitResultDict = dict([(plg.dataOutput.chiSqrt.value, plg) for plg in self.damif_plugins])
        fitResultList = fitResultDict.keys()
        fitResultList.sort()

        return fitResultDict[fitResultList[0]]
