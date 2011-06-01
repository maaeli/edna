#
#    Project: PROJECT
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) DLS 2010
#
#    Principal author:       Mark Basham
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
__author__="Mark Basham"
__license__ = "GPLv3+"
__copyright__ = "DLS 2010"

from EDImportLib  import EDCompiler
from EDTestSuite  import EDTestSuite

class EDTestSuitePluginControlTomographyv10( EDTestSuite ):
    """
    This is the test suite for EDNA plugin Tomographyv10 
    It will run subsequently all unit tests and execution tests. 
    
    """        

    def process( self ):
        """
        """
        self.addTestCaseFromName( "EDTestCasePluginUnitControlTomographyv10" )
        self.addTestCaseFromName( "EDTestCasePluginExecuteControlTomographyv10" )
        


##############################################################################
if __name__ == '__main__':

    # JIT compiler accelerator
    EDCompiler.accelerator()

    edTestSuitePluginControlTomographyv10 = EDTestSuitePluginControlTomographyv10( "EDTestSuitePluginControlTomographyv10" )
    edTestSuitePluginControlTomographyv10.execute()

##############################################################################
