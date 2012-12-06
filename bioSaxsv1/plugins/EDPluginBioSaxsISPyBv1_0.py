# coding: utf8
#
#    Project: BioSaxs
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) 2012 ESRF
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
from __future__ import with_statement
__author__ = "Al. de Maria"
__license__ = "GPLv3+"
__copyright__ = "2012 ESRF"
__status__ = "Development"
__date__ = "20121204"

from EDPluginControl        import EDPluginControl
from EDFactoryPlugin        import edFactoryPlugin
from EDConfiguration        import EDConfiguration
from suds.client            import Client
from suds.transport.http    import HttpAuthenticated
edFactoryPlugin.loadModule("XSDataBioSaxsv1_0")
from XSDataBioSaxsv1_0      import XSDataInputBioSaxsISPyBv1_0, XSDataResultBioSaxsISPyBv1_0, XSDataBioSaxsSample, XSDataGnom
from XSDataEdnaSaxs         import XSDataAutoRg
from XSDataCommon           import XSDataInteger, XSDataDouble, XSDataString, XSDataFile, XSPluginItem, XSDataLength, XSDataBoolean


class EDPluginBioSaxsISPyBv1_0(EDPluginControl):
    """
	This URL will change.... where is the best place??
    """
    URL = "http://pcantolinos:8080/ispyb-ejb3/ispybWS/ToolsForBiosaxsWebService?wsdl"

    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsISPyBv1_0)
        

    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.sample, "Sample is None")

    def configure(self):
        """
        Configures the ISPyB webservice access
        """
        EDPluginControl.configure(self)
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.configure")
        self.URL        = self.URL
        self.user       = self.dataInput.sample.getLogin().getValue() 
        self.password   = self.dataInput.sample.getPasswd().getValue()  


    
    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        
        #Initializing webservices
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.preProcess")
        #I don't trust in this authentication....
        self.httpAuthenticatedToolsForBiosaxsWebService = HttpAuthenticated(username = self.user, password = self.password)
        self.client = Client(self.URL, transport = self.httpAuthenticatedToolsForBiosaxsWebService, cache = None)
        
        # XSDataBioSaxsSample
        self.dataBioSaxsSample = self.dataInput.sample #self.getBiosaxsSample()
        self.dataAutoRg = self.dataInput.autoRg
        self.dataGnom = self.dataInput.gnom
         
        #Params to be sent and I dont know them
        self.volume = self.dataInput.volume.getValue()
        self.framesAverage = self.dataInput.frameAverage.getValue()
        self.framesMerged = self.dataInput.frameMerged.getValue()


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.process")
        try:
            self.client.service.storeDataAnalysisResultByMeasurementId(
                                    self.dataBioSaxsSample.getMeasurementID().getValue(),
                                    self.dataAutoRg.getFilename().getPath().getValue(),
                                    self.dataAutoRg.getRg().getValue(),
                                    self.dataAutoRg.getRgStdev().getValue(),
                                    self.dataAutoRg.getI0().getValue(),
                                    self.dataAutoRg.getI0Stdev().getValue(),
                                    self.dataAutoRg.getFirstPointUsed().getValue(),
                                    self.dataAutoRg.getLastPointUsed().getValue(),
                                    self.dataAutoRg.getQuality().getValue(),
                                    self.dataAutoRg.getIsagregated().getValue(),
                                    self.dataBioSaxsSample.getCode().getValue(),
                                    self.dataBioSaxsSample.getConcentration().getValue(),
                                    self.dataGnom.getGnomFile().getPath().getValue(),
                                    self.dataGnom.getRgGuinier().getValue(),
                                    self.dataGnom.getRgGnom().getValue(),
                                    self.dataGnom.getDmax().getValue(),
                                    self.dataGnom.getTotal().getValue(),
                                    self.volume,
                                    self.framesAverage,
                                    self.framesMerged,
                                    "param1",
                                    "param2",
                                    "param3",
                                    "param4"
                                    )
        except:
            print "ISPyB error:"
            self.ERROR(ValueError)
            raise
            
        

    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.postProcess")
        # Create some output data
        xsDataResult = XSDataResultBioSaxsISPyBv1_0()
        self.setDataOutput(xsDataResult)

