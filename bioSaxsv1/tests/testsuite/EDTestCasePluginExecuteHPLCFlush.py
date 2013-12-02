# coding: utf8
#
#    Project: <projectName>
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) 2012 ESRF
#
#    Principal author:       JÃ©rÃ´me Kieffer
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

__author__ = "Al. de Maria"
__license__ = "GPLv3+"
__copyright__ = "2012 ESRF"

import os

from EDVerbose                           import EDVerbose
from EDAssert                            import EDAssert
from EDTestCasePluginExecute             import EDTestCasePluginExecute

class EDTestCasePluginExecuteHPLCFlush(EDTestCasePluginExecute):


    def __init__(self, _strTestName=None):
        EDTestCasePluginExecute.__init__(self, "EDPluginBioSaxsFlushHPLCv1_2")
        self.setDataInputFile(os.path.join(self.getPluginTestsDataHome(), "XSDataInputHPLCFlush_reference.xml"))
        
        self.setReferenceDataOutputFile(os.path.join(self.getPluginTestsDataHome(), "BioSaxsFlushHPLCv1_2_dataOutput.xml"))
    
    def preProcess(self):
        """
        PreProcess of the execution test: download a set of images  from http://www.edna-site.org
        and remove any existing output file 
        """
        EDTestCasePluginExecute.preProcess(self)


    def testExecute(self):
        """
        """
        self.run()


    def process(self):
        """
        """
        self.addTestMethod(self.testExecute)


if __name__ == '__main__':

    edTestCase = EDTestCasePluginExecuteHPLCFlush("EDTestCasePluginExecuteHPLCFlush")
    edTestCase.execute()
