# coding: utf-8
#
#    Project: EdnaSaxs/Atsas
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) 2011, ESRF Grenoble
#
#    Principal author:       Jérôme Kieffer
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

__author__ = "Jérôme Kieffer"
__license__ = "GPLv3+"
__copyright__ = "2011-2014, ESRF Grenoble"

import numpy

from EDPluginExec import EDPluginExec

from XSDataEdnaSaxs import XSDataInputDatop, XSDataResultDatop


class EDPluginExecDatopv2_0(EDPluginExec):
    """
    Plugin that simply performs an operation on a (couple of) curves. 
    operations can be  ADD, SUB, MUL, DIV
    
    Atsas free version 
    """
    epsilon = 1e-6

    def __init__(self):
        """
        """
        EDPluginExec.__init__(self)
        self.setXSDataInputClass(XSDataInputDatop)
        self.strOperation = None
        self.lstInFiles = []
        self.outputFile = None
        self.const = None

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginExecDatopv2_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.inputCurve, "No input Curve file provided")
        self.checkMandatoryParameters(self.dataInput.outputCurve, "No output Curve file is provided")
        self.checkMandatoryParameters(self.dataInput.operation, "No arithmetic operation provided ")

    def preProcess(self, _edObject=None):
        EDPluginExec.preProcess(self)
        self.DEBUG("EDPluginExecDatopv2_0.preProcess")
        self.outputFile = self.dataInput.outputCurve.path.value
        self.strOperation = self.dataInput.operation.value.replace("+", "ADD").replace("-", "SUB").replace("*", "MUL").replace("/", "DIV")
        self.lstInFiles = [ i.path.value for i in  self.dataInput.inputCurve]
        if self.dataInput.constant is not None:
            self.const = self.dataInput.constant.value
        
    def process(self):
        EDPluginExec.process(self)
        l = len(self.lstInFiles)
        if l > 0 :
            q0, I0, s0 = numpy.loadtxt(self.lstInFiles[0], unpack=True)
        if l > 1 :
            q1, I1, s1 = numpy.loadtxt(self.lstInFiles[-1], unpack=True)
        if self.strOperation in ("ADD", "SUB") and l==2:
            q = q1
            assert abs(q1 -  q0).max()<self.epsilon
            if self.strOperation == "SUB":
                I = I0 - I1
            else:
                I = I0 + I1
            s = numpy.sqrt(s0*s0 + s1*s1)
        if self.strOperation in ("MUL", "DIV") and l>=1 and self.dataInput.constant:
            q=q0
            if self.strOperation == "MUL":
                I = I0*self.const
                s = s0*self.const
            else:
                I = I0/self.const
                s = s0/self.const
            
        m=numpy.vstack((q,I,s))
        numpy.savetxt(self.outputFile, m.T)


    def postProcess(self, _edObject=None):
        EDPluginExec.postProcess(self)
        self.DEBUG("EDPluginExecDatopv2_0.postProcess")
        # Create some output data
        xsDataResult = XSDataResultDatop(outputCurve=self.dataInput.outputCurve)
        self.setDataOutput(xsDataResult)

