#
#    Project: PROJECT
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

__author__ = "irakli"
__license__ = "GPLv3+"
__copyright__ = "DLS"

import os

from EDTestCasePluginExecute             import EDTestCasePluginExecute

from XSDataCommon import XSDataString
from parse_atsas import get_ATSAS_version


class EDTestCasePluginExecuteExecDamaverv0_3(EDTestCasePluginExecute):
    """
    Those are all execution tests for the EDNA Exec plugin Damaverv0_3
    """

    def __init__(self, _strTestName=None):
        """
        """
        EDTestCasePluginExecute.__init__(self, "EDPluginExecDamaverv0_3")
#        self.setConfigurationFile(os.path.join(self.getPluginTestsDataHome(),
#                                               "XSConfiguration_Damaver.xml"))
        self.setDataInputFile(os.path.join(self.getPluginTestsDataHome(), \
                                           "XSDataInputDamaver_reference.xml"))
#         if get_ATSAS_version()<2962:
        ref = "XSDataResultDamaver_reference.xml"
#         else:
#             ref = "XSDataResultDamaver_reference.xml.2962"           
        self.setReferenceDataOutputFile(os.path.join(self.getPluginTestsDataHome(), ref))


    def testExecute(self):
        """
        """
        # Add path to the input data file
        for pdbInputFile in self.getPlugin().getDataInput().getPdbInputFiles():
            dataInputName = pdbInputFile.getPath().getValue()
            pdbInputFile.setPath(XSDataString(os.path.join(self.getPluginTestsDataHome(), dataInputName)))

        self.run()


    def process(self):
        """
        """
        self.addTestMethod(self.testExecute)



if __name__ == '__main__':

    testDamaverv0_3instance = EDTestCasePluginExecuteExecDamaverv0_3("EDTestCasePluginExecuteExecDamaverv0_3")
    testDamaverv0_3instance.execute()
