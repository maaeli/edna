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
#                             Jerome Kieffer
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

    URL = None
    CONF_URL_KEY = "url"
    CONF_URL_DEFAULT = "http://pcantolinos:8080/ispyb-ejb3/ispybWS/ToolsForBiosaxsWebService?wsdl"


    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsISPyBv1_0)
        self.dataBioSaxsSample = None
        self.dataAutoRg = None
        self.dataGnom = None

        #Params to be sent and I dont know them
        self.volume = None
        self.framesAverage = None
        self.framesMerged = None


    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.sample, "Sample is None")

    def configure(self):
        """
        Configures the ISPyB webservice access with the following parameters:
         - The "url" key from config file        
        """
        EDPluginControl.configure(self)
        if self.URL is None:
            self.DEBUG("EDPluginBioSaxsISPyBv1_0.configure")
            url = self.config.get(self.CONF_URL_KEY, None)
            if url:
                self.__class__.URL = url
            else:
                self.__class__.URL = self.CONF_URL_DEFAULT


    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)

        #Initializing webservices
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.preProcess")
        self.dataBioSaxsSample = self.dataInput.sample
        user = None
        password = ""
        if self.dataBioSaxsSample:
            if self.dataBioSaxsSample.login:
                user = self.dataBioSaxsSample.login.value
                password = self.dataBioSaxsSample.passwd.value
        if not user:
            self.ERROR("No login/password information in sample configuration. Giving up.")
            self.setFailure()
            return

        #I don't trust in this authentication....

        self.httpAuthenticatedToolsForBiosaxsWebService = HttpAuthenticated(username=user, password=password)
        self.client = Client(self.URL, transport=self.httpAuthenticatedToolsForBiosaxsWebService, cache=None)

        self.dataAutoRg = self.dataInput.autoRg
        self.dataGnom = self.dataInput.gnom

        #Params to be sent and I dont know them
        if self.dataInput.volume:
            self.volume = self.dataInput.volume.value

        self.framesAverage = self.dataInput.frameAverage.value
        self.framesMerged = self.dataInput.frameMerged.value


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.process")
        try:
            self.client.service.storeDataAnalysisResultByMeasurementId(
                                    self.dataBioSaxsSample.measurementID.value,
                                    self.dataAutoRg.filename.path.value,
                                    self.dataAutoRg.rg.value,
                                    self.dataAutoRg.rgStdev.value,
                                    self.dataAutoRg.i0.value,
                                    self.dataAutoRg.i0Stdev.value,
                                    self.dataAutoRg.firstPointUsed.value,
                                    self.dataAutoRg.lastPointUsed.value,
                                    self.dataAutoRg.quality.value,
                                    self.dataAutoRg.isagregated.value,
                                    self.dataBioSaxsSample.code.value,
                                    self.dataBioSaxsSample.concentration.value,
                                    self.dataGnom.gnomFile.path.value,
                                    self.dataGnom.rgGuinier.value,
                                    self.dataGnom.rgGnom.value,
                                    self.dataGnom.dmax.value,
                                    self.dataGnom.total.value,
                                    self.volume,
                                    self.framesAverage,
                                    self.framesMerged,
                                    "param1",
                                    "param2",
                                    "param3",
                                    "param4"
                                    )
        except Exception, error:
            strError = "ISPyB error: %s" % error
            self.ERROR(strError)
            self.setFailure()



    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.postProcess")
        # Create some output data
        xsDataResult = XSDataResultBioSaxsISPyBv1_0()
        self.setDataOutput(xsDataResult)

