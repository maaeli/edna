#!/usr/bin/env python
#coding: utf8
#
#    Project: Full Field XRay Absorption Spectroscopy
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) 2012, ESRF, Grenoble
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
__author__ = "Jérôme Kieffer"
__license__ = "GPLv3+"
__copyright__ = "2012, ESRF, Grenoble"
__contact__ = "jerome.kieffer@esrf.eu"
__date__ = "20120529"
__doc__ = """
Merge and Crop HDF5 stacks of FullField Xanes/Exafs data 
"""

import sys, logging, os, time
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("hdf5merge")
import numpy
import h5py

class MergeFFX(object):
    """
    Merge FullField Xanes/Exafs dataset     
    """
    OFFSETS = "Offsets"
    MAX_OFFSET = "MaxOffset"
    STACK = "data"
    ENERGY = "energy"
    MAX_INT = "maxInt"
    NX_DATA = "NXdata"
    START_TIME = "start_time"
    END_TIME = "end_time"
    DURATION = "duration"
    PROGRAM = "program"
    REF_FRAME = "reference_frame"
    TITLE = "Merged FullField XANES mapping"

    def __init__(self, inputs, output, crop=False, check=False, normalize=False, logarithm=False, crop_region=None):
        """
        inputs and output are /path/to/file:internal
        """
        self._h5files = []
        self.start_time = None
        self.end_time = None
        self.inputs = self.validateInputs(inputs) #list of HDF5 groups
        if output is None:
            raise RuntimeError("Output cannot be None")
        self.output = output
        self.crop = bool(crop)
        self.check = bool(check)
        self.normalize = bool(normalize)
        self.h5file = None
        self.h5grp = None
        self.offsets_security = None
        self.offsets = {}
        self._shape = None
        self.ln = logarithm
        
        if crop_region:
            self.get_offsets()
            if self.offsets_security is None:
                self.offsets_security = 0
            dim1,dim2=crop_region.split(",",1)
            start1, stop1 = dim1.split(":", 1)
            start2, stop2 = dim2.split(":", 1)
            if not start1: start1 = "0"
            if not start2: start2 = "0"
            start1 = int(start1) + self.offsets_security
            stop1 = int(stop1) + self.offsets_security
            start2 = int(start2) + self.offsets_security
            stop2 = int(stop2) + self.offsets_security
            self._crop_region = (slice(start1, stop1), slice(start2, stop2))
            self.dim1 = stop1 - start1
            self.dim2 = stop2 - start2
        else:
            self._crop_region = None
            self.dim1 = None
            self.dim2 = None


    def validateInputs(self, inputs):
        """
        @return: dict with "path:h5" -> Group object 
        """
        res = {}
        for h in inputs:
            if ":" not in h:
                logger.error("Input %s does not look like a HDF5 path: /path/to/file.h5:Aligned" % h)
            else:
                filepath, h5path = h.split(":", 1)
                if os.path.isfile(filepath):
                    h5file = h5py.File(filepath, "r")

#                    cls.set_cache(h5file, policy=0.0)
                    if h5path in h5file:
                        if h5file[h5path].__class__.__name__ == "Group":
                            grp = h5file[h5path]
                        else:
                            grp = h5file[h5path].parent
                        res[h] = grp
                        if self.STACK in grp:
                            ds = grp[self.STACK]
                            logger.debug("hfd5: %s\tdataset: %s\t shape: %s" % (filepath, ds.name, ds.shape))
                        if self.START_TIME in grp:
                            start_time = self.parseIsoTime(str(grp[self.START_TIME][()]))
                            if self.start_time is None:
                                self.start_time = start_time
                            elif  self.start_time > start_time:
                                self.start_time = start_time
                        if self.END_TIME in grp:
                            end_time = self.parseIsoTime(str(grp[self.END_TIME][()]))
                            if self.end_time is None:
                                self.end_time = end_time
                            elif  self.end_time < end_time:
                                self.end_time = end_time
                        self._h5files.append(h5file)
                        logger.debug("%s start: %s stop: %s" % (h5path, self.start_time, self.end_time))
                else:
                    logger.warning("No such group %s in file: %s" % (h5path, filepath))
        return res

    
    def open_hdf5(self, filename, size=None, policy=None):
        """
        Create an HDF5 file with extra option to optimize cache writing
        """
        #ensure the file exists
        if not os.path.isfile(filename):
            h5py.File(filename).close()

        propfaid = h5py.h5p.create(h5py.h5p.FILE_ACCESS)
        cache_settings = list(propfaid.get_cache())
        if not size:
            cache_settings[2] = int(10 * cache_settings[2])
        else:
            cache_settings[2] = int(size)
        if policy is not None:
            cache_settings[3] = float(policy)
        propfaid.set_cache(*cache_settings)
        fid = h5py.h5f.open(filename, fapl=propfaid)
        self.h5file = h5py.File(fid)



    def create_output(self):
        if ":" not in self.output:
            logger.error("Input %s does not look like a HDF5 path: /path/to/file.h5:Aligned" % self.output)
        else:
            filepath, h5path = self.output.split(":", 1)
            self.open_hdf5(filepath, size=100e6, policy=0.0)
            if h5path in self.h5file:
                self.h5grp = self.h5file[h5path]
            else:
                self.h5grp = self.h5file.create_group(h5path)
            self.h5grp.attrs["NX_class"] = "NXentry"
            self.h5grp.attrs["creator"] = os.path.basename(__file__)
            self.h5grp.attrs["index"] = "1"
            if "title" not in  self.h5grp:
                self.h5grp.create_dataset("title", data=self.TITLE)
            if not "program" in  self.h5grp:
                self.h5grp.create_dataset("program", data=os.path.basename(__file__))
            if not self.START_TIME in  self.h5grp:
                self.h5grp.create_dataset(self.START_TIME, data=self.getIsoTime(self.start_time))
            ########################################################################
            # Huge hack: for scalar modification: use [()] to refer to the data !!!
            ########################################################################
            if self.END_TIME in self.h5grp:
                self.h5grp[self.END_TIME][()] = self.getIsoTime(self.end_time)
            else:
                self.h5grp.create_dataset(self.END_TIME, data=self.getIsoTime(self.end_time))
            if self.end_time and self.start_time:
                duration = self.end_time - self.start_time
                if self.DURATION in  self.h5grp:
                    self.h5grp[self.DURATION][()] = self.end_time - self.start_time
                else:
                    self.h5grp.create_dataset(self.DURATION, data=duration, dtype="float")

            if self.ENERGY in self.h5grp:
                ds_nrj = self.h5grp[self.ENERGY]
            else:
                nrj = self.get_energy()
                ds_nrj = self.h5grp.create_dataset(self.ENERGY, (nrj.size,), dtype="float32", data=nrj)
                ds_nrj.attrs["interpretation"] = "scalar"
                ds_nrj.attrs["unit"] = "keV"
                ds_nrj.attrs["long_name"] = "Energy of the monochromated beam"
                ds_nrj.attrs["axis"] = "1"

            if self.STACK in self.h5grp:
                ds = self.h5grp[self.STACK]
            else:
                ds = self.h5grp.create_dataset(self.STACK, (self.shape[0], self.dim1, self.dim2),
                                       dtype="float32", chunks=(1, max(1, self.dim1 // 8), max(1, self.dim2 // 8)))
                ds.attrs["interpretation"] = "image" # "spectrum", "scalar", "image" or "vertex"
                ds.attrs["signal"] = "1"
                ds.attrs["axes"] = "energy"
                ds.attrs["creator"] = os.path.basename(__file__)
                ds.attrs["long_name"] = self.TITLE
            if self.NX_DATA not in  self.h5grp:
                nxdata = self.h5grp.create_group(self.NX_DATA)
                nxdata.attrs["NX_class"] = "NXdata"
                nxdata[self.ENERGY] = ds_nrj
                nxdata[self.STACK] = ds


    def get_offsets(self):
        """
        calculate the offet for every datasets
        """
        if not self.offsets:
            for path, h5grp in self.inputs.items():
                if self.OFFSETS in h5grp:
                    offsets = h5grp[self.OFFSETS]
                    if (self.MAX_OFFSET in offsets.attrs):
                        my_offset = offsets.attrs[self.MAX_OFFSET]
                        logger.debug("%s offset %s" % (path, my_offset))
                        self.offsets_security = my_offset
                    npa = offsets[:]
                    self.offsets[path] = npa
                    logger.debug("%s: min offset= %s max offset= %s" % (path, npa.min(axis=0), npa.max(axis=0)))

    def get_crop_region(self):
        if not self._crop_region:
            if self.crop:
                self.get_offsets()
                shape = numpy.array(self.shape[1:])
                secu = self.offsets_security
                start = numpy.ceil(numpy.array([npa.max(axis=0) for npa in self.offsets.values()]).max(axis=0) + secu).astype(int)
                stop = numpy.floor(numpy.array([npa.min(axis=0) for npa in self.offsets.values()]).min(axis=0) - secu + shape).astype(int)
                #handle the cas of offsets larger than secu
                start = numpy.maximum(start, 0)
                stop = numpy.minimum(stop, shape - secu)
                self._crop_region = (slice(start[0], stop[0]), slice(start[1], stop[1]))
                logger.debug("Crop region: %s, %s" % (start, stop))
                self.dim1 = stop[0] - start[0]
                self.dim2 = stop[1] - start[1]
            else:
                self._crop_region = tuple([slice(i) for i in numpy.array(self.shape[1:])])
                self.dim1, self.dim2 = self.shape[1:]
        return self._crop_region
    crop_region = property(get_crop_region)


    def get_shape(self):
        if self._shape is None :
            for path, h5grp in self.inputs.items():
                if self.STACK in h5grp:
                    self._shape = h5grp[self.STACK].shape
                    break
                else:
                     logger.warning("No dataset %s in %s" % (self.STACK, path))
        return self._shape
    shape = property(get_shape)

    def get_energy(self):
        for path, h5grp in self.inputs.items():
            if self.ENERGY in h5grp:
                return  h5grp[self.ENERGY][:]
            else:
                 logger.warning("No dataset %s in %s" % (self.ENERGY, path))


    def merge_dataset(self):
        print self.crop_region
        print('Crop region: [%s:%s, %s:%s] ' % (self.crop_region[0].start, self.crop_region[0].stop,
                                               self.crop_region[1].start, self.crop_region[1].stop))
        ds = self.h5grp[self.STACK]
        logger.debug("Output dataset shape: (%i,%i,%i)" % ds.shape)
        sys.stdout.write("Averaging out frame ")
        readt = []
        writet = []
        for frn in xrange(self.shape[0]):
            sys.stdout.write("%04i" % frn)
            fr = numpy.zeros((self.dim1, self.dim2), "float64")
            i = 0
            tr0 = time.time()
            for path, h5grp in self.inputs.items():
                if self.normalize and (self.MAX_INT in h5grp):
                    norm_factor = h5grp[self.MAX_INT][frn]
                else:
                    norm_factor = 1.0
                if self.STACK in h5grp:
                    idx = (frn,) + self.crop_region
                    cropped = numpy.array(h5grp[self.STACK][idx])
                    if abs(cropped).max() < 1e-10:
                        continue
                    i += 1
                    logger.debug("%s frame shape: %s new_ %s target %s" % (path, idx, cropped.shape, fr.shape))
                    fr += cropped / norm_factor
                else:
                    logger.warning("no %s in %s ?????"(self.STACK, frn))
            tr = time.time() - tr0
            sys.stdout.write("  r=%5.3fs" % tr)
            readt.append(tr)
            if i == 0:
                logger.warning("Why is i=0?????")
                i = 1
            tw0 = time.time()
            if self.ln:
                ds[frn] = -numpy.log(fr / i)
            else:
                ds[frn] = fr / i
            tw = time.time() - tw0
            sys.stdout.write("  w=%5.3fs" % tw)
            writet.append(tw)
            sys.stdout.flush()
            sys.stdout.write("\b"*24)

        print("%sFinished !!!" % os.linesep)
        return readt, writet

    @classmethod
    def getIsoTime(cls, forceTime=None):
        """
        @param forceTime: enforce a given time (current by default)
        @type forceTime: float
        @return: the current time as an ISO8601 string
        @rtype: string  
        """
        if forceTime is None:
            forceTime = time.time()
        localtime = time.localtime(forceTime)
        gmtime = time.gmtime(forceTime)
        tz_h = localtime.tm_hour - gmtime.tm_hour
        tz_m = localtime.tm_min - gmtime.tm_min
        return "%s%+03i:%02i" % (time.strftime("%Y-%m-%dT%H:%M:%S", localtime), tz_h, tz_m)

    @classmethod
    def parseIsoTime(cls, strtime):
        """
        @param strtime: iso representation of time
        @type strtime: string
        @return: seconds since Epoch
        @rtype: float  
        """
        local_time = strtime[:19]
        tz = strtime[19:]
        gm_time = time.mktime(time.strptime(local_time, "%Y-%m-%dT%H:%M:%S")) #+ time.mktime(time.strptime(tz, "%H:%M"))
        return gm_time


if __name__ == "__main__":
    from optparse import OptionParser
    parser = OptionParser()
    parser.add_option("-o", "--output", dest="h5path",
                      help="write result to HDF5 file with given path: path/to/file.h5:Aligned")
    parser.add_option("-a", "--autocrop", dest="autocrop",
                      help="Shall we crop the dataset to valid area", default=False, action="store_true")
    parser.add_option("-c", "--crop", dest="extracrop",
                      help="Extra crop: force croped region: example -C 5:35,6:46 keeps an rectangle width 40 and height 30 (Y,X) ", default=None)
    parser.add_option("-k", "--check", dest="recheck",
                      help="Shall we recheck the consistency of the various frames ... very time consuming !!! (not implemented)", default=False)
    parser.add_option("-n", "--normalize", dest="normalize",
                      help="renormalize frames from intensity", default=True, action="store_true")
    parser.add_option("-N", "--no-normalize", dest="normalize",
                      help="Do NOT renormalize frames from intensity", default=True, action="store_false")
    parser.add_option("-q", "--quiet",
                      action="store_false", dest="verbose", default=True,
                      help="don't print status messages to stdout")
    parser.add_option("-l", "--ln",
                      dest="ln", default=False, action="store_true",
                      help="write data as -logarithm of merged input")
    parser.add_option("-d", "--debug",
                      dest="debug", default=False, action="store_true",
                      help="switch to debug mode with more information printed out")

    (options, args) = parser.parse_args()
    print("")
    print("Options:")
    print('========')
    for k, v in options.__dict__.items():
        print("    %s: %s" % (k, v))
    print("")
    print("Input files and HDF5 path:")
    print("==========================")
    for f in list(args):
        print("    %s" % f)
    print(" ")
    if options.debug:
        logger.setLevel(level=logging.DEBUG)
    mfx = MergeFFX(args, options.h5path, crop=options.autocrop, check=options.recheck, normalize=options.normalize, logarithm=options.ln, crop_region=options.extracrop)
    mfx.get_crop_region()
    mfx.create_output()
#    mfx.get_offsets()
#    mfx.get_crop_region()
    r, w = mfx.merge_dataset()
    from pylab import *
    plot(r, 'b', label="read time")
    plot(w, 'r', label="write time")
    xlabel("Frame number")
    ylabel("elapsed time (s)")
    title("HDF5 FullField Xanes dataset merge profile")
    legend()
    show()
