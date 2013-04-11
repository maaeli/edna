#! coding: utf8
#
#    Project: EdnaSaxs/Atsas
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) DLS
#
#    Principal author:       irakli
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

__authors__ = ["irakli", "Jérôme Kieffer"]
__license__ = "GPLv3+"
__copyright__ = "2010 DLS, 2013 ESRF"

import os
from EDPluginExecProcessScript import EDPluginExecProcessScript
from XSDataEdnaSaxs import XSDataInputDammif, XSDataResultDammif, XSDataSaxsModel
from XSDataCommon import XSDataString, XSDataFile, XSDataDouble


class EDPluginExecDammifv0_2(EDPluginExecProcessScript):
    """
    Execution plugin for ab-initio model determination using DAMMIF
    """
    # Should be able to go up to P19, but DAMMIF only seems to work for symmetries up to P12
    knownSymmetry = ["P%i" % i for i in range(1, 13)] + ["P%i2" % i for i in range(2, 13)]

    def __init__(self):
        """
        """
        EDPluginExecProcessScript.__init__(self)
        self.setXSDataInputClass(XSDataInputDammif)

        self.mode = 'fast'
        self.unit = 'ANGSTROM'
        self.symmetry = 'P1'
        self.particleShape = 'UNKNOWN'
        self.constant = ''
        self.chained = ''
        self.Rfactor = None
        self.sqrtChi = None
        self.volume = None
        self.Rg = None
        self.Dmax = None
        self.name = "dammif"

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginExecDammifv0_2.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.gnomOutputFile, "No GNOM output file specified")

        self.checkDammifModeInput()
        self.checkDammifUnitInput()
        self.checkDammifSymmetryInput()
        self.checkDammifParticleShapeInput()
        self.checkDammifConstant()
        self.checkDammifChained()

    def checkDammifModeInput(self):
        self.DEBUG("EDPluginExecDammifv0_2.checkDammifMode")
        try:
            if self.dataInput.mode.value.lower() in ['fast', 'slow']:
                self.mode = self.dataInput.mode.value.lower()
        except Exception:
            self.WARNING("Running DAMMIF in fast mode by default")

    def checkDammifUnitInput(self):
        self.DEBUG("EDPluginExecDammifv0_2.checkDammifUnit")
        try:
            if self.dataInput.unit.value.lower() in ['angstrom', 'nanometer']:
                self.unit = self.dataInput.unit.value.upper()
        except Exception:
            self.WARNING("Using A-1 units for q-axis values by default")

    def checkDammifSymmetryInput(self):
        self.DEBUG("EDPluginExecDammifv0_2.checkDammifSymmetryInput")
        try:
            if self.dataInput.getSymmetry().value in _knownSymmetry:
                self.symmetry = self.dataInput.getSymmetry().value
        except Exception:
            self.WARNING("Symmetry wasn't specified. Setting symmetry to P1")

    def checkDammifParticleShapeInput(self):
        particleShape = ['PROLATE', 'OBLATE', 'UNKNOWN']
        try:
            if self.dataInput.getExpectedParticleShape().value in range(3):
                self.particleShape = particleShape[self.dataInput.getExpectedParticleShape().value]
        except Exception:
            self.WARNING("Using Unknown particle shape")

    def checkDammifConstant(self):
        try:
            self.constant = '--constant=' + str(self.dataInput.getConstant().value)
        except Exception:
            self.DEBUG("Constant to subtract will be defined automatically")

    def checkDammifChained(self):
        try:
            if self.dataInput.chained.value:
                self.chained = '--chained'
        except Exception:
            self.DEBUG("Atoms in the output model are not chained")

    def preProcess(self, _edObject=None):
        EDPluginExecProcessScript.preProcess(self)
        self.DEBUG("EDPluginExecDammifv0_2.preProcess")
        if self.dataInput.order:
            self.name = "dammif-%s" % self.dataInput.order.value

        self.generateDammifScript()
 

    def postProcess(self, _edObject=None):
        EDPluginExecProcessScript.postProcess(self)
        self.DEBUG("EDPluginExecDammifv0_2.postProcess")
        # Create some output data
        cwd = self.getWorkingDirectory()
        model = XSDataSaxsModel(name=XSDataString(name))

        xsDataResult = XSDataResultDammif(model=model)
        pathLogFile = os.path.join(cwd, "dammif.log")
        pathFitFile = os.path.join(cwd, "dammif.fit")
        pathFirFile = os.path.join(cwd, "dammif.fir")
        pathMoleculeFile = os.path.join(cwd, "dammif-1.pdb")
        pathSolventFile = os.path.join(cwd, "dammif-0.pdb")

        xsFitFile = XSDataFile(XSDataString(pathFitFile))

        xsSolventFile = XSDataFile(XSDataString(pathSolventFile))

        if os.path.exists(pathLogFile):
            xsDataResult.logFile = model.logFile = XSDataFile(XSDataString(pathLogFile))
            xsDataResult.rfactor = model.rfactor = returnDammifRFactor()
        if os.path.exists(pathFitFile):
            xsDataResult.fitFile = model.fitfile = XSDataFile(XSDataString(pathFitFile))
        if os.path.exists(pathFirFile):
            model.firfile = XSDataFile(XSDataString(pathFirFile))
            xsDataResult.chiSqrt = model.chiSqrt = returnDammifChiSqrt()
        if os.path.exists(pathMoleculeFile.value):
            xsDataResult.pdbMoleculeFile = model.pdbFile = XSDataFile(XSDataString(pathMoleculeFile))
        if os.path.exists(pathSolventFile.value):
            xsDataResult.setPdbSolventFile(xsSolventFile)

        self.generateExecutiveSummary()
        xsDataResult.status = XSDataStatus(message=self.getXSDataMessage(),
                                          executiveSummary=XSDataString(os.linesep.join(self.getListExecutiveSummaryLines())))
        self.dataOutput = xsDataResult

    def generateDammifScript(self):
        self.DEBUG("EDPluginExecDammifv0_2.generateDammifScript")

        # Dammif doesn't accept file names longer than 64 characters.
        # Using symlink to work around this issue
        tmpInputFileName = self.dataInput.gnomOutputFile.path.value
        os.symlink(tmpInputFileName, os.path.join(self.getWorkingDirectory(), "dammif.out"))

        commandLine = ['--mode', self.mode, \
                       '--unit', self.unit, \
                       '--symmetry', self.symmetry, \
                       '--anisometry', self.particleShape, \
                       self.constant, self.chained, 'dammif.out']

        self.setScriptCommandline(' '.join(commandLine))


    def returnDammifChiSqrt(self):
        logFile = open(os.path.join(self.getWorkingDirectory(), "dammif.fir"))
        self.sqrtChi = float(logFile.readline().split('=')[-1])
        return XSDataDouble(self.sqrtChi)

    def returnDammifRFactor(self):
        logFile = open(os.path.join(self.getWorkingDirectory(), "dammif.log"))
        tmpRfactor = None
        for line in logFile:
            wordsLine = [tmpStr for tmpStr in line.split(' ') if tmpStr is not '']
            if wordsLine[0] == "Rf:":
                tmpRfactor = float(wordsLine[1][:-1])
        self.Rfactor = tmpRfactor
        return XSDataDouble(tmpRfactor)

    def generateExecutiveSummary(self, __edPlugin=None):
        tmpDammif = "Results of %s: " % self.name
        tmpRFactor = "RFactor = %s" % self.Rfactor
        tmpChiSqrt = "Sqrt(Chi) = %s" % self.sqrtChi
        tmpVolume = "Volume = %s" % self.volume
        tmpDmax = "Volume = %s" % self.Dmax
        tmpRg = "Rg = %s" % self.Dmax
        tmpStrLine = "\t".join([tmpDammif, tmpChiSqrt, tmpRFactor, tmpVolume, tmpDmax, tmpRg])
        self.addExecutiveSummaryLine(tmpStrLine)
