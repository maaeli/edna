#coding: utf8
#
#    Project: EdnaSaxs/Atsas
#             http://www.edna-site.org
#
#    Copyright (C) 2010, DLS
#                  2013, ESRF
#
#    Principal author:       irakli
#                            Jérôme Kieffer
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
__authors__ = ["irakli", "Jérôme Kieffer"]
__license__ = "GPLv3+"
__copyright__ = "2010 DLS; 2013 ESRF"

import os

from EDVerbose import EDVerbose
from EDPluginExecProcessScript import EDPluginExecProcessScript

from XSDataEdnaSaxs import XSDataInputDamfilt
from XSDataEdnaSaxs import XSDataResultDamfilt

from XSDataCommon import XSDataFile, XSDataString


class EDPluginExecDamfiltv0_2(EDPluginExecProcessScript):
    """
    Execution plugin for ab-initio model determination using Damfilt
    """


    def __init__(self):
        """
        """
        EDPluginExecProcessScript.__init__(self)
        self.setXSDataInputClass(XSDataInputDamfilt)

        self.__strInputPdbFileName = 'input.pdb'
        self.__strOutputPdbFileName = 'damfilt.pdb'

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginExecDamfiltv0_2.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.getInputPdbFile(), "No template file specified")


    def preProcess(self, _edObject=None):
        EDPluginExecProcessScript.preProcess(self)
        self.DEBUG("EDPluginExecDamfiltv0_2.preProcess")
        self.generateDamfiltScript()


    def process(self, _edObject=None):
        EDPluginExecProcessScript.process(self)
        self.DEBUG("EDPluginExecDamfiltv0_2.process")


    def postProcess(self, _edObject=None):
        EDPluginExecProcessScript.postProcess(self)
        self.DEBUG("EDPluginExecDamfiltv0_2.postProcess")

        xsDataResult = XSDataResultDamfilt()

        pathOutputFile = XSDataString(os.path.join(self.getWorkingDirectory(), self.__strOutputPdbFileName))
        xsDataResult.setOutputPdbFile(XSDataFile(pathOutputFile))
        xsDataResult.status = XSDataStatus(message=self.getXSDataMessage(),
                                          executiveSummary=XSDataString(os.linesep.join(self.getListExecutiveSummaryLines())))
        self.setDataOutput(xsDataResult)

    def generateDamfiltScript(self):
        self.DEBUG("EDPluginExecDamfiltv0_2.generateDamfiltScript")

        _tmpInputFileName = self.dataInput.getInputPdbFile().path.value
        os.symlink(_tmpInputFileName, os.path.join(self.getWorkingDirectory(), self.__strInputPdbFileName))

        self.setScriptCommandline("")
        commandString = 'input.pdb' + '\n' * 5
        self.addListCommandExecution(commandString)
        #self.setScriptCommandline(self.__strInputPdbFileName)

    def generateExecutiveSummary(self, __edPlugin=None):
            self.addExecutiveSummaryLine(self.readProcessLogFile())
