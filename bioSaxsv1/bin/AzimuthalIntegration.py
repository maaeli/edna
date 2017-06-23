#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#    Project: BioSaxs
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) European Synchrotron Radiation Facility, Grenoble, France
#
#    Principal author:       Jérôme Kieffer (Jerome.Kieffer@ESRF.eu)
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
__author__ = "Jérôme Kieffer"
__contact__ = "Jerome.Kieffer@ESRF.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__version__ = "20130226"

import os, sys, optparse, multiprocessing, threading, types, time
if sys.version > (3, 0):
    from queue import Queue
else:
    from Queue import Queue

# Append the EDNA kernel source directory to the python path
if not os.environ.has_key("EDNA_HOME"):
    pyStrProgramPath = os.path.abspath(sys.argv[0])
    pyLPath = pyStrProgramPath.split(os.sep)
    if len(pyLPath) > 3:
        pyStrEdnaHomePath = os.sep.join(pyLPath[:-3])
    else:
        print ("Problem in the EDNA_HOME path ..." + pyStrEdnaHomePath)
        sys.exit()

    os.environ["EDNA_HOME"] = pyStrEdnaHomePath

sys.path.append(os.path.join(os.environ["EDNA_HOME"], "kernel", "src"))

from EDVerbose import EDVerbose
from EDJob import EDJob
from EDThreading import Semaphore
# from EDParallelExecute  import EDParallelExecute


class Reprocess(object):
    EDNAPluginName = "EDPluginBioSaxsProcessOneFilev1_4"
    hc = 12.398419292004204
    def __init__(self):
        self.XML = "<XSDataInput>\
<normalizedImage><path><value>${FULLPATH}</value></path></normalizedImage>\
<correctedImage><path><value>${DIRDIRNAME}/2d/${BASENAME}.edf</value></path></correctedImage>\
<normalizedImageSize><value>4100000</value></normalizedImageSize>\
<integratedCurve><path><value>${DIRDIRNAME}/1d/${BASENAME}.edf</value></path></integratedCurve>\
<maskFile><path><value>${MASKFILE}</value></path></maskFile>\
<code><value>BSA</value></code>\
</XSDataInput>"
        self.maskfile = None
        self.dataFiles = []
        self.wavelength = 1.0
        self.debug = False
        self.mode = "offline"
        self.newerOnly = False
        self.nbcpu = multiprocessing.cpu_count()
        self.cpu_sem = Semaphore(self.nbcpu)
        self.process_sem = Semaphore()
        self.queue = Queue()
        
    def fileName2xml(self, filename):
        """Here we create the XML string to be passed to the EDNA plugin from the input filename
        This can / should be modified by the final user
        
        @param filename: full path of the input file
        @type filename: python string representing the path
        @rtype: XML string
        @return: python string  
        """
        if filename.endswith(".edf"):
            FULLPATH = os.path.abspath(filename)
            DIRNAME, NAME = os.path.split(FULLPATH)
            DIRDIRNAME = os.path.dirname(DIRNAME)
            BASENAME, EXT = os.path.splitext(NAME)
            if not os.path.isdir(os.path.join(DIRDIRNAME, "1d")):
                   os.makedirs(os.path.join(DIRDIRNAME, "1d"), int("775", 8))
            return self.xml.replace("${FULLPATH}", FULLPATH).\
                replace("${DIRNAME}", DIRNAME).replace("${NAME}", NAME).\
                replace("${DIRDIRNAME}", DIRDIRNAME).replace("${BASENAME}", BASENAME).\
                replace("${EXT}", EXT).replace("$MASKFILE", self.maskfile or "")

    def XMLerr(self, strXMLin):
        """
        This is an example of XMLerr function ... it prints only the name of the file created
        @param srXMLin: The XML string used to launch the job
        @type strXMLin: python string with the input XML
        @rtype: None
        @return: None     
        """
        self.cpu_sem.release()
        if type(strXMLin) not in types.StringTypes:
            strXMLin= strXMLin.marshal()
        EDVerbose.WARNING("Error in the processing of :\n%s" % strXMLin)
        return None

    def XMLsuccess(self, strXMLin):
        """
        This is an example of XMLerr function ... it prints only the name of the file created
        @param srXMLin: The XML string used to launch the job
        @type strXMLin: python string with the input XML
        @rtype: None
        @return: None     
        """
        self.cpu_sem.release()
#        EDVerbose.WARNING("Error in the processing of :\n%s" % strXMLin)
        return None


    def parse(self):
        """
        parse options from command line
        """
        parser = optparse.OptionParser()
        parser.add_option("-V", "--version", dest="version", action="store_true",
                          help="print version of the program and quit", metavar="FILE", default=False)
        parser.add_option("-v", "--verbose",
                          action="store_true", dest="debug", default=False,
                          help="switch to debug/verbose mode")
        parser.add_option("-m", "--mask", dest="mask",
                      help="file containing the mask (for image reconstruction)", default=None)
        parser.add_option("-M", "--mode", dest="mode",
                      help="Mode can be online/offline/all", default="offline")
        parser.add_option("-o", "--out", dest="output",
                      help="file for log", default=None)
        parser.add_option("-w", "--wavelength", dest="wavelength", type="float",
                      help="wavelength of the X-Ray beam in Angstrom", default=None)
        parser.add_option("-e", "--energy", dest="energy", type="float",
                      help="energy of the X-Ray beam in keV (hc=%skeV.A)" % self.hc, default=None)
        parser.add_option("-t", "--template", dest="template", type="str",
                      help="template XML file", default=None)
        parser.add_option("-n", "--nbcpu", dest="nbcpu", type="int",
                      help="template XML file", default=self.nbcpu)


        (options, args) = parser.parse_args()

        # Analyse aruments and options
        if options.version:
            print("BioSaxs Azimuthal integration version %s" % __version__)
            sys.exit(0)
        if options.debug:
            EDVerbose.setVerboseDebugOn()
            self.debug = True
        if options.output:
            EDVerbose.setLogFileName(options.output)
        if options.mask and os.path.isfile(options.mask):
            self.maskfile = options.mask
        if options.template and os.path.isfile(options.template):
            self.xml = open(options.template).read()
        if options.wavelength:
            self.wavelength = 1e-10 * options.wavelength
        elif options.energy:
            self.wavelength = 1e-10 * self.hc / options.energy
        if options.mode=="offline":
            self.mode = "offline"
            self.newerOnly = False
        elif options.mode=="online":
            self.mode = "dirwarch"
            self.newerOnly = True
        elif options.mode=="dirwatch":
            self.mode = "dirwarch"
            self.newerOnly = False
        self.cpu_sem = Semaphore(options.nbcpu)
        self.nbcpu = options.nbcpu
        self.dataFiles = [f for f in args if os.path.isfile(f)]
        if not self.dataFiles:
            raise RuntimeError("Please provide datafiles or read the --help")


    def process(self):
        for fn in self.dataFiles:
            EDVerbose.screen("Processing file %s" % fn)
            edj = EDJob(self.EDNAPluginName)
            edj.dataInput = self.fileName2xml(fn)
            edj.connectSUCCESS(self.XMLsuccess)
            edj.connectFAILURE(self.XMLerr)
            self.queue.put(edj)
            if self.process_sem._Semaphore__value > 0 :
                t = threading.Thread(target=self.startProcessing)
                t.start()
        EDVerbose.screen("Back in main")
        while self.cpu_sem._Semaphore__value < self.nbcpu:
            time.sleep(0.1)
        EDJob.synchronizeAll()
        EDJob.stats()

    def startProcessing(self):
        with self.process_sem:
            while not self.queue.empty():
                self.cpu_sem.acquire()
                edj = self.queue.get()
                edj.execute()
#                    edj.synchronize()



if __name__ == '__main__':
    r = Reprocess()
    r.parse()
    r.process()

