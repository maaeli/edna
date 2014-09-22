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
__date__ = "20131003"

import os, shutil
from EDPluginControl        import EDPluginControl
from EDFactoryPlugin        import edFactoryPlugin
from suds.client            import Client
from suds.transport.http    import HttpAuthenticated
edFactoryPlugin.loadModule("XSDataBioSaxsv1_0")
from XSDataBioSaxsv1_0      import XSDataInputBioSaxsISPyB_HPLCv1_0, XSDataResultBioSaxsISPyB_HPLCv1_0
from XSDataCommon           import  XSDataString, XSDataStatus


class EDPluginBioSaxsISPyB_HPLCv1_0(EDPluginControl):

    URL = None
    CONF_URL_KEY = "url"
    CONF_URL_DEFAULT = "http://ispyvalid.esrf.fr:8080/ispyb-ejb3/ispybWS/ToolsForBiosaxsWebService?wsdl"


    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsISPyB_HPLCv1_0)
        self.dataBioSaxsSample = None
        self.pyarchcurves = []
        self.pyarchgraph = {}
        self.lstError = []
        self.code = "opd"
        self.number = "29"
        self.hdf5File = None
        self.jsonFile = None
        self.hplcPlot = None


    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginBioSaxsISPyB_HPLCv1_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.sample, "Sample is None")

    def configure(self):
        """
        Configures the ISPyB_HPLC webservice access with the following parameters:
         - The "url" key from config file        
        """
        EDPluginControl.configure(self)
        if self.URL is None:
            self.DEBUG("EDPluginBioSaxsISPyB_HPLCv1_0.configure")
            url = self.config.get(self.CONF_URL_KEY, None)
            if url:
                self.__class__.URL = url
            else:
                self.__class__.URL = self.CONF_URL_DEFAULT


    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)
        # Initializing webservices
        self.DEBUG("EDPluginBioSaxsISPyB_HPLCv1_0.preProcess")
        self.dataBioSaxsSample = self.dataInput.sample
        user = None
        password = ""
        if self.dataBioSaxsSample:
            if self.dataBioSaxsSample.login:
                user = self.dataBioSaxsSample.login.value
                password = self.dataBioSaxsSample.passwd.value
                if self.dataBioSaxsSample.ispybURL:
                    self.URL = self.dataBioSaxsSample.ispybURL.value
        if not user:
            self.ERROR("No login/password information in sample configuration. Giving up. falling back on test mode")
#             self.setFailure()
#             return
            user = "opd29"
            password = "tonic29"


        # I don't trust in this authentication.... but it is going to work soon

        self.httpAuthenticatedToolsForBiosaxsWebService = HttpAuthenticated(username=user, password=password)
        self.client = Client(self.URL, transport=self.httpAuthenticatedToolsForBiosaxsWebService, cache=None)
        self.hdf5File = self.dataInput.hdf5File.path.value
        self.jsonFile = self.dataInput.jsonFile.path.value
        self.hplcPlot = self.dataInput.hplcPlot.path.value


    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginBioSaxsISPyB_HPLCv1_0.process")
        try:
            self.copy_to_pyarch()
        except Exception as error:
            strErrorMessage = "Error while copying to pyarch: %s" % error
            self.ERROR(strErrorMessage)
            self.lstError.append(strErrorMessage)
        if self.dataInput.sample.collectionOrder is not None:
            collectionOrder = str(self.dataInput.sample.collectionOrder.value)
        else:
            collectionOrder = "-1"
        try:
            self.client.service.storeHPLC(
                                    self.code,
                                    self.number,
                                    self.hdf5File,
                                    self.jsonFile,
                                    self.hplcPlot)
        except Exception, error:
            strError = "ISPyB error: %s" % error
            self.ERROR(strError)
            self.setFailure()


    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginBioSaxsISPyB_HPLCv1_0.postProcess")
        # Create some output data

        xsDataResult = XSDataResultBioSaxsISPyB_HPLCv1_0(status=XSDataStatus(executiveSummary=XSDataString(os.linesep.join(self.lstError))))
        self.setDataOutput(xsDataResult)

    def copy_to_pyarch(self):
        if self.dataInput.sample.ispybDestination:
            pyarch = os.path.join(self.dataInput.sample.ispybDestination.path.value, "HPLC", self.dataInput.sample.measurementID.value)
            try:
                if not os.path.isdir(pyarch):
                    os.makedirs(pyarch)
            except IOError as error:
                ermsg = "Error while directory creation in pyarch: %s " % error
                self.lstError.append(ermsg)
                self.ERROR(ermsg)
            self.hdf5File = self.copyfile(self.hdf5File, pyarch)
            self.jsonFile = self.copyfile(self.jsonFile, pyarch)
            self.hplcPlot = self.copyfile(self.hplcPlot, pyarch)

    def copyfile(self, afile, pyarch, dest="curve"):
        if not pyarch:
            self.ERROR("pyArch is %s" % pyarch)
        if afile and os.path.exists(afile) and os.path.isdir(pyarch):
            try:
                shutil.copy(afile, pyarch)
            except IOError as error:
                ermsg = "Error while copying %s to pyarch %s: %s " % (afile, pyarch, error)
                self.lstError.append(ermsg)
                self.WARNING(ermsg)
            else:
                return os.path.join(pyarch, afile)
