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
__date__ = "20130124"

import os, shutil
from EDPluginControl        import EDPluginControl
from EDFactoryPlugin        import edFactoryPlugin
from suds.client            import Client
from suds.transport.http    import HttpAuthenticated
edFactoryPlugin.loadModule("XSDataBioEdnaSaxsv1_0")
from XSDataBioSaxsv1_0      import XSDataInputBioSaxsISPyBModellingv1_0, XSDataResultBioSaxsISPyBModellingv1_0
from XSDataCommon           import  XSDataString, XSDataStatus



class EDPluginBioSaxsISPyBModellingv1_0(EDPluginControl):

    URL = None
    CONF_URL_KEY = "url"
    CONF_URL_DEFAULT = "http://pcantolinos:8080/ispyb-ejb3/ispybWS/ToolsForBiosaxsWebService?wsdl"


    def __init__(self):
        """
        """
        EDPluginControl.__init__(self)
        self.setXSDataInputClass(XSDataInputBioSaxsISPyBModellingv1_0)
       
        # Params to be sent and I dont know them
        self.modellingResult = None


    def checkParameters(self):
        """
        Checks the mandatory parameters.
        """
        self.DEBUG("EDPluginBioSaxsISPyBModellingv1_0.checkParameters")
        self.checkMandatoryParameters(self.dataInput, "Data Input is None")
        self.checkMandatoryParameters(self.dataInput.sample, "Sample is None")
        self.checkMandatoryParameters(self.dataInput.saxsModelingResult, "SaxsModelingResult is None")


    def configure(self):
        """
        Configures the ISPyB webservice access with the following parameters:
         - The "url" key from config file        
        """
        EDPluginControl.configure(self)
      


    def preProcess(self, _edObject=None):
        EDPluginControl.preProcess(self)

        # Initializing webservices
        self.DEBUG("EDPluginBioSaxsISPyBModellingv1_0.preProcess")
        self.dataBioSaxsSample = self.dataInput.sample
    
        self.URL = self.dataBioSaxsSample.ispybURL
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
        self.client = Client(self.dataBioSaxsSample.ispybURL, transport=self.httpAuthenticatedToolsForBiosaxsWebService, cache=None)

       
    def process(self, _edObject=None):
        EDPluginControl.process(self)
        self.DEBUG("EDPluginBioSaxsISPyBModellingv1_0.process")
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
            self.id = self.dataInput.sample.measurementID
            self.concentrations = [2.4, 4.5,7]
            self.models = "[{pdbFile: '/data/../dammif1.pdb', rg: '1.23', dMax: '232', I0: '12121'}, {pdbFile: '/data/../dammif2.pdb', rg: '2.23', dMax: '232', I0: '12121'}]"
            self.dammaver = "{pdbFile: '/data/../dammif1.pdb', rg: '1.23', dMax: '232', I0: '12121'}"
            self.dammif = "{pdbFile: '/data/../dammif1.pdb', rg: '1.23', dMax: '232', I0: '12121'}"
            self.damming = "{pdbFile: '/data/../damming1.pdb', rg: '1.23', dMax: '232', I0: '12121'}"
            self.nsdPlot = '/data/../nsd.png'
            self.chi2plot = '/data/../chi2plot.png'           
            return self.client.service.storeAbInitioModels(self.id, str(self.concentrations), self.models, self.dammaver, self.dammif, self.damming, self.nsdPlot, self.chi2plot)
           
        except Exception, error:
            strError = "ISPyB error: %s" % error
            self.ERROR(strError)
            self.setFailure()


    def postProcess(self, _edObject=None):
        EDPluginControl.postProcess(self)
        self.DEBUG("EDPluginBioSaxsISPyBModellingv1_0.postProcess")
        # Create some output data

        xsDataResult = XSDataResultBioSaxsISPyBModellingv1_0(status=XSDataStatus(executiveSummary=XSDataString(os.linesep.join(self.lstError))))
        self.setDataOutput(xsDataResult)

    def copy_to_pyarch(self):
        if self.dataInput.sample.ispybDestination:
            pyarch = os.path.join(self.dataInput.sample.ispybDestination.path.value, "1d")
            try:
                if not os.path.isdir(pyarch):
                    os.makedirs(pyarch)
            except IOError as error:
                ermsg = "Error while directory creation in pyarch: %s " % error
                self.lstError.append(ermsg)
                self.ERROR(ermsg)
            for xsdfile in self.dataInput.curves:
                if xsdfile:
                    self.copyfile(xsdfile.path.value, pyarch)
            self.copyfile(self.filename, pyarch)
            self.copyfile(self.gnomFile, pyarch)
            self.copyfile(self.bestBuffer, pyarch)
            self.copyfile(self.scatterPlot, pyarch,"scatterPlot")
            self.copyfile(self.guinierPlot, pyarch,"guinierPlot")
            self.copyfile(self.kratkyPlot, pyarch,"kratkyPlot")
            self.copyfile(self.densityPlot, pyarch,"densityPlot")

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
                if dest=="curve":
                    self.pyarchcurves.append(os.path.join(pyarch, os.path.basename(afile)))
                else:
                    self.pyarchgraph[dest]=os.path.join(pyarch, os.path.basename(afile))
