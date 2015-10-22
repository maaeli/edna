# coding: utf-8
#
#    Project: templatev1
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) 2012, ESRF Grenoble
#
#    Principal author:        Al. de Maria
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
__copyright__ = "2012, ESRF Grenoble"


from EDVerbose import EDVerbose
from EDTestCasePluginUnit import EDTestCasePluginUnit
from EDFactoryPluginStatic import EDFactoryPluginStatic
EDFactoryPluginStatic.loadModule("XSDataInputBioSaxsISPyBv1_0")
from XSDataBioSaxsv1_0 import XSDataInputBioSaxsToSASv1_0, XSDataFile, XSDataDouble

class EDTestCasePluginUnitBioSaxsISPyB(EDTestCasePluginUnit):
    def __init__(self, _edStringTestName=None):
        EDTestCasePluginUnit.__init__(self, "EDPluginBioSaxsISPyBv1_0")

    def process(self):
        self.addTestMethod(self.testCheckParameters)


if __name__ == '__main__':
    EDTestCasePluginUnitBioSaxsISPyB = EDTestCasePluginUnitBioSaxsISPyB("EDTestCasePluginUnitBioSaxsISPyB")
    EDTestCasePluginUnitBioSaxsISPyB.execute()
