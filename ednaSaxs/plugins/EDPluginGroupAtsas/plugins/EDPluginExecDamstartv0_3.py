#coding: utf-8
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
from XSDataEdnaSaxs import XSDataInputDamstart, XSDataSaxsModel, XSDataResultDamstart, XSDataSaxsModel
from XSDataCommon import XSDataFile, XSDataString, XSDataStatus, XSDataMessage


class EDPluginExecDamstartv0_3(EDPluginExecProcessScript):
    """
    Execution plugin for ab-initio model determination using Damstart
    """


    def __init__(self):
        """
        """
        EDPluginExecProcessScript.__init__(self)
        self.setXSDataInputClass(XSDataInputDamstart)

        self.__strInputPdbFileName = 'input.pdb'
        self.__strOutputPdbFileName = 'damstart.pdb'

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginExecDamstartv0_3.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.getInputPdbFile(), "No template file specified")


    def preProcess(self, _edObject=None):
        EDPluginExecProcessScript.preProcess(self)
        self.DEBUG("EDPluginExecDamstartv0_3.preProcess")
        self.generateDamstartScript()


    def process(self, _edObject=None):
        EDPluginExecProcessScript.process(self)
        self.DEBUG("EDPluginExecDamstartv0_3.process")


    def postProcess(self, _edObject=None):
        EDPluginExecProcessScript.postProcess(self)
        self.DEBUG("EDPluginExecDamstartv0_3.postProcess")
        model = XSDataSaxsModel(name=XSDataString("damstart"))
        xsDataResult = XSDataResultDamstart(model=model)

        xsDataResult.outputPdbFile = model.pdbFile = XSDataFile(XSDataString(os.path.join(self.getWorkingDirectory(), self.__strOutputPdbFileName)))
        xsDataResult.status = XSDataStatus(message=self.getXSDataMessage(),
                                          executiveSummary=XSDataString(os.linesep.join(self.getListExecutiveSummaryLines())))
        self.setDataOutput(xsDataResult)

    def generateDamstartScript(self):
        self.DEBUG("EDPluginExecDamstartv0_3.generateDamstartScript")

        _tmpInputFileName = self.dataInput.getInputPdbFile().path.value
        self.symlink(_tmpInputFileName, self.__strInputPdbFileName)

        self.setScriptCommandline("--output=%s %s"%(self.__strOutputPdbFileName, self.__strInputPdbFileName))
#         commandString = 'input.pdb' + '\n' * 5
#         self.addListCommandExecution(commandString)
        #self.setScriptCommandline(self.__strInputPdbFileName)

#    def generateExecutiveSummary(self, __edPlugin=None):
#            self.addExecutiveSummaryLine(self.readProcessLogFile())
    def symlink(self, filen, link):
        """
        Create a symlink to CWD with relative path
        """
        src = os.path.abspath(filen)
        cwd = self.getWorkingDirectory()
        dest = os.path.join(cwd, link)
        os.symlink(os.path.relpath(src, cwd), dest)
