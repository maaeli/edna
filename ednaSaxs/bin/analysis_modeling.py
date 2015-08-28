#!/usr/bin/env python
# coding: utf-8

from __future__ import with_statement

__authors__ = [ "Jérôme Kieffer"]
__contact__ = "jerome.kieffer@esrf.eu"
__license__ = "GPLv3+"
__copyright__ = "European Synchrotron Radiation Facility, Grenoble, France"
__date__ = "20130416"
__status__ = "beta"
__doc__ = """Usage: 


"""

import os, sys, time, threading, gc, types
if sys.version > (3, 0):
    from queue import Queue
else:
    from Queue import Queue

# Append the EDNA kernel source directory to the python path

if not os.environ.has_key("EDNA_HOME"):
    strProgramPath = os.path.abspath(sys.argv[0])
    lPath = strProgramPath.split(os.sep)
    if len(lPath) > 3:
        strEdnaHomePath = os.sep.join(lPath[:-3])
    else:
        raise RuntimeError("Problem in the EDNA_HOME path ... %s" % strEdnaHomePath)
        sys.exit()
    os.environ["EDNA_HOME"] = strEdnaHomePath

sys.path.append(os.path.join(os.environ["EDNA_HOME"], "kernel", "src"))
from EDFactoryPlugin import edFactoryPlugin
edFactoryPlugin.loadModule("XSDataEdnaSaxs")
edFactoryPlugin.loadModule("XSDataBioSaxs")
from XSDataCommon import XSDataDouble, XSDataFile, XSDataString
from XSDataEdnaSaxs import XSDataInputSaxsAnalysisModeling
from EDLogging import EDLogging
from EDJob import EDJob
from EDThreading import Semaphore
from EDUtilsParallel import EDUtilsParallel
from EDStatus import EDStatus

class Reprocess(EDLogging):
    def __init__(self, strPluginName, iNbCpu=None):
        EDLogging.__init__(self)
        self.pluginName = strPluginName
        self.startTime = time.time()
        try:
            self.iNbCpu = int(iNbCpu)
        except:
            self.iNbCpu = EDUtilsParallel.detectNumberOfCPUs()

        self.screen("Initializing Reprocess with max %i jobs in parallel." % self.iNbCpu)
        self.__semaphoreNbThreads = Semaphore(self.iNbCpu)
        EDUtilsParallel.initializeNbThread(self.iNbCpu)
        self.jobQueue = Queue()
        self.processingSem = Semaphore()
        self.statLock = Semaphore()
        self.lastStatistics = "No statistics collected yet, please use the 'collectStatistics' method first"
        self.lastFailure = "No job Failed (yet)"
        self.lastSuccess = "No job succeeded (yet)"


    def startJob(self, xsd):
        """
        @param xsd: XML data structure as a string or path to a string
        @return: jobID which is a sting: Plugin-000001
        """
        self.DEBUG("In %s.startJob()" % self.__class__.__name__)
        if type(xsd) in types.StringTypes:
            if xsd.strip() == "":
                return
            if os.path.isfile(xsd):
                xsd = open(xsd, "rb").read()
        edJob = EDJob(self.pluginName)
        if edJob is None:
            return "Error in load Plugin"
        jobId = edJob.getJobId()
        edJob.setDataInput(xsd)
        self.jobQueue.put(edJob)
        if self.processingSem._Semaphore__value > 0 :
            t = threading.Thread(target=self.startProcessing)
            t.start()
        return jobId

    def startProcessing(self):
        """
        Process all jobs in the queue.
        """
        with self.processingSem:
            while not self.jobQueue.empty():
                self.__semaphoreNbThreads.acquire()
                edJob = self.jobQueue.get()
                edJob.connectSUCCESS(self.successJobExecution)
                edJob.connectFAILURE(self.failureJobExecution)
                edJob.execute()
#                edJob.synchronize()

    def successJobExecution(self, jobId):
        self.DEBUG("In %s.successJobExecution(%s)" % (self.__class__.__name__, jobId))
        with self.locked():
            self.__semaphoreNbThreads.release()
            EDJob.cleanJobfromID(jobId, False)
            self.lastSuccess = jobId
            gc.collect()

    def failureJobExecution(self, jobId):
        self.DEBUG("In %s.failureJobExecution(%s)" % (self.__class__.__name__, jobId))
        with self.locked():
            self.__semaphoreNbThreads.release()
            EDJob.cleanJobfromID(jobId, False)
            self.lastFailure = jobId
            sys.stdout.flush()
            sys.stderr.flush()
            gc.collect()

    def getRunning(self):
        """
        retrieve the list of plugins currently under execution (with their plugin-Id)
        """
        return EDStatus.getRunning()

    def getSuccess(self):
        """
        retrieve the list of plugins finished with success (with their plugin-Id)
        """
        return EDStatus.getSuccess()

    def getFailure(self):
        """
        retrieve the list of plugins finished with failure (with their plugin-Id)
        """
        return EDStatus.getFailure()

    def collectStatistics(self):
        """
        Retrieve some statistics on all EDNA-Jobs
        @return: a page of information about EDNA-jobs
        """
        t = threading.Thread(target=self.statistics)
        t.start()


    def statistics(self):
        """
        retrieve some statistics about past jobs.
        """
        with self.statLock:
            fStartStat = time.time()
            self.lastStatistics = EDJob.stats()
            self.lastStatistics += os.linesep + "Statistics collected on %s, the collect took: %.3fs" % (time.asctime(), time.time() - fStartStat)
        return self.lastStatistics

    def getStatistics(self):
        """
        just return statistics previously calculated
        """
        return self.lastStatistics

    def getJobOutput(self, jobId):
        """
        Retrieve XML output form a job
        @param jobId: name of the job
        @return: output from a job
        """
        return EDJob.getDataOutputFromId(jobId)

    def getJobInput(self, jobId):
        """
        Retrieve XML input from a job
        @param jobId: name of the job
        @return: xml input from a job
        """
        return EDJob.getDataInputFromId(jobId)

    def join(self):
        """
        wait for all jobs to finish
        """
        while not (self.jobQueue.empty() and \
                (self.__semaphoreNbThreads._Semaphore__value == self.iNbCpu) and \
                (EDUtilsParallel.getNbRunning() == 0) and \
                (self.processingSem._Semaphore__value == 1) and\
                (len(EDStatus.getRunning()) == 0)):
            time.sleep(1)




if __name__ == "__main__":
    filerange = None
    rdabs = None
    rdrel = None
    outFile = None
    subFile = None
    #xml = None
    listXml = []
    filenames = []
    if len(sys.argv) == 1:
            print(__doc__)
            sys.exit(1)
    from optparse import OptionParser
    parser = OptionParser(usage="%prog reprocess on SAXS-analysis and modeling pipeline (for scattering curve to ab-initio model", version="%prog 1.0")
    parser.add_option("-d", "--debug",
                      action="store_true", dest="verbose", default=False,
                      help="switch to debug mode")
    parser.add_option("-y", "--yappi", action="store_true",
                      dest="yappi", default=False,
                      help="use an multi-threaded profiler named 'YAPPI'")
    parser.add_option("-n", "--ncpu", dest="ncpu", action="store", type="int",
                      help="limit the number of CPU used", default=None)

    parser.add_option("-p", "--plugin", action="store", type="string",
                      dest="plugin", default="EDPluginControlSaxsAnalysisModelingv1_0",
                      help="use an alternative plugin, by default EDPluginControlSaxsAnalysisModelingv1_0")
#    parser.add_option("-r", "--range", action="store", type="str",
#                      dest="filerange", default=None,
#                      help="the range of frames to merge (by default all)")
#    parser.add_option("-a", "--rdabs", dest="rdabs", action="store", type="float",
#                      help="lower limit for similarity (radiation damage estimation) with first image in the serie", default=None)
#    parser.add_option("-e", "--rdrel", dest="rdrel", action="store", type="float",
#                      help="lower limit for similarity (radiation damage estimation) with previous image in the serie", default=None)

    (options, args) = parser.parse_args()
    print("")
    print("Options:")
    print('========')
    for k, v in options.__dict__.items():
        print("    %s: %s" % (k, v))
    print("")
    reprocess = Reprocess(options.plugin, options.ncpu)
    if options.yappi:
        try:
            import yappi

        except ImportError:
            print("Sorry, I was not able to import Yappi")
            yappi = None
        else:
            yappi.start()
    else:
        yappi = None
    if options.verbose:
        reprocess.setVerboseDebugOn()

    keys = [ os.path.abspath(onefile) for onefile in args if os.path.exists(onefile)]
    keys.sort()
    working_dir = "analyse-modeling-%s" % time.strftime("%Y%m%d-%H%M%S")
    base_dir = os.getcwd()
    os.makedirs(working_dir)
    os.chdir(working_dir)
    for run in keys:
        xsd = XSDataInputSaxsAnalysisModeling(scatterCurve=XSDataFile(XSDataString(run)), graphFormat=XSDataString("png"))
        reprocess.startJob(xsd)

    print("All %i jobs queued after %.3fs" % (len(args), time.time() - reprocess.startTime))
    reprocess.join()
    if yappi: yappi.stop()
    print("All %i jobs processed after %.3fs" % (len(args), time.time() - reprocess.startTime))
    print reprocess.statistics()
    if yappi:
        stat = yappi.get_stats(sort_type=yappi.SORTTYPE_TTOT)
        res = {}
        for i in stat.func_stats:
            if i[0] in res:
                res[i[0]][0] += i[1]
                res[i[0]][1] += i[2]
            else:
                res[i[0]] = [i[1], i[2]]
        keys = res.keys()
        keys.sort(sortn)
        with open("yappi.out", "w") as f:
            f.write("ncall\t\ttotal\t\tpercall\t\tfunction%s" % (os.linesep))
            for i in keys:
                f.write("%8s\t%16s\t%16s\t%s%s" % (res[i][0], res[i][1], res[i][1] / res[i][0], i, os.linesep))
        print("Profiling information written in yappi.out")
