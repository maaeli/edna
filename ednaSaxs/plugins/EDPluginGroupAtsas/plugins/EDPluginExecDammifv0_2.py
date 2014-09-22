#! coding: utf-8
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
from XSDataCommon import XSDataString, XSDataFile, XSDataDouble, XSDataStatus
import parse_atsas

class EDPluginExecDammifv0_2(EDPluginExecProcessScript):
    """
    Execution plugin for ab-initio model determination using DAMMIF
    """
    # Should be able to go up to P19, but DAMMIF only seems to work for symmetries up to P12
    knownSymmetry = ["P%i" % i for i in range(1, 13)] + ["P%i2" % i for i in range(2, 13)]
    name = "dammif"

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
        if self.dataInput.mode:
            self.DEBUG("EDPluginExecDammifv0_2.checkDammifMode")
            try:
                if self.dataInput.mode.value.lower() in ['fast', 'slow']:
                    self.mode = self.dataInput.mode.value.lower()
            except Exception as error:
                self.ERROR("Running DAMMIF in fast mode by default (%s)" % error)


    def checkDammifUnitInput(self):
        if self.dataInput.unit:
            self.DEBUG("EDPluginExecDammifv0_2.checkDammifUnit")
            try:
                if self.dataInput.unit.value.lower() in ['angstrom', 'nanometer']:
                    self.unit = self.dataInput.unit.value.upper()
            except Exception as error:
                self.ERROR("Using A-1 units for q-axis values by default (%s)" % error)


    def checkDammifSymmetryInput(self):
        if self.dataInput.symmetry:
            self.DEBUG("EDPluginExecDammifv0_2.checkDammifSymmetryInput")
            try:
                if self.dataInput.symmetry.value in self.knownSymmetry:
                    self.symmetry = self.dataInput.symmetry.value
            except Exception as error:
                self.ERROR("Symmetry wasn't specified. Setting symmetry to P1 (%s)" % error)


    def checkDammifParticleShapeInput(self):
        if self.dataInput.expectedParticleShape:
            particleShape = ['PROLATE', 'OBLATE', 'UNKNOWN']
            if self.dataInput.expectedParticleShape:
                try:
                    if self.dataInput.expectedParticleShape.value in range(3):
                        self.particleShape = particleShape[self.dataInput.expectedParticleShape.value]
                except Exception as error:
                    self.ERROR("Using Unknown particle shape (%s)" % error)


    def checkDammifConstant(self):
        if self.dataInput.constant:
            try:
                self.constant = '--constant=' + str(self.dataInput.constant.value)
            except Exception as error:
                self.ERROR("Constant to subtract will be defined automatically (%s)" % error)


    def checkDammifChained(self):
        if  self.dataInput.chained:
            try:
                if self.dataInput.chained.value:
                    self.chained = '--chained'
            except Exception as error:
                self.ERROR("Atoms in the output model are not chained (%s)" % error)


    def preProcess(self, _edObject=None):
        EDPluginExecProcessScript.preProcess(self)
        self.DEBUG("EDPluginExecDammifv0_2.preProcess")
        if self.dataInput.order:
            self.name = "dammif-%s" % self.dataInput.order.value #I know I only modify the instance variable, not the class one

        self.generateDammifScript()
 

    def postProcess(self, _edObject=None):
        EDPluginExecProcessScript.postProcess(self)
        self.DEBUG("EDPluginExecDammifv0_2.postProcess")
        # Create some output data
        cwd = self.getWorkingDirectory()
        model = XSDataSaxsModel(name=XSDataString(self.name))

        xsDataResult = XSDataResultDammif(model=model)
        pathLogFile = os.path.join(cwd, "dammif.log")
        pathFitFile = os.path.join(cwd, "dammif.fit")
        pathFirFile = os.path.join(cwd, "dammif.fir")
        pathMoleculeFile = os.path.join(cwd, "dammif-1.pdb")
        pathSolventFile = os.path.join(cwd, "dammif-0.pdb")

        try:
            res = parse_atsas.parsePDB(pathMoleculeFile)
        except Exception as error:
            self.ERROR("EDPluginExecDammifv0_2:parsePDB: %s" % error)
        else:
            for k in res:
                self.__setattr__(k, res[k])

        if os.path.exists(pathLogFile):
            xsDataResult.logFile = model.logFile = XSDataFile(XSDataString(pathLogFile))
            if self.Rfactor:
                xsDataResult.rfactor = model.rfactor = XSDataDouble(self.Rfactor)
        if os.path.exists(pathFitFile):
            xsDataResult.fitFile = model.fitfile = XSDataFile(XSDataString(pathFitFile))
        if os.path.exists(pathFirFile):
            model.firfile = XSDataFile(XSDataString(pathFirFile))
            xsDataResult.chiSqrt = model.chiSqrt = self.returnDammifChiSqrt()
        if os.path.exists(pathMoleculeFile):
            xsDataResult.pdbMoleculeFile = model.pdbFile = XSDataFile(XSDataString(pathMoleculeFile))    
        if os.path.exists(pathSolventFile):
            xsDataResult.pdbSolventFile = XSDataFile(XSDataString(pathSolventFile))
        if os.path.exists(pathFirFile):
            model.firFile = XSDataFile(XSDataString(pathFirFile))
        
        if self.volume:
            model.volume = XSDataDouble(self.volume)
        if self.Rg:
            model.rg= XSDataDouble(self.Rg)
        if self.Dmax:
            model.dmax = XSDataDouble(self.Dmax)

        self.generateExecutiveSummary()
        xsDataResult.status = XSDataStatus(message=self.getXSDataMessage(),
                                          executiveSummary=XSDataString(os.linesep.join(self.getListExecutiveSummaryLines())))
        self.dataOutput = xsDataResult


    def generateDammifScript(self):
        self.DEBUG("EDPluginExecDammifv0_2.generateDammifScript")

        # Dammif doesn't accept file names longer than 64 characters.
        # Using symlink to work around this issue
        tmpInputFileName = self.dataInput.gnomOutputFile.path.value
        self.symlink(tmpInputFileName, "dammif.out")

        commandLine = ['--mode', self.mode, \
                       '--unit', self.unit, \
                       '--symmetry', self.symmetry, \
                       '--anisometry', self.particleShape, \
                       self.constant, self.chained, 'dammif.out']

        self.setScriptCommandline(' '.join(commandLine))


    def returnDammifChiSqrt(self):
        try:
            self.sqrtChi = parse_atsas.SqrtChi(os.path.join(self.getWorkingDirectory(), "dammif.fir"))
        except Exception as error:
            self.ERROR("EDPluginExecDammifv0_2:returnDammifChiSqrt: %s"%error)
            return
        else:
            return XSDataDouble(self.sqrtChi)


    def generateExecutiveSummary(self, __edPlugin=None):
        tmpDammif = "Results of %s: " % self.name
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
