# coding: utf8
#
#    Project: EdnaSaxs/Atsas
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) 2010: DLS
#                  2013: ESRF
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
__authors__ = [ "irakli", "Jérôme Kieffer"]
__license__ = "GPLv3+"
__copyright__ = "2010 DLS, 2013 ESRF"

import os
from math import pi, cos, sin

from EDPluginExecProcessScript import EDPluginExecProcessScript
from XSDataEdnaSaxs import XSDataInputSupcomb, XSDataResultSupcomb, XSDataSaxsModel
from XSDataCommon import XSDataString, XSDataFile, XSDataDouble, XSDataRotation, XSDataVectorDouble, XSDataMessage, XSDataStatus
from EDFactoryPlugin import edFactoryPlugin
import parse_atsas

class EDPluginExecSupcombv0_2(EDPluginExecProcessScript):
    """
    Execution plugin for ab-initio model determination using Supcomb

    To superimpose two bodies in a batch mode type 
    supcomb13 <file1.pdb> <file2.pdb> [<mode>] [<Enant>]
    [<Symmetry>] 
    In this mode, the object        <file2.pdb> 
    is superimposed onto the object <file1.pdb> 
    starting from the best principal axes alignment,
    using by default ALL coordinates (<mode>=0) or only
    backbone othervise and using NO enanthiomorphs
    by default (<Enant>=N) or allowing them if <Enant>=Y
    Symmetry Pn or Pn2 can also be taken into account 
    The transformed object <filename2.pdb>  
    is saved onto the file <filename2r.pdb>

    A modification of supcomb13 for FAST search 
    The bodies are remapped to a rough DAM grids 
    for global minimization. The final solution 
    is then obtained by local refinement using true 
    structures in the vicinity of rough solution 
    
    To superimpose two bodies in a batch mode type 
    supcomb20 <file1.pdb> <file2.pdb> [<mode>] [<Enant>]
    In this mode, the object        <file2.pdb> 
    is superimposed onto the object <file1.pdb> 
    starting from the best principal axes alignment,
    using by default ALL coordinates (<mode>=0) or only
    backbone othervise and using NO enanthiomorphs
    by default (<Enant>=N) or allowing them if <Enant>=Y
    The transformed object <file2.pdb>  
    is saved onto the file <file2r.pdb>
    
    To start the program in a dialog mode, type     
    supcomb20  (without parameters)
    In this mode, the user will be prompted to 
    specify file names, allow or disallow enanthiomorphs
    to use all atoms or backbones and to test several   
    starting approximations for the alignment 
    
    The program minimizes a so-called normalized spatial
    spatial discrepancy (NSD) to find the best alignment
    of two models. The value is saved onto an output
    file as Final distance; NSD < 1 indicates that the 
    bodies are similar. The 4X4 transformation matrix A
    describes the operation made to transform the body
    <NEW> = A3 * <OLD> + Shift, where
    A3 is a 3X3 matrix (upper left part of A)
    and Shift = (DX, DY, DZ) is the 4th column of A
    
    For details of the algorithm, see 
    M.Kozin & D.Svergun (2001) Automated matching of 
    high- and low-resolution structural models.
           J. Appl. Crystallogr. 34, 33-41.  

    """

    name = "supcomb" #name of the model generated

    def __init__(self):
        """
        """
        EDPluginExecProcessScript.__init__(self)
        self.setXSDataInputClass(XSDataInputSupcomb)

        self.__bEnantiomorphs = True
        self.__bBackbone = False

        self.__strOutputFileName = 'result.pdb'
        self.__fNSD = None
        self.__vecRot = None
        self.__vecTrns = None


    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginExecSupcombv0_2.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.templateFile, "No template file specified")
        self.checkMandatoryParameters(self.dataInput.superimposeFile, "No superimpose file specified")

        self.checkSupcombEnantiomorphsInput()
        self.checkSupcombBackboneInput()


    def checkSupcombEnantiomorphsInput(self):
        self.DEBUG("EDPluginExecSupcombv0_2.checkEnantiomorphs")
        if self.dataInput.enantiomorphs:
            try:
                if self.dataInput.enantiomorphs.value:
                    self.__bEnantiomorphs = self.dataInput.enantiomorphs.value
            except Exception as error:
                self.WARNING("Enabling enantiomorphs in Supcomb by default: %s" % error)

    def checkSupcombBackboneInput(self):
        self.DEBUG("EDPluginExecSupcombv0_2.checkBackbone")
        if self.dataInput.backbone:
            try:
                if self.dataInput.backbone.value:
                    self.__bBackbone = self.dataInput.backbone.value
            except Exception as error:
                self.WARNING("Using all atoms in Supcomb by default: %s" % error)


    def preProcess(self, _edObject=None):
        EDPluginExecProcessScript.preProcess(self)
        self.DEBUG("EDPluginExecSupcombv0_2.preProcess")
        self.generateSupcombScript()
        if self.dataInput.name:
            self.name = self.dataInput.name.value


    def process(self, _edObject=None):
        EDPluginExecProcessScript.process(self)
        self.DEBUG("EDPluginExecSupcombv0_2.process")


    def postProcess(self, _edObject=None):
        EDPluginExecProcessScript.postProcess(self)
        self.DEBUG("EDPluginExecSupcombv0_2.postProcess")
        try:
            self.dataOutput = self.parseSupcombOutputFile()
        except Exception as error:
            self.ERROR("Error in supcomb: parseSupcombOutputFile: %s" % error)
            self.setFailure()

    def generateSupcombScript(self):
        self.DEBUG("EDPluginExecSupcombv0_2.generateSupcombScript")

        self.setScriptCommandline("")

        _tmpTemplateFileName = self.dataInput.templateFile.path.value
        _tmpSuperimposeFileName = self.dataInput.superimposeFile.path.value
        if self.__bBackbone:
            _tmpBackbone = '1'
        else:
            _tmpBackbone = ''
        if not self.__bEnantiomorphs:
            _tmpEnantiomorphs = 'No'
        else:
            _tmpEnantiomorphs = ''
        self.symlink(_tmpTemplateFileName, "template.pdb")
        self.symlink(_tmpSuperimposeFileName, "supimpose.pdb")

        commandLine = ['template.pdb', _tmpBackbone, \
                       'supimpose.pdb', _tmpEnantiomorphs, \
                       self.__strOutputFileName]

        self.addListCommandExecution('\n'.join(commandLine))


    def returnRotation(self, logLines):

        _psi = pi * float(logLines[0].split()[-1]) / 180.0
        _theta = pi * float(logLines[1].split()[-1]) / 180.0
        _phi = pi * float(logLines[2].split()[-1]) / 180.0

        q = [cos(_phi / 2) * cos(_theta / 2) * cos(_psi / 2) + sin(_phi / 2) * sin(_theta / 2) * sin(_psi / 2), \
             sin(_phi / 2) * cos(_theta / 2) * cos(_psi / 2) - cos(_phi / 2) * sin(_theta / 2) * sin(_psi / 2), \
             cos(_phi / 2) * sin(_theta / 2) * cos(_psi / 2) + sin(_phi / 2) * cos(_theta / 2) * sin(_psi / 2), \
             cos(_phi / 2) * cos(_theta / 2) * sin(_psi / 2) - sin(_phi / 2) * sin(_theta / 2) * cos(_psi / 2)]

        return XSDataRotation(q[0], q[1], q[2], q[3])


    def returnTranslation(self, logLines):

        _vecTmp = []
        for line in logLines:
            _vecTmp.append(float(line.split()[-1]))

        return XSDataVectorDouble(_vecTmp[0], _vecTmp[1], _vecTmp[2])


    def parseSupcombOutputFile(self):

        logFile = self.readProcessLogFile()
        logLines = logFile.splitlines()
        xsRot = self.returnRotation(logLines[-3:])
        xsTrns = self.returnTranslation(logLines[-6:-3])
        xsNSD = XSDataDouble(float(logLines[-8].split()[-1]))
        pdb = os.path.join(self.getWorkingDirectory(), self.__strOutputFileName)
                           
        try:
            res = parse_atsas.parsePDB(pdb, pdb)
        except Exception as error:
            self.ERROR("in parsePDB: %s" % error)
        model = XSDataSaxsModel(name=XSDataString(self.name),
                                logFile=XSDataFile(XSDataString(os.path.join(self.getWorkingDirectory(), self.getScriptLogFileName()))))
                                
        if "Rfactor" in res:
            model.rfactor = XSDataDouble(res["Rfactor"])
        if "volume" in res:
            model.volume = XSDataDouble(res["volume"])
        if "Rg" in res:
            model.rg = XSDataDouble(res["Rg"])
        if "Dmax" in res :
            model.dmax = XSDataDouble(res["Dmax"])

        xsDataResult = XSDataResultSupcomb(NSD=xsNSD,
                                           rot=xsRot,
                                           trns=xsTrns,
                                           model=model)
        xsDataResult.outputFilename = model.pdbFile = XSDataFile(XSDataString(pdb))
        xsDataResult.status = XSDataStatus(message=self.getXSDataMessage(),
                                          executiveSummary=XSDataString(os.linesep.join(self.getListExecutiveSummaryLines())))
        return xsDataResult

    def symlink(self, filen, link):
        """
        Create a symlink to CWD with relative path
        """
        src = os.path.abspath(filen)
        cwd = self.getWorkingDirectory()
        dest = os.path.join(cwd, link)
        os.symlink(os.path.relpath(src, cwd), dest)
