# coding: utf-8
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
__date__ = "20130124"

import os, shutil
from EDPluginControl        import EDPluginControl
from EDFactoryPlugin        import edFactoryPlugin
# from EDConfiguration        import EDConfiguration
from suds.client            import Client
from suds.transport.http    import HttpAuthenticated
edFactoryPlugin.loadModule("XSDataBioSaxsv1_0")
from XSDataBioSaxsv1_0      import XSDataInputBioSaxsSolutionScatteringISPyBv1_0, XSDataResultBioSaxsSolutionScatteringISPyBv1_0
# , XSDataBioSaxsSample, XSDataGnom
# from XSDataEdnaSaxs         import XSDataAutoRg
from XSDataCommon           import  XSDataString, XSDataStatus
# XSDataInteger, XSDataDouble, XSDataString, XSDataFile, XSPluginItem, XSDataLength, XSDataBoolean, XSDataStatus


class EDPluginBioSaxsSolutionScatteringISPyBv1_0(EDPluginControl):

    URL = None
    CONF_URL_KEY = "url"
    CONF_URL_DEFAULT = "http://pcantolinos:8080/ispyb-ejb3/ispybWS/ToolsForBiosaxsWebService?wsdl"


    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsSolutionScatteringISPyBv1_0)
        
        self.lstError = []
        # Params to be sent and I dont know them
        self.dammifAvg = None
        self.dammifFilter = None
        self.dammifStart = None
        self.dammifJobs = None
        self.scatterPlotFilePath = None
        self.guinierPlotFilePath = None
        self.kratkyPlotFilePath = None
        


    def checkParameters(self):
        """
        Checks the mandatory parameters.
        sample                 : XSDataBioSaxsSample
        dammifAvg            : XSDataString optional
        dammifFilter        : XSDataString optional
        dammifStart            : XSDataString optional
        dammifJobs            : XSDataString [] optional
        scatterPlotFile        : XSDataFile optional
        guinierPlotFile        : XSDataFile optional
        kratkyPlotFile        : XSDataFile optional
        """
        self.DEBUG("EDPluginBioSaxsSolutionScatteringISPyBv1_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.sample, "Sample is None")

    def configure(self):
        """
        Configures the ISPyB webservice access with the following parameters:
         - The "url" key from config file        
        """
        EDPluginControl.configure(self)
        if self.URL is None:
            self.DEBUG("EDPluginBioSaxsSolutionScatteringISPyBv1_0.configure")
            url = self.config.get(self.CONF_URL_KEY, None)
            if url:
                self.__class__.URL = url
            else:
                self.__class__.URL = self.CONF_URL_DEFAULT


    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)

        # Initializing webservices
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

        # I don't trust in this authentication.... but it is going to work soon
        self.httpAuthenticatedToolsForBiosaxsWebService = HttpAuthenticated(username=user, password=password)
        self.client = Client(self.URL, transport=self.httpAuthenticatedToolsForBiosaxsWebService, cache=None)
        
        
        if self.dataInput.dammifAvg:
            self.dammifAvg = self.dataInput.dammifAvg.value
            
        if self.dataInput.dammifFilter:
            self.dammifFilter = self.dataInput.dammifFilter.value
            
        if self.dataInput.dammifStart:
            self.dammifStart = self.dataInput.dammifStart.value
            
        if self.dataInput.dammifJobs:
            self.dammifJobs = self.dataInput.dammifJobs.value
                     
        if self.dataInput.scatterPlotFile:
            self.scatterPlotFilePath = self.dataInput.scatterPlotFile.path.value
            
        if self.dataInput.guinierPlotFile:
            self.guinierPlotFilePath = self.dataInput.guinierPlotFile.path.value
            
        if self.dataInput.kratkyPlotFile:
            self.kratkyPlotFilePath = self.dataInput.kratkyPlotFile.path.value


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginBioSaxsISPyBv1_0.process")
        try:
            self.copy_to_pyarch()
        except Exception as error:
            strErrorMessage = "Error while copying to pyarch: %s" % error
            self.ERROR(strErrorMessage)
            self.lstError.append(strErrorMessage)

        try:
            self.client.service.storeDataAnalysisSolutionScatteringResultByMeasurementId(
                                    self.dataBioSaxsSample.measurementID.value,
                                    self.dammifAvg,
                                    self.dammifFilter,
                                    self.dammifStart,
                                    self.dammifJobs,
                                    self.scatterPlotFilePath,
                                    self.guinierPlotFilePath,
                                    self.kratkyPlotFilePath,
                                    'extraParam1',
                                    'extraParam2',
                                    'extraParam3',
                                    'extraParam4'
                                    
                                    )
        except Exception, error:
            strError = "ISPyB error: %s" % error
            self.ERROR(strError)
            self.setFailure()

    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        xsDataResult = XSDataResultBioSaxsSolutionScatteringISPyBv1_0(status=XSDataStatus(executiveSummary=XSDataString(os.linesep.join(self.lstError))))
        self.setDataOutput(xsDataResult)
        self.DEBUG("EDPluginBioSaxsSolutionScatteringISPyBv1_0.postProcess")


    def copy_to_pyarch(self):
        if self.dataInput.sample.ispybDestination:
            pyarch = os.path.join(self.dataInput.sample.ispybDestination.path.value, "subs")
            try:
                if not os.path.isdir(pyarch):
                    os.makedirs(pyarch)
            except IOError as error:
                ermsg = "Error while directory creation in pyarch: %s " % error
                self.lstError.append(ermsg)
                self.WARNING(ermsg)

            try:
                if self.scatterPlotFilePath and os.path.exists(self.scatterPlotFilePath):
                    self.copyfile(self.scatterPlotFilePath, pyarch)
                if self.guinierPlotFilePath and os.path.exists(self.guinierPlotFilePath):
                    self.copyfile(self.guinierPlotFilePath, pyarch)
                if self.kratkyPlotFilePath and os.path.exists(self.kratkyPlotFilePath):
                    self.copyfile(self.kratkyPlotFilePath, pyarch)
            except IOError as error:
                ermsg = "Error copying file in pyarch: %s " % error
                self.lstError.append(ermsg)
                self.WARNING(ermsg)

    def copyfile(self, afile, pyarch):
        afile = self.filename
        try:
            shutil.copy(afile, pyarch)
        except IOError as error:
            ermsg = "Saxs Solution Scattering Error while copying %s to pyarch: %s " % (afile, error)
            self.lstError.append(ermsg)
            self.WARNING(ermsg)
        else:
            self.pyarchfiles.append(os.path.join(pyarch, os.path.basename(afile)))


