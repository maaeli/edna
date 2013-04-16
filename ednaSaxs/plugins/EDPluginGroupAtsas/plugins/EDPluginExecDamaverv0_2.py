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
from EDPluginExecProcessScript import EDPluginExecProcessScript
from XSDataEdnaSaxs import XSDataInputDamaver, XSDataResultDamaver, XSDataSaxsModel
from XSDataCommon import XSDataString, XSDataFile, XSDataDouble, XSDataMessage, XSDataStatus

class EDPluginExecDamaverv0_2(EDPluginExecProcessScript):
    """
    Execution plugin running DAMAVER pipeline for alignment of input pdb models,
    selecting the most typical one and building an averaged model  
    """
    knownSymmetry = ["P%i" % i for i in range(1, 20)] + ["P%i2" % i for i in range(2, 13)]
#    name = "damaver"

    def __init__(self):
        """
        """
        EDPluginExecProcessScript.__init__(self)
        self.setXSDataInputClass(XSDataInputDamaver)

        self.__xsDataResult = XSDataResultDamaver()

        self.__strSymmetry = ''
        self.__bAutomatic = True

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginExecDamaverv0_2.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.pdbInputFiles, "PDB input files are missing")


    def preProcess(self, _edObject=None):
        EDPluginExecProcessScript.preProcess(self)
        self.DEBUG("EDPluginExecDamaverv0_2.preProcess")

        self.checkDamaverPath()
        self.checkDamaverAutomaticInput()
        self.checkDamaverSymmetryInput()
        self.generateDamaverScript()

    def checkDamaverPath(self):
        if '.' in self.getScriptExecutable():
            self.WARNING('Damaver might not run properly when \'.\' is present in the path to launch it')

    def checkDamaverAutomaticInput(self):
        if self.dataInput.automatic:
            try:
                if self.dataInput.automatic:
                    self.__bAutomatic = self.dataInput.automatic.value
            except Exception as error:
                self.WARNING("Running Damaver automation pipeline by default: %s"%error)


    def checkDamaverSymmetryInput(self):
        self.DEBUG("EDPluginExecDammifv0_2.checkDammifSymmetryInput")
        if self.dataInput.symmetry:
            try:
                if self.dataInput.symmetry.value in self.knownSymmetry:
                    self.__strSymmetry = self.dataInput.symmetry.value
            except Exception as error:
                self.WARNING("Symmetry wasn't specified. Setting symmetry to P1: %s" % error)


    def postProcess(self, _edObject=None):
        EDPluginExecProcessScript.postProcess(self)
        self.DEBUG("EDPluginExecDamaverv0_2.postProcess")
        # Create some output data

        self.outputDamaverPdbFiles()
        if self.__bAutomatic:
            self.parseDamselLog()
        self.generateExecutiveSummary()
        self.__xsDataResult.status = XSDataStatus(message=self.getXSDataMessage(),
                                                  executiveSummary=XSDataString(os.linesep.join(self.getListExecutiveSummaryLines())))
        self.dataOutput = self.__xsDataResult


    def outputDamaverPdbFiles(self):
        cwd = self.getWorkingDirectory()
        damaverPDB = os.path.join(cwd, "damaver.pdb")
        if os.path.exists(damaverPDB):
            self.__xsDataResult.model = XSDataSaxsModel(name=XSDataString("damaver"))
            self.__xsDataResult.damaverPdbFile = self.__xsDataResult.model.pdbFile = XSDataFile(XSDataString(damaverPDB))

        if self.__bAutomatic:
            damfilterFile = os.path.join(cwd, "damfilt.pdb")
            if os.path.exists(damfilterFile):
                self.__xsDataResult.damfilterPdbFile = XSDataFile(XSDataString(damfilterFile))

            damstartFile = os.path.join(cwd, "damstart.pdb")
            if os.path.exists(damstartFile):
                self.__xsDataResult.damstartPdbFile = XSDataFile(XSDataString(damstartFile))

    def parseDamselLog(self):
        damselLog = open(os.path.join(self.getWorkingDirectory(), "damsel.log"))

        for line in damselLog:
            wordsLine = [tmpStr for tmpStr in line.split(' ') if tmpStr is not '']
            if wordsLine[:4] == ['Mean', 'value', 'of', 'NSD']:
                self.__xsDataResult.setMeanNSD(XSDataDouble(float(wordsLine[-1])))
            if wordsLine[:3] == ['Variation', 'of', 'NSD']:
                self.__xsDataResult.setVariationNSD(XSDataDouble(float(wordsLine[-1])))



    def generateDamaverScript(self):
        self.DEBUG("EDPluginExecDammifv0_2.generateDammifScript")

        dataFileNames = []
        for idx, pdbInputFile in enumerate(self.dataInput.pdbInputFiles):
            tmpInputFileName = pdbInputFile.path.value
            self.symlink(tmpInputFileName, 'dammif-' + str(idx + 1) + '.pdb')
            dataFileNames.append('dammif-' + str(idx + 1) + '.pdb')

        if self.__bAutomatic:
            commandScriptLine = ['/a', self.__strSymmetry]
        else:
            damsupLog = open(os.path.join(self.getWorkingDirectory(), "damsup.log"), 'w')
            damsupLog.write('\n'.join(dataFileNames))
            damsupLog.close()
            commandScriptLine = ['damsup.log']
        self.setScriptCommandline(' '.join(commandScriptLine))

    def generateExecutiveSummary(self, __edPlugin=None):
        self.addExecutiveSummaryLine("DAMAVER output pdb model : %s" % os.path.join(self.getWorkingDirectory(), "damaver.pdb"))
        if self.__bAutomatic:
            self.addExecutiveSummaryLine("DAMFILT output pdb model : %s" % os.path.join(self.getWorkingDirectory(), "damfilt.pdb"))
            self.addExecutiveSummaryLine("DAMSTART output pdb model : %s" % os.path.join(self.getWorkingDirectory(), "damstart.pdb"))
            damselLog = open(os.path.join(self.getWorkingDirectory(), "damsel.log"))
            for line in damselLog:
                self.addExecutiveSummaryLine(line)

    def symlink(self, filen, link):
        """
        Create a symlink to CWD with relative path
        """
        src = os.path.abspath(filen)
        cwd = self.getWorkingDirectory()
        dest = os.path.join(cwd, link)
        os.symlink(os.path.relpath(src, cwd), dest)
