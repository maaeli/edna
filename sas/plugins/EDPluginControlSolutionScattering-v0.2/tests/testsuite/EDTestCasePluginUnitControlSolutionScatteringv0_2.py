#
#    Project: PROJECT
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) DLS
#
#    Principal author:        irakli
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

__author__ = "irakli"
__license__ = "GPLv3+"
__copyright__ = "DLS"


from EDVerbose import EDVerbose
from EDTestCasePluginUnit import EDTestCasePluginUnit

from XSDataSAS import XSDataInputSolutionScattering

class EDTestCasePluginUnitControlSolutionScatteringv0_2(EDTestCasePluginUnit):


    def __init__(self, _edStringTestName=None):
        EDTestCasePluginUnit.__init__(self, "EDPluginControlSolutionScatteringv0_2")


    def testCheckParameters(self):
        xsDataInput = XSDataInputSolutionScattering()
        edPluginExecSolutionScattering = self.createPlugin()
        edPluginExecSolutionScattering.setDataInput(xsDataInput)
        edPluginExecSolutionScattering.checkParameters()



    def process(self):
        self.addTestMethod(self.testCheckParameters)




if __name__ == '__main__':

    EDTestCasePluginUnitControlSolutionScatteringv0_2 = EDTestCasePluginUnitControlSolutionScatteringv0_2("EDTestCasePluginUnitControlSolutionScatteringv0_2")
    EDTestCasePluginUnitControlSolutionScatteringv0_2.execute()
