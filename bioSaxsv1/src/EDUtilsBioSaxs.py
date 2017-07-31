#
#coding: utf8
#
#    Project: BioSaxs : ID14-3
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) ESRF
#
#    Principal author:        Jérôme Kieffer
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
from Cython.Plex.Regexps import Opt
"""
Utilities for BioSaxs, especially for logging back both to EDNA using EDVerbose and to BioSaxsCube through SpecVariable
"""

__author__ = "Jérôme Kieffer"
__license__ = "GPLv3+"
__copyright__ = "ESRF"

import sys
import os
import time
import traceback
from EDUtilsPlatform import EDUtilsPlatform
from EDThreading import Semaphore
from EDUtilsPath import EDUtilsPath
architecture = EDUtilsPlatform.architecture
specClientPath = os.path.join(EDUtilsPath.EDNA_HOME, "libraries", "SpecClient", architecture)
if os.path.isdir(specClientPath) and (specClientPath not in sys.path):
    sys.path.insert(1, specClientPath)


from EDVerbose import EDVerbose
from EDObject import EDObject
try:
    from SpecClient import SpecVariable
except:
    SpecVariable = None

import h5py
import numpy
import matplotlib
import json
matplotlib.use('Agg')
from matplotlib import pylab
import scipy.integrate as scint
from signalProcessing import find_peaks_cwt
from scipy.signal import medfilt, butter, filtfilt
from scipy.optimize import curve_fit
from math import floor as mfloor
import numpy as np


class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class EDUtilsBioSaxs(EDObject):

    DETECTORS = ["pilatus", "vantec"]
    OPERATIONS = ["normalisation", "reprocess", "average", "complete"]
    TRANSLATION = {"beamStopDiode": "DiodeCurr",
                   "machineCurrent": "MachCurr",
                   "concentration": "Concentration",
                   "comments": "Comments",
                   "code": "Code",
                   "maskFile": "Mask",
                   "normalizationFactor": "Normalization",
                   "beamCenter_1": "Center_1",
                   "beamCenter_2": "Center_2",
                   "pixelSize_1": "PSize_1",
                   "pixelSize_2": "PSize_2",
                   "detectorDistance": "SampleDistance",
                   "wavelength": "WaveLength",
                   "detector": "Detector",
                   "storageTemperature": "storageTemperature",
                   "exposureTemperature": "exposureTemperature",
                   "exposureTime": "exposureTime",
                   "frameNumber": "frameNumber",
                   "frameMax": "frameMax",
                   "timeOfFrame": "time_of_day"
                   }
    FLOAT_KEYS = ["beamStopDiode", "machineCurrent", "concentration", "normalizationFactor",
                  "beamCenter_1", "beamCenter_2", "pixelSize_1", "pixelSize_2",
                  "detectorDistance", "wavelength", "timeOfFrame",
                  "storageTemperature", "exposureTemperature", "exposureTime"]
    INT_KEYS = ["frameNumber", "frameMax"]

    __strSpecVersion = None
    __strSpecStatus = None
    __strSpecAbort = None
    __specVarStatus = None
    __specVarAbort = None

    @staticmethod
    def initSpec(_strSpecVersion, _strSpecStatus, _strSpecAbort):
        """
        Initialization of SpecVariable  ...
        """
        if EDUtilsBioSaxs.specVersion is None:
            EDUtilsBioSaxs.__strSpecVersion = _strSpecVersion
            EDUtilsBioSaxs.__strSpecStatus = _strSpecStatus
            EDUtilsBioSaxs.__strSpecAbort = _strSpecAbort
            if SpecVariable:
                EDUtilsBioSaxs.__specVarStatus = SpecVariable.SpecVariable(_strSpecStatus)
                EDUtilsBioSaxs.__specVarAbort = SpecVariable.SpecVariable(_strSpecAbort)
        else:
            EDVerbose.DEBUG("EDUtilsBioSaxs initSpec called whereas it was already set-up")
            if EDUtilsBioSaxs.__strSpecVersion != _strSpecVersion:
                EDVerbose.WARNING("EDUtilsBioSaxs initSpec specVersion %s whereas configured with %s"
                                  % (_strSpecVersion, EDUtilsBioSaxs.__strSpecVersion))
            if EDUtilsBioSaxs.__strSpecStatus != _strSpecStatus:
                EDVerbose.WARNING("EDUtilsBioSaxs initSpec specStatus %s whereas configured with %s"
                                  % (_strSpecVersion, EDUtilsBioSaxs.__strSpecVersion))
            if EDUtilsBioSaxs.__strSpecAbort != _strSpecAbort:
                EDVerbose.WARNING("EDUtilsBioSaxs initSpec specAbort %s whereas configured with %s"
                                  % (_strSpecVersion, EDUtilsBioSaxs.__strSpecVersion))

    @staticmethod
    def showMessage(_iLevel, _strMessage, _strFilename=None):
        """
        Class Method:
        Similar to logging module of python but for updating BioSaxsCube

        @param _iLevel: print level seems to be
                        4 for Errors
                        3 for Warnings
                        2 for Info
                        1
                        0
        @type _iLevel: int
        @param _strMessage: comment to be printed
        @type _strMessage: string
        @param _strFilename: the file related to the message (nothing to do with a logfile)
        @type _strFilename: string or None
        """

        if _iLevel == 4:
            EDVerbose.ERROR(_strMessage)
        elif _iLevel == 3:
            EDVerbose.WARNING(_strMessage)
        else:
            EDVerbose.screen(_strMessage)
#        else:
#            EDVerbose.DEBUG(_strMessage)

        if EDUtilsBioSaxs.specStatus is not None:
            currentStatus = EDUtilsBioSaxs.specStatus.value["reprocess"]["status"]     # must do this, since SpecClient is apparently returning a non-expected data structure
            i = currentStatus.rfind(",")
            # TB: This ,1 or ,0 suffix nonsense seems to be a hack to force Spec to signal a variable change to bsxcube
            if i == -1 or currentStatus[i + 1:] == "1":
                if _strFilename is None:
                    newStatus = "%s,%s,0" % (_iLevel, _strMessage)
                else:
                    newStatus = "%s,%s,%s,0" % (_iLevel, _strMessage, _strFilename)
            else:
                if _strFilename is None:
                    newStatus = "%s,%s,1" % (_iLevel, _strMessage)
                else:
                    newStatus = "%s,%s,%s,1" % (_iLevel, _strMessage, _strFilename)
            EDUtilsBioSaxs.specStatus.setValue(newStatus)

        if (EDUtilsBioSaxs.specAbort is not None) and (EDUtilsBioSaxs.specAbort.value["reprocess"]["abort"]) == "1":
            # must do this, since SpecClient is apparently returning a non-expected data structure
            EDVerbose.ERROR("Aborting data reprocess!")
#            sys.exit(0)

    @staticmethod
    def getFilenameDetails(_strFilename):
        """
        Split the name of the file in 4 components:
        prefix_run_frame_extra.extension
        @return: prefix, run, frame, extra, extension
        @rtype: 4-tuple of strings
        """
        _strFilename = str(_strFilename)
        filei, extension = os.path.splitext(_strFilename)

        items = filei.split("_")
        prefix = items[0]
        run = ""
        frame = ""
        extra = ""

        for oneItem in items[1:]:
            if oneItem.isdigit():
                if run == "":
                    run = oneItem
                elif frame == "":
                    frame = oneItem
                elif extra == "":
                    extra = oneItem
                else:
                    extra += "_" + oneItem
            else:
                if run == "":
                    prefix += "_" + oneItem
                else:
                    extra += "_" + oneItem

        try: #remove the "." at the begining of the extension
            extension = extension[1:]
        except IndexError:
            extension = ""


        try: #remove the "_" at the begining of the extra
            extra = extra[1:]
        except IndexError:
            extra = ""

        return prefix, run, frame, extra, extension

    @staticmethod
    def makeTranslation(pTranslate, pKeyword, pDefaultValue):
        """
        Static method

        ????


        @type pTranslate: list ??
        @param pKeyword: the given keyword to be replaced
        @param pDefaultValue: default value for the keyword
        """
        for keyword, value in pTranslate:
            if keyword == pKeyword:
                newValue = ""
                for i in range(0, len(value)):
                    if value[i] != "\"":
                        newValue += value[i]
                return newValue

        if len(pTranslate) > 0:
            EDUtilsBioSaxs.showMessage(3, "Trying to get value '%s' which doesn't exist!" % pKeyword)

        return pDefaultValue


class HPLCframe(object):
    def __init__(self, runID, frameId=None):
        self.runID = runID
        self.frameId = frameId
        self.curve = None
        self.subtracted = None
        self.processing = True
        self.time = None
        self.gnom = None
        self.Dmax = None
        self.total = None
        self.volume = None
        self.Rg = None
        self.Rg_Stdev = None
        self.I0 = None
        self.I0_Stdev = None
        self.quality = None
        self.sum_I = None
        self.Vc = None
        self.Qr = None
        self.mass = None
        self.Vc_Stdev = None
        self.Qr_Stdev = None
        self.mass_Stdev = None
        self.q = None
        self.I = None
        self.err = None

    def purge_memory(self):
        """
        free the memory associated with the curve
        """
        self.q = None
        self.I = None
        self.err = None


def median_filt(input_array, width=3):
    """
    Simple 1D median filter (with reflect mode)
    """
    b = numpy.zeros(input_array.size + width, dtype=input_array.dtype)
    b[:width // 2] = input_array[width // 2 - 1::-1]
    b[-width + width // 2:] = input_array[-1:-width + width // 2 - 1:-1]
    b[width // 2:-width + width // 2] = input_array
    c = numpy.outer(b, numpy.ones(width, dtype=input_array.dtype))
    c.strides = c.strides[0], c.strides[0]
    d = numpy.median(c, axis= -1)
    return d[:-width]


def label(a):
    "Simple labaling algo for non zero regions"
    last = 0
    cnt = 1
    out = numpy.zeros_like(a)
    for i in range(a.size):
        if a[i] == 0:
            if last != 0:
                cnt += 1
            last = 0
        else:
            out[i] = cnt
            last = cnt
    return out

def datasmoothness(raw, filtered):
    return ((raw - filtered) * (raw - filtered)).mean() * 1.0 / raw.mean() ** 2



class HPLCrun(object):
    def __init__(self, runId, first_curve=None, firstCurveIntensity = None):
        self.id = runId
        self.deleted = False
        self.buffer = None  # filename of the buffer
        self.first_curve = first_curve
        self.frames = {} #key: id, value: HPLCframe instance
        self.curves = []
        self.for_buffer = []
        self.for_buffer_sum_I = None
        self.for_buffer_sum_sigma2 = None
        self.hdf5_filename = None
        self.hdf5 = None
        self.chunk_size = 250
        self.lock = Semaphore()
        if first_curve:
            self.files.append(first_curve)
        if firstCurveIntensity:
            self.firstCurveIntensity = firstCurveIntensity
        else: 
            self.firstCurveIntensity = None
        self.max_size = None
        self.start_time = None
        self.time = None
        self.gnom = None
        self.Dmax = None
        self.total = None
        self.volume = None
        self.Rg = None
        self.Rg_Stdev = None
        self.I0 = None
        self.I0_Stdev = None
        self.quality = None
        self.q = None
        self.size = None
        self.scattering_I = None
        self.scattering_Stdev = None
        self.subtracted_I = None
        self.subtracted_Stdev = None
        self.sum_I = None
        self.Vc = None
        self.Qr = None
        self.mass = None
        self.Vc_Stdev = None
        self.Qr_Stdev = None
        self.mass_Stdev = None  
        self.buffer_frames = None
        self.merge_frames = None  # indexes of first and last frame marged
        self.buffer_I = None
        self.buffer_Stdev = None
        self.merge_I = None 
        self.merge_Stdev = None     
        self.merge_curves = []
        self.merge_Rg = {}
        self.merge_analysis = {}
        self.merge_framesDIC = {}
        self.keys1d = ["gnom","Dmax","total","volume","Rg","Rg_Stdev","I0","I0_Stdev","quality","sum_I","Vc", "Qr","mass","Vc_Stdev","Qr_Stdev","mass_Stdev"]
        self.keys2d = ["scattering_I","scattering_Stdev","subtracted_I","subtracted_Stdev"]
        self.keys_frames = ["buffer_frames", "merge_frames"]
        self.keys_merges = ["buffer_I", "buffer_Stdev", "merge_I", "merge_Stdev"]
        # self.keys_analysis = ["merge_Guinier", "merge_Gnom", "merge_Porod"]

    def reset(self):
        self.deleted = True
        self.buffer = None  # filename of the buffer
        self.first_curve = None
        self.frames = {}  # key: id, value: HPLCframe instance
        self.curves = []
        self.for_buffer = []
        self.start_time = None
        self.time = None
        self.gnom = None
        self.Dmax = None
        self.total = None
        self.volume = None
        self.Rg = None
        self.Rg_Stdev = None
        self.I0 = None
        self.I0_Stdev = None
        self.quality = None
        self.q = None
        self.size = None
        self.scattering_I = None
        self.scattering_Stdev = None
        self.subtracted_I = None
        self.subtracted_Stdev = None
        self.sum_I = None
        self.Vc = None
        self.Qr = None
        self.mass = None
        self.Vc_Stdev = None
        self.Qr_Stdev = None
        self.mass_Stdev = None
        self.buffer_frames = None
        self.merge_frames = None  # indexes of first and last frame merged
        self.buffer_I = None
        self.buffer_Stdev = None
        self.merge_I = None
        self.merge_Stdev = None
        self.merge_curves = []
        self.merge_Rg = {}
        self.merge_analysis = {}
        self.merge_framesDIC = {}

    def dump_json(self, filename=None):

        dico = {}
        dico["id"] = self.id
        dico["buffer"] = self.buffer
        dico["first_curve"] = self.first_curve
        dico["frames"] = {}
        dico["curves"] = self.curves
        dico["for_buffer"] = self.for_buffer
        dico["hdf5_filename"] = self.hdf5_filename
        dico["chunk_size"] = self.chunk_size

        for i in self.frames:
            dico["frames"][i] = self.frames[i].__dict__
        if not filename and self.hdf5_filename:
            filename = os.path.splitext(self.hdf5_filename)[0] + ".json"
        json.dump(dico, open(filename, "w"), indent=1)

    def load_json(self, filename=None):
        if not filename and self.hdf5_filename:
            filename = os.path.splitext(self.hdf5_filename)[0] + ".json"
        dico = json.load(open(filename, "r"))
        for i in dico:
            if i != "frames":
                self.__setattr__(i, dico[i])
        frames = dico["frames"]
        for i in frames:
            frame = HPLCframe(self.id)
            for k, v in frames[i].items():
                frame.__setattr__(k, v)
            self.frames[int(i)] = frame

    def init_hdf5(self, filename):
        if self.hdf5_filename is None:
            with self.lock:
                if self.hdf5_filename is None:
                    self.hdf5_filename = filename

    def calc_size(self, idx):
        return (1 + (idx // self.chunk_size)) * self.chunk_size

    def extract_data(self, force_finished=False):
        self.max_size = self.calc_size(max(self.frames.keys()) + 1)
        self.time = numpy.zeros(self.max_size, dtype=numpy.float64)
       
        if (self.q is None) or (self.size is None): 
            if self.first_curve and os.path.exists(self.first_curve):
                data = numpy.loadtxt(self.first_curve)
                self.q = data[:, 0]
                self.size = self.q.size 
        for key in self.keys2d:
            self.__setattr__(key, numpy.zeros((self.max_size, self.size), dtype=numpy.float32))

        for key in self.keys1d:
            self.__setattr__(key, numpy.zeros(self.max_size, dtype=numpy.float32))

        for i, frame in self.frames.items():
            if not force_finished:
                while frame.processing:
                    time.sleep(1.0)
            for key in ["time"] + self.keys1d:
                self.__getattribute__(key)[i] = frame.__getattribute__(key) or 0.0
            
            if frame.curve and os.path.exists(frame.curve):
                data = numpy.loadtxt(frame.curve)
                self.scattering_I[i, :] = data[:, 1]
                self.scattering_Stdev[i, :] = data[:, 2]
            if frame.subtracted and os.path.exists(frame.subtracted):
                data = numpy.loadtxt(frame.subtracted)
                self.subtracted_I[i, :] = data[:, 1]
                self.subtracted_Stdev[i, :] = data[:, 2]
        t = self.time > 0
        x = numpy.arange(self.max_size)
        self.time = numpy.interp(x, x[t], self.time[t])
        if self.start_time:
            self.time -= self.start_time
        else:
            self.time -= self.time.min()

    def save_hdf5(self):
        if not self.max_size:
            self.extract_data()
        with self.lock:
            if os.path.exists(self.hdf5_filename):
                os.unlink(self.hdf5_filename)
            self.hdf5 = h5py.File(self.hdf5_filename)
            self.hdf5.create_dataset("q", shape=(self.size,), dtype=numpy.float32, data=self.q)
            for key in ["time"] + self.keys1d + self.keys2d:
                self.hdf5[key] = numpy.asarray(self.__getattribute__(key), dtype=numpy.float32)
            self.hdf5.close()
        return self.hdf5_filename

    def make_plot(self):
        if self.time is None:
            self.extract_data()
        data = self.sum_I
        if (self.time is None) or ((data > 0).sum() > self.time.size):
            EDVerbose.WARNING("Error in time scale. discarding time scale")
            valid_pts = numpy.arange(data.size)
            valid_time = valid_pts
            xaxislabel = "Point"
        else:
            valid_time = self.time
            valid_pts = numpy.arange(self.time.size)
            xaxislabel = "time (seconds)"
        if valid_pts.size < 2:
            EDVerbose.WARNING("Too few points to make a curve")
            return

        fig = pylab.plt.figure()
        fig_size = fig.get_size_inches()
        fig.set_size_inches([fig_size[0], 2 * fig_size[1]])

        sp0 = fig.add_subplot(311)  # summed I
        sp1 = fig.add_subplot(312)  # Rg
        sp2 = fig.add_subplot(313)  # I0

        sp0.plot(valid_time, data)  # , label="Total Scattering")
        sp0.set_ylabel("Total Scattering")
        datamin = (data[data > 0]).min()
        datamax = data.max()
        if datamax > datamin:  # avoid division by zero
            sp0.set_ylim(datamin, datamax)
            sp0.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
        sp0.legend()

        sp1.errorbar(valid_time, self.Rg, self.Rg_Stdev, label="Rg")
#         sp1.plot(valid_time, self.gnom[valid_pts], label="Gnom")
#         sp1.plot(valid_time, self.Dmax[valid_pts], label="Dmax")
        sp1.set_ylabel("Radius of gyration (nm)")
        datamax = median_filt((self.Rg + self.Rg_Stdev)[valid_pts], 9).max()
        if datamax > 0:
            sp1.set_ylim(0, datamax)
            sp1.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
        sp1.legend()

        sp2.errorbar(valid_time, self.I0[valid_pts], self.I0_Stdev[valid_pts])  # , label="I0")
        sp2.set_ylabel("I0 from AutoRg")
        sp2.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
        sp2.set_xlabel(xaxislabel)
        sp2.legend()

#
#         sp3 = fig.add_subplot(514)
#         sp3.plot(valid_time, 100.0 * self.quality[valid_pts])  # , label="Quality")
#         sp3.set_ylabel("Qual. %")
#         sp3.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
# #         sp3.legend()
#
#         sp4 = fig.add_subplot(515)
#         sp4.plot(valid_time, self.volume[valid_pts])  # , label="Volume")
#         sp4.set_ylabel("Vol. nm^3")
#         if (valid_time - valid_pts).sum() == 0:
#             sp4.set_xlabel("Point")
#         else:
#             sp4.set_xlabel("time (seconds)")
#         datamax = median_filt(self.volume, 9).max()
#         if datamax > 0:
#             sp4.set_ylim(0, datamax)
#             sp4.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(4))
# #         sp4.legend()
        pngFile = os.path.splitext(self.hdf5_filename)[0] + ".png"
        fig.savefig(pngFile)
        fig.savefig(os.path.splitext(self.hdf5_filename)[0] + ".svg", transparent=True, bbox_inches='tight', pad_inches=0)
        return pngFile

#     def analyse(self):
#         """
#         Look for curves to merge...
#         """
#         lab = label(self.I0)
#         res = []
#         self.merge_frames = []
#         for i in range(1, int(lab.max() + 1)):
#             loc = (lab == i)
#             c = loc.sum()
#             if c > 10:
#                 idx = numpy.where(loc)[0]
#                 start = idx[0]
#                 stop = idx[-1]
#                 maxi = self.I0[start: stop + 1].argmax() + start
#                 rg0 = self.Rg[maxi]
#                 sg0 = self.Rg_Stdev[maxi]
#                 good = (abs(self.Rg - rg0) < sg0) #keep curves with same Rg within +/- 1 stdev
#                 good[:start] = 0
#                 good[stop:] = 0
#                 lg = label(good[start:stop + 1])
#                 lv = lg[maxi - start]
#                 resl = numpy.where(lg == lv)[0] + start
#                 if len(resl) > 1:
#                     res.append(numpy.where(lg == lv)[0] + start)
#                     self.merge_frames.append([resl[0], resl[-1]])

#        return res

    def analyse(self):
        # Note: This algorithm was tested with data acquired at BM29 in late 2012, early 2013
        # Changes in the acquisition protocol might require adaption of parameters

        # paramterers for finding ROIs:
        smoothing_degree = 9

        # parameters for smoothing for peak finding
        nyf = 0.5
        first_butter_par = 4
        second_butter_par = 0.1 / nyf

        # parameters for peak finding algorithm
        window_min_size = 1
        window_max_size_rel = 0.2  # to be multiplied by size of ROI

        Ismooth = medfilt(self.I0, smoothing_degree)
        lab = label(Ismooth)
        Rgsmooth = medfilt(self.Rg, smoothing_degree)
        res = []
        self.merge_frames = []

        for i in range(1, int(lab.max() + 1)):
            loc = (lab == i)
            c = loc.sum()
            # Only analyse peak regions of at leat 10 subsequent frames
            if c > 10:
                idx = numpy.where(loc)[0]
                start = idx[0]
                stop = idx[-1]
                Ishort = self.I0[start:stop]
                I0med = Ismooth[start:stop]

                Rgmed = Rgsmooth[start:stop]
                Rg_Stdshort = self.Rg_Stdev[start:stop]
                Rgshort = self.Rg[start:stop]
                # This is an attempt to remove "dirt" - long broad peaks with no real peeak structure, noise on short timescales
                # Test this with Ishort vs I0med
                if datasmoothness(Ishort, I0med) < 0.25:
    #

                    # we smooth the data with a butterworth filter to remove high-frequency noise


                    b, a = butter(first_butter_par, second_butter_par)
                    #We should take care of the pading length to avoid errors
                    if 3*max(len(a),len(b)) > len(Ishort):
                        fl = filtfilt(b, a, Ishort)
                    else:
                        fl = filtfilt(b, a, Ishort,padlen = Ishort.shape[0]-2)



                    # The parameters for the peak finding
                    window_max_size = mfloor(window_max_size_rel * len(numpy.where(fl)[0]))
                    peaks = find_peaks_cwt(fl, numpy.arange(window_min_size, window_max_size))




                    for i in range(len(peaks)):
                        peak = peaks[i]

                        if peaks[i - 1] < peak:
                            minindex = (peaks[i - 1] + peak) / 2
                        else:
                            minindex = 0

                        if i < len(peaks) - 1:
                            maxindex = (peaks[i + 1] + peak) / 2
                        else:
                            maxindex = stop - start - 1


                        if peak < maxindex and len(I0med[peak:maxindex])>1:                               
                            maxindex = I0med[peak:maxindex].argmin() + peak
                        if minindex < peak  and len(I0med[minindex:peak + 1])>1 :
                            minindex = I0med[minindex:peak + 1].argmin() + minindex
                        maxi = I0med[minindex:maxindex].argmax() + minindex


                        if datasmoothness(Ishort[minindex:maxindex], I0med[minindex:maxindex]) < 0.3:
                            if  I0med[peak] >= I0med[maxindex] and I0med[peak] >= I0med[minindex] and maxindex - minindex > 10:



                                rg0 = Rgmed[maxi]
                                srg0 = Rg_Stdshort[maxi]

                                good = ((abs(Rgmed - rg0) < srg0))
                                good[maxindex] = False

                                if not (len(numpy.where(good[minindex:maxi] == False)[0]) == 0):

                                    regionstart = numpy.where(good[minindex:maxi] == False)[0].max() + minindex
                                else:
                                    regionstart = minindex
                                if not (len(numpy.where(good[maxi:maxindex] == False)[0]) == 0):
                                    regionend = numpy.where(good[maxi:maxindex] == False)[0].min() + maxi
                                else:
                                    regionend = maxindex

                                if regionend - regionstart > 5:
                                    good[:regionstart] = 0
                                    good[regionend:] = 0
                                    lg = label(good)
                                    lv = lg[maxi]
                                    region = numpy.where(lg == lv)[0] + start
                                    res.append(region)

                                    self.merge_frames.append([region[0], region[-1]])
        return res



    def extract_merges(self):
        #if self.buffer_I = None:
        #    self.buffer_I = numpy.zeros(self.size, dtype=numpy.float32)
        #if self.buffer_Stdev = None:    
        #    self.buffer_Stdev = numpy.zeros(self.size, dtype=numpy.float32)
        if self.merge_frames:
            self.merge_I = numpy.zeros((len(self.merge_frames), self.size), dtype=numpy.float32)
            self.merge_Stdev = numpy.zeros((len(self.merge_frames), self.size), dtype=numpy.float32)
        else:
            self.merge_I = numpy.zeros(self.size, dtype=numpy.float32)
            self.merge_Stdev = numpy.zeros(self.size, dtype=numpy.float32)

        self.buffer_frames = [0, len(self.for_buffer)]

        if self.buffer and os.path.exists(self.buffer) and  (self.buffer_I is None):
            self.buffer_I = numpy.zeros(self.size, dtype=numpy.float32)
            self.buffer_Stdev = numpy.zeros(self.size, dtype=numpy.float32)
            data = numpy.loadtxt(self.buffer)
            self.buffer_I = data[:, 1]
            self.buffer_Stdev = data[:, 2]

        if (not self.merge_frames == None) and len(self.merge_frames) > 0:
            for i in range(len(self.merge_frames)):
                group = self.merge_frames[i]
                assert len(group) == 2
                if group[0] == group[1]:  # we have only 1 frame in the group
                    outname = self.frames[group[0]].subtracted
                else:
                    outname = os.path.splitext(self.frames[group[0]].subtracted)[0] + "_aver_%s.dat" % group[-1]
                if os.path.exists(outname):
                    data = numpy.loadtxt(outname)
                    self.merge_I[i, :] = data[:, 1]
                    self.merge_Stdev[i, :] = data[:, 2]
        else:
            self.merge_frames = [0, 0]


    def append_hdf5(self):
        self.extract_merges()
        with self.lock:
            try:
#                 if os.path.exists(self.hdf5_filename):
#                     os.unlink(self.hdf5_filename)
                self.hdf5 = h5py.File(self.hdf5_filename)
                for key in self.keys_frames + self.keys_merges:
                    if not self.__getattribute__(key) == None:
                        self.hdf5[key] = numpy.asarray(self.__getattribute__(key), dtype=numpy.float32)
                self.hdf5.close()
            except:
                print traceback.format_exc()
                
        return self.hdf5_filename


def calcVc(dat, Rg, dRg, I0, dI0, imin):
    """Calculates the Rambo-Tainer invariant Vc, including extrapolation to q=0

    Arguments: 
    @param dat:  data in q,I,dI format, cropped to maximal q that should be used for calculation (normally 2 nm-1)
    @param Rg,dRg,I0,dI0:  results from Guinier approximation/autorg
    @param imin:  minimal index of the Guinier range, below that index data will be extrapolated by the Guinier approximation
    @returns: Vc and an error estimate based on non-correlated error propagation
    """
    dq = dat[1, 0] - dat[0, 0]
    qmin = dat[imin, 0]
    qlow = numpy.arange(0, qmin, dq)

    lowqint = scint.trapz((qlow * I0 * numpy.exp(-(qlow * qlow * Rg * Rg) / 3.0)), qlow)
    dlowqint = scint.trapz(qlow * numpy.sqrt((numpy.exp(-(qlow * qlow * Rg * Rg) / 3.0) * dI0) ** 2 + ((I0 * 2.0 * (qlow * qlow) * Rg / 3.0) * numpy.exp(-(qlow * qlow * Rg * Rg) / 3.0) * dRg) ** 2), qlow)
    vabs = scint.trapz(dat[imin:, 0] * dat[imin:, 1], dat[imin:, 0])
    dvabs = scint.trapz(dat[imin:, 0] * dat[imin:, 2], dat[imin:, 0])
    vc = I0 / (lowqint + vabs)
    dvc = (dI0 / I0 + (dlowqint + dvabs) / (lowqint + vabs)) * vc
    return (vc, dvc)


def RamboTainerInvariant(dat, Rg, dRg, I0, dI0, imin, qmax=2):
    """calculates the invariants Vc and Qr from the Rambo&Tainer 2013 Paper,
    also the the mass estimate based on Qr for proteins

    Arguments: 
    @param dat: data in q,I,dI format, q in nm-1
    @param Rg,dRg,I0,dI0: results from Guinier approximation
    @param imin: minimal index of the Guinier range, below that index data will be extrapolated by the Guinier approximation
    @param qmax: maximum q-value for the calculation in nm-1
    @return: dict with Vc, Qr and mass plus errors
    """
    scale_prot = 1.0 / 0.1231
    power_prot = 1.0

    imax = abs(dat[:, 0] - qmax).argmin()
    if (imax <= imin) or (imin < 0):  # unlikely but can happened
        return {}
    vc = calcVc(dat[:imax, :], Rg, dRg, I0, dI0, imin)

    qr = vc[0] ** 2 / (Rg)
    mass = scale_prot * qr ** power_prot

    dqr = qr * (dRg / Rg + 2 * ((vc[1]) / (vc[0])))
    dmass = mass * dqr / qr

    return {'Vc': vc[0], 'dVc': vc[1], 'Qr': qr, 'dQr': dqr, 'mass': mass, 'dmass': dmass}


### Rg implementation stolen from BioXTas RAW###
#Define the rg fit function
#Fitting settings
#errorWeight          =  [True, wx.NewId(), 'bool']
                            



def linear_func(x, a, b):
    return a+b*x

# def calcRg(q, i, err, transform=True, error_weight = True):
#      
#     
#     if transform:
#         #Start out by transforming as usual.
#         x = q*q
#         y = np.log(i)
#         yerr = err*np.absolute(err/i)
#     else:
#         x = q
#         y = i
#         yerr = err
#  
#     try:
#         if error_weight:
#             opt, cov = curve_fit(linear_func, x, y, sigma=yerr, absolute_sigma=True)
#             #print "opt", opt
#         else:
#             opt, cov = curve_fit(linear_func, x, y)
#             print "scipy", opt
#         suc_fit = True
#     except TypeError:
#         opt = []
#         cov = []
#         suc_fit = False
#  
#     if suc_fit and opt[1] < 0 and np.isreal(opt[1]) and np.isreal(opt[0]):
#         RG=np.sqrt(-3.*opt[1])
#         I0=np.exp(opt[0])
#  
#         #error in rg and i0 is calculated by noting that q(x)+/-Dq has Dq=abs(dq/dx)Dx, where q(x) is your function you're using
#         #on the quantity x+/-Dx, with Dq and Dx as the uncertainties and dq/dx the derviative of q with respect to x.
#         RGer=np.absolute(0.5*(np.sqrt(-3./opt[1])))*np.sqrt(np.absolute(cov[1,1,]))
#         I0er=I0*np.sqrt(np.absolute(cov[0,0]))
#  
#     else:
#         RG = -1
#         I0 = -1
#         RGer = -1
#         I0er = -1
#  
#     return RG, I0, RGer, I0er, opt, cov



class InsufficientDataError(Error):
    """Exception raised for errors in the input.

    Attributes:
        expression -- input expression in which the error occurred
        message -- explanation of the error
    """

    def __init__(self):
        self.expression = ""
        self.message = "Not enough data do determine Rg"
        
        


def weightedlinFit(x,y,yerr):
    datax = x
    datay = y
    weight = 1/(yerr*yerr)
    n = datax.shape[0]
    sigma = weight.sum()
    sigmay = (datay*weight).sum()
    sigmax = (datax*weight).sum()
    sigmaxy = (datax*datay*weight).sum()
    sigmaxx = (datax*datax*weight).sum()
    
    detA = sigmax*sigmax-sigma*sigmaxx
    if not(detA==0):
        x = [-sigmaxx*sigmay + sigmax*sigmaxy,-sigmax*sigmay+sigma*sigmaxy]/detA
        xmean = datax.mean()
        ymean = datay.mean()
        ssxx = (datax**2).sum() -n*xmean**2
        ssyy = (datay**2).sum() -n*ymean**2
        ssxy = (datay*datax).sum() -n*ymean*xmean
        s = ((ssyy + x[0]*ssxy)/(n-2))**0.5
        da = s*(1/n + (xmean**2)/ssxx)**0.5
        db = s/ssxx**0.5
        a = x[0]
        b = x[1]
        xopt = (a,b)
        dx = (da,db)
        return xopt, dx

def calcRg(x,y,yerr):
    xopt, dx= weightedlinFit(x,y,yerr)
    #print xopt, dx
    RG=np.sqrt(3.*xopt[1])
    I0=np.exp(xopt[0])
     
    #error in rg and i0 is calculated by noting that q(x)+/-Dq has Dq=abs(dq/dx)Dx, where q(x) is your function you're using
    #on the quantity x+/-Dx, with Dq and Dx as the uncertainties and dq/dx the derviative of q with respect to x.
    RGer=np.sqrt(3./dx[1])
    I0er=I0*dx[0]
    return RG, I0, RGer, I0er, xopt

def autoRg(sasm):
    #This function automatically calculates the radius of gyration and scattering intensity at zero angle
    #from a given scattering profile. It roughly follows the method used by the autorg function in the atsas package

    q = sasm[:,0]
    i = sasm[:,1]
    err = sasm[:,2]
    #qmin  qmax = sasm.getQrange()
    
    
    q = q[np.where(np.isnan(i) == False)]
    err = err[np.where(np.isnan(i) == False)]
    i = i[np.where(np.isnan(i) == False)]

    q = q[np.where(np.isinf(i) == False)]
    err = err[np.where(np.isinf(i) == False)] 
    i = i[np.where(np.isinf(i) == False)]
    
    q = q[np.where(i > 0)]
    err = err[np.where(i > 0)] 
    i = i[np.where(i > 0)]
    


    qmin = 3
    qmax = -1

  

    #Pick the start of the RG fitting range. Note that in autorg, this is done
    #by looking for strong deviations at low q from aggregation or structure factor
    #or instrumental scattering, and ignoring those. This function isn't that advanced
    #so we start at 0.
    data_start = max(qmin,np.argmax(i > 0))
    #print "data_start", data_start
    q = q[data_start:-1]
    i = i[data_start:-1]
    err = err[data_start:-1]
    #Following the atsas package, the end point of our search space is the q value
    #where the intensity has droped by an order of magnitude from the initial value.
    #data_end = np.abs(i-i[data_start]/10).argmin()
    data_end = np.argmax(i < i[0]/10)
    #print "used data ", data_start, data_end + data_start
    if (data_end ) < 10:
        raise InsufficientDataError()
  
    #This makes sure we're not getting some weird fluke at the end of the scattering profile.
    if data_end > len(q)/2.:
        found = False
        idx = 0
        while not found:
            idx = idx +1
            if i[idx]<i[data_start]/10:
                found = True
            elif idx == len(q) -1:
                found = True
        data_end = idx
    q = q[0:data_end]
    i = i[0:data_end]
    err = err[0:data_end]

    #Start out by transforming as usual.
    qs = q*q
    il = np.log(i)
    iler = np.absolute(err/i)
    
#     qs = qs[np.where(np.isnan(il) == False)]
# #    iler = iler[np.where(np.isnan(il) == False)] 
#     il = il[np.where(np.isnan(il) == False)]


    #Pick a minimum fitting window size. 10 is consistent with atsas autorg.
    min_window = 10

    max_window = data_end-data_start

    fit_list = []

    #It is very time consuming to search every possible window size and every possible starting point.
    #Here we define a subset to search.
    tot_points = max_window
    window_step = tot_points/10
    data_step = tot_points/50

    if window_step == 0:
        window_step =1
    if data_step ==0:
        data_step =1

    window_list = range(min_window,max_window, window_step)
    window_list.append(max_window)


    #This function takes every window size in the window list, stepts it through the data range, and
    #fits it to get the RG and I0. If basic conditions are met, qmin*RG<1 and qmax*RG<1.35, and RG>0.1,
    #We keep the fit.
    for w in window_list:
        for start in range(data_start,data_end-w, data_step):
            x = qs[start:start+w]
            y = il[start:start+w]
            yerr = iler[start:start+w]

            #Remove NaN and Inf values:
            x = x[np.where(np.isnan(y) == False)]
            yerr = yerr[np.where(np.isnan(y) == False)]
            y = y[np.where(np.isnan(y) == False)]

            x = x[np.where(np.isinf(y) == False)]
            yerr = yerr[np.where(np.isinf(y) == False)]
            y = y[np.where(np.isinf(y) == False)]

            try:
                RG, I0, RGer, I0er,opt = calcRg(x, y, yerr)#, transform=False, error_weight =False)
            except ValueError as VE:
                print VE
                raise 
            except Exception as err:
                print "An error occured. y = ", y, "yerr = ", yerr, "x = ", x
                raise 
 
            if RG>0.01 and q[start]*RG<1 and q[start+w-1]*RG<1.35 and RGer/RG <= 1:
  
                a = opt[0]
                b = -opt[1]
              
  
                r_sqr = 1 - np.square(il[start:start+w]-linear_func(qs[start:start+w], a, b)).sum()/np.square(il[start:start+w]-il[start:start+w].mean()).sum()
                #print "R", r_sqr
                if r_sqr > .15:
                    chi_sqr = np.square((il[start:start+w]-linear_func(qs[start:start+w], a, b))/iler[start:start+w]).sum()
  
                    #All of my reduced chi_squared values are too small, so I suspect something isn't right with that.
                    #Values less than one tend to indicate either a wrong degree of freedom, or a serious overestimate
                    #of the error bars for the system.
                    dof = w - 2.
                    reduced_chi_sqr = chi_sqr/dof
  
                    fit_list.append([start, w, q[start], q[start+w-1], RG, RGer, I0, I0er, q[start]*RG, q[start+w-1]*RG, r_sqr, chi_sqr, reduced_chi_sqr])
                 
    #Extreme cases: may need to relax the parameters.
    if len(fit_list)<1:
        #Stuff goes here
        pass

    if len(fit_list)>0:
        fit_list = np.array(fit_list)

        #Now we evaluate the quality of the fits based both on fitting data and on other criteria.

        #Choice of weights is pretty arbitrary. This set seems to yield results similar to the atsas autorg
        #for the few things I've tested.
        qmaxrg_weight = 1
        qminrg_weight = 1
        rg_frac_err_weight = 1
        i0_frac_err_weight = 1
        r_sqr_weight = 4
        reduced_chi_sqr_weight = 0
        window_size_weight = 4

        weights = np.array([qmaxrg_weight, qminrg_weight, rg_frac_err_weight, i0_frac_err_weight, r_sqr_weight,
                            reduced_chi_sqr_weight, window_size_weight])

        quality = np.zeros(len(fit_list))

        max_window_real = float(window_list[-1])

        all_scores = []

        #This iterates through all the fits, and calculates a score. The score is out of 1, 1 being the best, 0 being the worst.
        for a in range(len(fit_list)):
            #Scores all should be 1 based. Reduced chi_square score is not, hence it not being weighted.

            qmaxrg_score = 1-np.absolute((fit_list[a,9]-1.3)/1.3)
            qminrg_score = 1-fit_list[a,8]
            rg_frac_err_score = 1-fit_list[a,5]/fit_list[a,4]
            i0_frac_err_score = 1 - fit_list[a,7]/fit_list[a,6]
            r_sqr_score = fit_list[a,10]
            reduced_chi_sqr_score = 1/fit_list[a,12] #Not right
            window_size_score = fit_list[a,1]/max_window_real

            scores = np.array([qmaxrg_score, qminrg_score, rg_frac_err_score, i0_frac_err_score, r_sqr_score,
                               reduced_chi_sqr_score, window_size_score])

            # print scores

            total_score = (weights*scores).sum()/weights.sum()

            quality[a] = total_score

            all_scores.append(scores)


        #I have picked an aribtrary threshold here. Not sure if 0.6 is a good quality cutoff or not.
        if quality.max() > 0.6:
            # idx = quality.argmax()
            # rg = fit_list[idx,4]
            # rger1 = fit_list[idx,5]
            # i0 = fit_list[idx,6]
            # i0er = fit_list[idx,7]
            # idx_min = fit_list[idx,0]
            # idx_max = fit_list[idx,0]+fit_list[idx,1]

            # try:
            #     #This adds in uncertainty based on the standard deviation of values with high quality scores
            #     #again, the range of the quality score is fairly aribtrary. It should be refined against real
            #     #data at some point.
            #     rger2 = fit_list[:,4][quality>quality[idx]-.1].std()
            #     rger = rger1 + rger2
            # except:
            #     rger = rger1
            try:
                idx = quality.argmax()
                rg = fit_list[:,4][quality>quality[idx]-.1].mean()
                rger = fit_list[:,5][quality>quality[idx]-.1].std()
                i0 = fit_list[:,6][quality>quality[idx]-.1].mean()
                i0er = fit_list[:,7][quality>quality[idx]-.1].std()
                idx_min = int(fit_list[idx,0])
                idx_max = int(fit_list[idx,0]+fit_list[idx,1]-1)
                #idx_min_corr = np.argmin(np.absolute(sasm[:,0] - fit_list[idx,3]))
                #idx_max_corr = np.argmin(np.absolute(sasm[:,0] - fit_list[idx,4]))
            except:
                idx = quality.argmax()
                rg = fit_list[idx,4]
                rger = fit_list[idx,5]
                i0 = fit_list[idx,6]
                i0er = fit_list[idx,7]
                idx_min = int(fit_list[idx,0])
                idx_max = int(fit_list[idx,0]+fit_list[idx,1]-1)


        else:
            print "F1"
            rg = -1
            rger = -1
            i0 = -1
            i0er = -1
            idx_min = -1
            idx_max = -1

    else:
        print "F2"
        rg = -1
        rger = -1
        i0 = -1
        i0er = -1
        idx_min = -1
        idx_max = -1
        quality = []
        all_scores = []

    idx_min = idx_min + data_start
    idx_max = idx_max + data_start

    #We could add another function here, if not good quality fits are found, either reiterate through the
    #the data and refit with looser criteria, or accept lower scores, possibly with larger error bars.

    #returns Rg, Rg error, I0, I0 error, the index of the first q point of the fit and the index of the last q point of the fit
    return rg, rger, i0, i0er, idx_min, idx_max





