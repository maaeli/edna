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
from XSDataEdnaSaxs import XSDataInputDammin, XSDataResultDammin, XSDataSaxsModel
from XSDataCommon import XSDataString, XSDataFile, XSDataDouble, XSDataMessage, XSDataStatus
import parse_atsas

class EDPluginExecDamminv0_2(EDPluginExecProcessScript):
    """
    Execution plugin for ab-initio model determination using DAMMIN
    
    TODO: Some combinations of symmetry and dummy atom models
          are incompatible and DAMMIN will reset the dummy atom model.
          This should be accounted for to provide proper command input sequence
    """
    knownSymmetry = ["P%i" % i for i in range(1, 20)] + ["P%i2" % i for i in range(2, 13)] + ['P23', 'P432', 'PICO']
    DAMModel = ['S', 'E', 'C', 'P']
    particleShape = ['P', 'O', 'U']

    def __init__(self):
        """
        """
        EDPluginExecProcessScript.__init__(self)
        self.setXSDataInputClass(XSDataInputDammin)

        self.__strMode = 'F'
        self.__strProjectDesc = ''
        self.__strAngleUnit = ''
        self.__strCurveFit = ''
        self.__strDAM = ''
        self.__strSymmetry = 'P1'
        self.__strParticleShape = ''
        self.Rfactor = None
        self.sqrtChi = None
        self.volume = None
        self.Rg = None
        self.Dmax = None

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginExecDamminv0_2.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.gnomOutputFile, "No GNOM output file specified")

        self.checkDamminMode()
        self.checkDamminDAMInput()
        self.checkDamminSymmetryInput()        # TODO: Only using P1 because of input discrepancy for higher symmetries
        self.checkParticleShapeInput()


    def checkDamminMode(self):
        if self.dataInput.mode:
            try:
                if self.dataInput.mode.value.upper() in ['FAST', 'SLOW']:
                    self.__strMode = self.dataInput.mode.value.upper()[0]
            except Exception as error:
                self.WARNING("Running DAMMIN in FAST mode by default: %s" % error)

    def checkDamminSymmetryInput(self):

        if self.dataInput.symmetry:
            try:
                if self.dataInput.symmetry.value in self.knownSymmetry:
                    self.__strSymmetry = self.dataInput.symmetry.value
            except Exception as error:
                self.WARNING("Symmetry wasn't specified. Setting symmetry to P1: %s" % error)

    def checkDamminDAMInput(self):


        if self.dataInput.initialDummyAtomModel:
            try:
                if self.dataInput.initialDummyAtomModel.value in range(4):
                    self.__strDAM = self.DAMModel[self.dataInput.initialDummyAtomModel.value]
                    return
            except Exception as error:
                self.ERROR("No standard dummy atom model selected. Looking for a PDB mode file: %s" % error)
        elif self.dataInput.pdbInputFile:
            try:
                tmpInputFileName = self.dataInput.pdbInputFile.path.value
                self.symlink(tmpInputFileName, "input.pdb")
                self.__strDAM = 'input.pdb'
            except Exception as error:
                self.ERROR("Dummy atom model PDB file not specified. Using default model: %s" % error)


    def checkParticleShapeInput(self):

        if self.dataInput.expectedParticleShape:
            try:
                if self.dataInput.expectedParticleShape.value in range(3):
                    self.__strParticleShape = self.particleShape[self.dataInput.expectedParticleShape.value]
            except Exception as error:
                self.ERROR("Using Unknown particle shape: %s" % error)


    def preProcess(self, _edObject=None):
        EDPluginExecProcessScript.preProcess(self)
        self.DEBUG("EDPluginExecDamminv0_2.preProcess")
        if self.dataInput.name:
            self.__strProjectDesc = self.dataInput.name.value
        if self.dataInput.unit:
            unit = self.dataInput.unit.value.lower()
            if unit in ["a", "ang", "angstrom", "1", "1/a", "a^-1"]:
                self.__strAngleUnit = "1"
            if unit in ["nm", "nanom", "nanometer", "2", "1/nm", "nm^-1"]:
                self.__strAngleUnit = "2"
        self.generateDamminScript()


    def postProcess(self, _edObject=None):
        EDPluginExecProcessScript.postProcess(self)
        self.DEBUG("EDPluginExecDamminv0_2.postProcess")
        # Create some output data
        cwd = self.getWorkingDirectory()
        model = XSDataSaxsModel(name=XSDataString("dammin"))

        xsDataResult = XSDataResultDammin(model=model)
        pathLogFile = os.path.join(cwd, "dammin.log")
        pathFitFile = os.path.join(cwd, "dammin.fit")
        pathFirFile = os.path.join(cwd, "dammin.fir")
        pathMoleculeFile = os.path.join(cwd, "dammin-1.pdb")
        pathSolventFile = os.path.join(cwd, "dammin-0.pdb")

        try:
            res = parse_atsas.parsePDB(pathMoleculeFile, pathMoleculeFile)
        except Exception as error:
            self.ERROR("EDPluginExecDamminv0_2:parsePDB: %s" % error)
        else:
            for k in res:
                self.__setattr__(k, res[k])

        if os.path.exists(pathLogFile):
            xsDataResult.logFile = model.logFile = XSDataFile(XSDataString(pathLogFile))
            if not  self.Rfactor:
                self.Rfactor = self.returnDamminRFactor()
            if self.Rfactor:
                xsDataResult.rfactor = model.rfactor = XSDataDouble(self.Rfactor)
        if os.path.exists(pathFitFile):
            xsDataResult.fitFile = model.fitfile = XSDataFile(XSDataString(pathFitFile))
        if os.path.exists(pathFirFile):
            model.firfile = XSDataFile(XSDataString(pathFirFile))
            xsDataResult.chiSqrt = model.chiSqrt = self.returnDamminChiSqrt()
        if os.path.exists(pathMoleculeFile):
            xsDataResult.pdbMoleculeFile = model.pdbFile = XSDataFile(XSDataString(pathMoleculeFile))
        if os.path.exists(pathSolventFile):
            xsDataResult.pdbSolventFile = XSDataFile(XSDataString(pathSolventFile))
        if os.path.exists(pathFirFile):
            model.firFile = XSDataFile(XSDataString(pathFirFile))

        if self.volume:
            model.volume = XSDataDouble(self.volume)
        if self.Rg:
            model.rg = XSDataDouble(self.Rg)
        if self.Dmax:
            model.dmax = XSDataDouble(self.Dmax)

        self.generateExecutiveSummary()
        xsDataResult.status = XSDataStatus(message=self.getXSDataMessage(),
                                          executiveSummary=XSDataString(os.linesep.join(self.getListExecutiveSummaryLines())))
        self.dataOutput = xsDataResult


    def generateDamminScript(self):
        self.DEBUG("EDPluginExecDamminv0_2.generateDamminScript_v2")

        # Dammin doesn't accept file names longer than 64 characters.
        # Using symlink to work around this issue
        tmpInputFileName = self.dataInput.gnomOutputFile.path.value
        self.symlink(tmpInputFileName, "dammin.out")

        self.setScriptCommandline("")

        commandString = [self.__strMode, 'dammin.log', 'dammin.out', \
                         self.__strProjectDesc,
                         self.__strAngleUnit,
                         self.__strCurveFit, \
                         self.__strDAM, \
                         self.__strSymmetry]

        if self.__strDAM not in ['', 'S']:
            commandString += self.returnModelDimensions()

        commandString += self.__strParticleShape
        commandString.extend(5 * [''])                  # Just in case there are more default settings
#        print commandString
        self.addListCommandExecution('\n'.join(commandString))


    def returnModelDimensions(self):
        # TODO: For some symmetry groups DAMMIN asks for less dimensions
        if self.dataInput.initialDummyAtomModel:
            if self.dataInput.initialDummyAtomModel.value in range(1, 4):
                return 3 * ['']
            if self.dataInput.initialDummyAtomModel.value is 4:
                return ['']
        else:
            return ['']


    def returnDamminChiSqrt(self):
        logFile = open(os.path.join(self.getWorkingDirectory(), "dammin.fir"))
        self.sqrtChi = float(logFile.readline().split(' ')[-1])
        return XSDataDouble(self.sqrtChi)

    def returnDamminRFactor(self):
        logFile = open(os.path.join(self.getWorkingDirectory(), "dammin.log"))

        tmpRfactor = None

        for line in logFile:
            wordsLine = [tmpStr for tmpStr in line.split(' ') if tmpStr is not '']
            if wordsLine[0] == "Rf:":
                tmpRfactor = float(wordsLine[1])

        return tmpRfactor

    def generateExecutiveSummary(self, __edPlugin=None):
        tmpDammif = "Results of dammin: "
        tmpRFactor = "RFactor = %s" % self.Rfactor
        tmpChiSqrt = "Sqrt(Chi) = %s" % self.sqrtChi
        tmpVolume = "Volume = %s" % self.volume
        tmpDmax = "Dmax = %s" % self.Dmax
        tmpRg = "Rg = %s" % self.Rg
        tmpStrLine = "\t".join([tmpDammif, tmpChiSqrt, tmpRFactor, tmpVolume, tmpDmax, tmpRg])
        self.addExecutiveSummaryLine(tmpStrLine)


    def symlink(self, filen, link):
        """
        Create a symlink to CWD with relative path
        """
        src = os.path.abspath(filen)
        cwd = self.getWorkingDirectory()
        dest = os.path.join(cwd, link)
        os.symlink(os.path.relpath(src, cwd), dest)
