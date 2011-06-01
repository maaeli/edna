#
#    Project: mxPluginExec
#             http://www.edna-site.org
#
#    File: "$Id: EDTestCasePluginExecuteBestv1_2_withDetectorDistanceMax.py 1943 2010-08-23 13:59:41Z svensson $"
#
#    Copyright (C) 2008-2009 European Synchrotron Radiation Facility
#                            Grenoble, France
#
#    Principal authors:      Marie-Francoise Incardona (incardon@esrf.fr)
#                            Olof Svensson (svensson@esrf.fr) 
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


__authors__ = [ "Olof Svensson", "Marie-Francoise Incardona" ]
__contact__ = "svensson@esrf.fr"
__license__ = "LGPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"


from EDVerbose                           import EDVerbose
from EDAssert                            import EDAssert
from EDUtilsTest                         import EDUtilsTest
from EDUtilsPath                         import EDUtilsPath
from EDTestCasePluginExecuteBestv1_2     import EDTestCasePluginExecuteBestv1_2



class EDTestCasePluginExecuteBestv1_2_withDetectorDistanceMax(EDTestCasePluginExecuteBestv1_2):

    def __init__(self, _oalStringTestName=None):
        EDTestCasePluginExecuteBestv1_2.__init__(self, "EDPluginBestv1_2")

        self.setConfigurationFile(self.getRefConfigFile())
        self.setDataInputFile(EDUtilsPath.mergePath(self.getPluginTestsDataHome(), "XSDataInputBest_withDetectorDistanceMax.xml"))
        if (self.m_bRunOnIntel):
            self.setReferenceDataOutputFile(EDUtilsPath.mergePath(self.getPluginTestsDataHome(), "XSDataResultBest_withDetectorDistanceMaxForIntel.xml"))
        else:
            self.setReferenceDataOutputFile(EDUtilsPath.mergePath(self.getPluginTestsDataHome(), "XSDataResultBest_withDetectorDistanceMax.xml"))


    def testExecute(self):
        self.run()
        
        xsDataResultBest = self.getPlugin().getDataOutput()
        fDistance = xsDataResultBest.getCollectionPlan()[0].getStrategySummary().getDistance().getValue()
        EDAssert.lowerThan(fDistance, 500.0, "Distance shorter than max distance 500 mm")


    def process(self):
        self.addTestMethod(self.testExecute)


if __name__ == '__main__':

    edTestCasePluginExecuteBestv1_2_withDetectorDistanceMax = EDTestCasePluginExecuteBestv1_2_withDetectorDistanceMax("EDTestCasePluginExecuteBestv1_2_withDetectorDistanceMax")
    edTestCasePluginExecuteBestv1_2_withDetectorDistanceMax.execute()
