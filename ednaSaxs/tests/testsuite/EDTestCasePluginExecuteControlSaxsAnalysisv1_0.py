# coding: utf-8
#
#    Project: EdnaSaxs
#             http://www.edna-site.org
#
#    Copyright (C) 2012 ESRF
#
#    Principal author:  Jérôme Kieffer
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
__copyright__ = "ESRF"
__date__ = "27/08/2015"
__status__ = "production"
import os

from EDVerbose                           import EDVerbose
from EDAssert                            import EDAssert
from EDTestCasePluginExecute             import EDTestCasePluginExecute
from XSDataEdnaSaxs import XSDataInputSaxsAnalysis as XSDataInput
from XSDataEdnaSaxs import XSDataResultSaxsAnalysis as XSDataResult
from parse_atsas import get_ATSAS_version

class EDTestCasePluginExecuteControlSaxsAnalysisv1_0(EDTestCasePluginExecute):


    def __init__(self, _strTestName=None):
        EDTestCasePluginExecute.__init__(self, "EDPluginControlSaxsAnalysisv1_0")
#        self.setConfigurationFile(os.path.join(self.getPluginTestsDataHome(),
#                                               "XSConfiguration_SaxsAnalysis.xml"))
        self.setDataInputFile(os.path.join(self.getPluginTestsDataHome(), \
                                           "XSDataInputSaxsAnalysisv1_0_reference.xml"))

    def preProcess(self):
        """
        Download reference 1D curves
        """
        EDTestCasePluginExecute.preProcess(self)
        self.loadTestImage(["autosubtracted.dat"])
        version = self.plugin.config.get("atsasVersion", "2.4.0")
        if version < "2.5":
            res = "XSDataResultSaxsAnalysisv1_0_reference.xml-2.4.0"
        elif version < "2.6":
            res = "XSDataResultSaxsAnalysisv1_0_reference.xml-2.5.2"
        else:
            res = "XSDataResultSaxsAnalysisv1_0_reference.xml-2.6.1"
        self.setReferenceDataOutputFile(os.path.join(self.getPluginTestsDataHome(), res))


    def testExecute(self):
        """
        """
        self.run()
        plugin = self.getPlugin()

################################################################################
# Compare XSDataResults
################################################################################

        strExpectedOutput = self.readAndParseFile(self.getReferenceDataOutputFile())
        EDVerbose.DEBUG("Checking obtained result...")
        xsDataResultReference = XSDataResult.parseString(strExpectedOutput)
        xsDataResultObtained = plugin.getDataOutput()
        EDAssert.strAlmostEqual(xsDataResultReference.marshal(), xsDataResultObtained.marshal(), "XSDataResult output are the same", _strExcluded="bioSaxs")



    def process(self):
        """
        """
        self.addTestMethod(self.testExecute)




if __name__ == '__main__':

    edTest = EDTestCasePluginExecuteControlSaxsAnalysisv1_0("EDTestCasePluginExecuteControlSaxsAnalysisv1_0")
    edTest.execute()
