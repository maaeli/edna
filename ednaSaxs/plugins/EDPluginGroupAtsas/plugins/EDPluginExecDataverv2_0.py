# coding: utf-8
#
#    Project: EdnaSaxs/Atsas
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) 2011 ESRF, Grenoble
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
__contact__ = "Jérôme.Kieffer@esrf.fr"
__license__ = "GPLv3+"
__copyright__ = "2014 ESRF, Grenoble"
__date__ = "17/11/2014"
__status__ = "Production"

import os
import shutil
import numpy
from EDPluginExec import EDPluginExec
from EDFactoryPluginStatic import EDFactoryPluginStatic
EDFactoryPluginStatic.loadModule("XSDataEdnaSaxs")
from XSDataEdnaSaxs import XSDataInputDataver, XSDataResultDataver
from XSDataCommon import XSDataString, XSDataFile


class EDPluginExecDataverv2_0(EDPluginExec):
    """
    Execution plugin that does the (basic) data averaging
    
    new versiion: atsas free
    """
    epsilon = 1e-6

    def __init__(self):
        """
        """
        EDPluginExec.__init__(self)
        self.setXSDataInputClass(XSDataInputDataver)
        self.strOutFile = None
        self.lstInFiles = []

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginExecDataverv2_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.inputCurve, "No input curve filenames provided")

    def preProcess(self, _edObject=None):
        EDPluginExec.preProcess(self)
        self.DEBUG("EDPluginExecDataverv2_0.preProcess")
        self.lstInFiles = [i.path.value for i in  self.dataInput.inputCurve]
        if self.dataInput.outputCurve is not None:
            self.strOutFile = self.dataInput.outputCurve.path.value
        else:
            self.strOutFile = os.path.join(self.getWorkingDirectory(), "dataver_out.dat")

    def process(self, _edObject=None):
        """
        Numpy implementation of dataver
        """
        EDPluginExec.process(self)
        l = len(self.lstInFiles)
        if l == 1:
            shutil.copyfile(self.lstInFiles[0], self.strOutFile)
            return
        q = I = s2 = None
        for fn in self.lstInFiles:
            if q is None:
                q, I, s = numpy.loadtxt(fn, unpack=True)
                s2 = s * s
            else:
                q1, I1, s1 = numpy.loadtxt(fn, unpack=True)
                assert abs(q1 - q).max() < self.epsilon
                I += I1
                s2 += s1 * s1
        m = numpy.vstack((q, I / l, numpy.sqrt(s2) / l))

        with open(self.strOutFile, "w") as outfile:
            numpy.savetxt(outfile, m.T)
        #numpy.savetxt(self.strOutFile, m.T)

    def postProcess(self, _edObject=None):
        EDPluginExec.postProcess(self)
        self.DEBUG("EDPluginExecDataverv2_0.postProcess")
        # Create some output data
        xsDataResult = XSDataResultDataver()
        xsDataResult.outputCurve = XSDataFile(XSDataString(self.strOutFile))
        self.setDataOutput(xsDataResult)

