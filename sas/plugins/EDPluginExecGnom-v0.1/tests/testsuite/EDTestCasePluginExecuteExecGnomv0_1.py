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
from EDUtilsFile                         import EDUtilsFile

from XSDataSAS import XSDataFloat


class EDTestCasePluginExecuteExecGnomv0_1(EDTestCasePluginExecute):
    """
    Those are all execution tests for the EDNA Exec plugin Gnomv0_1
    """

    def __init__(self, _strTestName=None):
        """
        """
        EDTestCasePluginExecute.__init__(self, "EDPluginExecGnomv0_1")
        self.setConfigurationFile(self.getRefConfigFile())
        self.setDataInputFile(os.path.join(self.getPluginTestsDataHome(), \
                                           "XSDataInputGnom_reference.xml"))
        self.setReferenceDataOutputFile(os.path.join(self.getPluginTestsDataHome(), \
                                                     "XSDataResultGnom_reference.xml"))


    def testExecute(self):
        """
        """
        self.readGnomDataFile(os.path.join(self.getPluginTestsDataHome(), "lyzexp.dat"))
        self.run()


    def process(self):
        """
        """
        self.addTestMethod(self.testExecute)
        
    def postProcess(self):
        """
        """
        self.getPlugin().plotFittingResults()

    def readGnomDataFile(self, fileName):
        tmpExperimentalDataQ = []
        tmpExperimentalDataValues = []

        dataLines = EDUtilsFile.readFile(fileName).splitlines()[1:]
        for line in dataLines:
            tmpValue = XSDataFloat()
            tmpQ = XSDataFloat()
            lineList = line.split()
            tmpQ.setValue(float(lineList[0]))
            tmpValue.setValue(float(lineList[1]))
            tmpExperimentalDataQ.append(tmpQ)
            tmpExperimentalDataValues.append(tmpValue)
        self.getPlugin().getDataInput().setExperimentalDataQ(tmpExperimentalDataQ)
        self.getPlugin().getDataInput().setExperimentalDataValues(tmpExperimentalDataValues)




if __name__ == '__main__':

    testGnomv0_1instance = EDTestCasePluginExecuteExecGnomv0_1("EDTestCasePluginExecuteExecGnomv0_1")
    testGnomv0_1instance.execute()
