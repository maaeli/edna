#
#    Project: mxPluginExec
#             http://www.edna-site.org
#
#    Copyright (C) 2008-2012 European Synchrotron Radiation Facility
#                            Grenoble, France
#
#    Principal authors:      Marie-Francoise Incardona (incardon@esrf.fr)
#                            Olof Svensson (svensson@esrf.fr) 
#
#    Contributing author:    Karl Levik (karl.levik@diamond.ac.uk)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published
#    by the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    and the GNU Lesser General Public License  along with this program.  
#    If not, see <http://www.gnu.org/licenses/>.
#

__authors__ = [ "Olof Svensson", "Marie-Francoise Incardona", "Karl Levik" ]
__contact__ = "svensson@esrf.fr"
__license__ = "LGPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20120712"
__status__ = "production"

import os


from EDTestCasePluginExecute             import EDTestCasePluginExecute
from EDApplication import EDApplication
from XSDataCommon import XSPluginItem

class EDTestCasePluginExecuteMOSFLMv10(EDTestCasePluginExecute):


    def __init__(self, _strTestName=None):
        EDTestCasePluginExecute.__init__(self, _strTestName)
        self.setConfigurationFile(self.getRefConfigFile())
        edPluginMOSFLM = self.createPlugin()
        strResultDir = "executionTestResult"
        strPluginTestDataHome = self.getPluginTestsDataHome()
        self.strExecutionTestDataInputHome = os.path.join(strPluginTestDataHome, "executionTestInput")
        self.strExecutionTestDataResultHome = os.path.join(strPluginTestDataHome, strResultDir)


    def preProcess(self):
        EDTestCasePluginExecute.preProcess(self)
        self.loadTestImage([ "ref-testscale_1_001.img", "ref-testscale_1_002.img" ])

