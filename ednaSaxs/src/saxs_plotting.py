#!/usr/bin/python
# coding: utf8
#
#    Project: Edna Saxs
#             http://www.edna-site.org
#
#    File: "$Id$"
#
#    Copyright (C) 2012 ESRF
#
#    Principal author: Jérôme Kieffer
#
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

__authors__ = ["Jérôme Kieffer"]
__license__ = "GPLv3+"
__copyright__ = "ESRF"
__date__ = "20130124"
__status__ = "Development"
__version__ = "0.1"
import os, sys, time
from optparse import OptionParser
import numpy
from scipy import stats
import matplotlib
# matplotlib.use('Agg')
import matplotlib.pyplot as plt

def load_saxs(filename):
    """
    return q, I, stderr
    """
    data = None
    for i in range(10):  # skip up to 10 comments lines
        try:
            data = numpy.loadtxt(filename, skiprows=i)
        except Exception:
            pass
        else:
            break
    if data == None:
        raise RuntimeError("Unable to read input file")
    if data.ndim == 2 and data.shape[1] == 2:
        q = data[:, 0]
        I = data[:, 1]
        std = None
    elif  data.ndim == 2 and data.shape[1] == 3:
        q = data[:, 0]
        I = data[:, 1]
        std = data[:, 2]
    else:
        raise RuntimeError("Unable to find columns in data file")
    return q, I, std


def guinierPlot(curve_file, first_point=None, last_point=None, filename=None, format="png", unit="nm"):
    """
    Generate a Guinier plot Ln(I) vs q**2
    @param curve_file: name of the saxs curve file
    @param: first_point,last point: integers, by default 0 and -1
    @param  filename: name of the file where the cuve should be saved
    @param format: image format
    @return: the matplotlib figure  
    """
    data = numpy.loadtxt(curve_file)
    q = data[:, 0]
    I = data[:, 1]
    if (first_point is None) and (last_point is None):
        for line in open(curve_file):
            if "# AutoRg: Points" in line:
                d = [int(i) for i in line.split() if i.isdigit()]
                if len(d) >= 2:
                    first_point = d[0]
                    last_point = d[1] + 1
    if first_point is None:
        first_point = 0
    if last_point is None:
        last_point = -1

    q2 = q * q
    logI = numpy.log(I)

    slope, intercept, r_value, p_value, std_err = stats.linregress(q2[first_point:last_point], logI[first_point:last_point])
    Rg = numpy.sqrt(-3 * slope)
    I0 = numpy.exp(intercept)
    end = min(q.size, (-1.5 / slope > q).sum())
    q = q[:end]
    I = I[:end]
    q2 = q2[:end]
    logI = logI[:end]


    fig1 = plt.figure(figsize=(6, 5))
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.plot(q2, logI, label="Experimental curve")
    ax1.plot(q2[first_point:last_point], logI[first_point:last_point], marker='D', markersize=5, label="Guinier region")
    ax1.annotate("qRg$_{min}$=%.1f" % (Rg * q[first_point]), (q2[first_point], logI[first_point]), xytext=None, xycoords='data',
         textcoords='data')
    ax1.annotate("qRg$_{max}$=%.1f" % (Rg * q[last_point]), (q2[last_point], logI[last_point]), xytext=None, xycoords='data',
         textcoords='data')

    ax1.plot(q2, intercept + slope * q2, label="ln[$I(q)$] = %.2f %.2f * $q^2$" % (intercept, slope))
    ax1.set_ylabel('ln[$I(q)$]')
    ax1.set_xlabel('$q^2$ (%s$^{-2}$)' % unit)
    ax1.set_title("Guinier plot: $Rg=$%.1f %s $I0=$%.1f" % (Rg, unit, I0))
    ax1.legend(loc=3)
    if filename:
        if format:
            fig1.savefig(filename, format=format)
        else:
            fig1.savefig(filename)
    return fig1

def kartkyPlot(curve_file, filename=None, format="png", unit="nm"):
    """
    Generate a Kratky: q2I(q) vs q 
    @param curve_file: name of the saxs curve file
    @param: first_point,last point: integers, by default 0 and -1
    @param  filename: name of the file where the cuve should be saved
    @param format: image format
    @return: the matplotlib figure  
    """
    data = numpy.loadtxt(curve_file)
    q = data[:, 0]
    I = data[:, 1]
    q2I = q * q * I
    fig1 = plt.figure(figsize=(6, 5))
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.plot(q, q2I, label="Experimental curve")
    ax1.set_ylabel('$q^2I (%s^2)$' % unit)
    ax1.set_xlabel('$q$ (%s)' % unit)
    ax1.set_title("Kratky plot")
    ax1.legend(loc=0)
    if filename:
        if format:
            fig1.savefig(filename, format=format)
        else:
            fig1.savefig(filename)
    return fig1

def autoRg(q=None, I=None, std=None, datfile=None, mininterval=10, qminRg=1.0, qmaxRg=1.3):
    def fn(a):
        if numpy.isfinite(a['stderr']):
            return  a['stderr']  # / numpy.sqrt(a["len"])
        else:
            return sys.maxint
    def cmp(a, b):
        if fn(a) < fn(b):
            return 1
        elif fn(a) > fn(b):
            return -1
        else:
            return 0

    if (q is None) or (I is None) and datfile:
        q, I, std = load_saxs(datfile)
    out = {}
    start_search = I.argmax()
    Imax = I[start_search]
    keep = (I > Imax / 10)
    keep[:start_search] = 0
    len_search = keep.sum()
    q2 = q * q
    logI = numpy.log(I)
    allres = []
    res = []
    t0 = time.time()
    for s in range(start_search, start_search + len_search - mininterval):
        for e in range(s + mininterval, start_search + len_search):
            slope, intercept, r, tt, stderr = stats.linregress(q2[s:e], logI[s:e])
            Rg = numpy.sqrt(-slope * 3)
            if not numpy.isnan(Rg):
                ares = {"start":s, "end":e,
                        "Rg":Rg, "logI0":intercept, "R":r, "tt":tt, "stderr":stderr, "len":e - s, "I0":numpy.exp(intercept),
                        "qminRg":Rg * q[s],
                        "qmaxRg":Rg * q[e - 1]}
                allres.append(ares)
                if Rg * q[s] <= qminRg and Rg * q[e - 1] <= qmaxRg:
                    res.append(ares)
    print "Naive implementation took: %.3fs" % (time.time() - t0)
    t0 = time.time()
    big_dim = (len_search - mininterval + 1) * (len_search - mininterval) / 2  # + len_search * mininterval
    print "big_dim", big_dim
    x = numpy.zeros((big_dim, len_search), dtype="float32")
    y = numpy.zeros((big_dim, len_search), dtype="float32")
    n = numpy.zeros(big_dim, dtype="int16")
    start = numpy.zeros(big_dim, dtype="int16")
    stop = numpy.zeros(big_dim, dtype="int16")
    idx = 0
    print start_search, len_search
    for sta in range(start_search, start_search + len_search - mininterval):
        for sto in range(sta + mininterval, start_search + len_search):
            x[idx, sta - start_search:sto - start_search] = q2[sta :sto]
            y[idx, sta - start_search:sto - start_search] = logI[sta :sto]
            n[idx] = sto - sta
            start[idx] = sta
            stop[idx] = sto
            idx += 1
    print n
    print idx, (n > 0).sum()
    t1 = time.time()
    print "Array creation took: %.3fs" % (t1 - t0)
    Sx = x.sum(axis= -1)
    Sy = y.sum(axis= -1)
    Sxx = (x * x).sum(axis= -1)
    Sxy = (y * x).sum(axis= -1)
    s = (n * Sxy - Sx * Sy) / (n * Sxx - Sx * Sx)
    Rg = numpy.sqrt(-s * 3)
    valid = numpy.logical_and((Rg * q[start] <= qminRg) , (Rg * q[stop - 1] <= qmaxRg))
    t2 = time.time()
    print "Calculations took: %.3fs" % (t2 - t1)
    print valid
    if valid.sum()>0:
        start = start[valid]
        stop = stop[valid]
        x = x[valid]
        y = y[valid]
        n = n[valid]
        s = s[valid]
        Rg = Rg[valid]
        Sx = Sx[valid]
        Sy = Sy[valid]
        Sxx = Sxx[valid]
        Sxy = Sxy[valid]
        Syy = (y*y).sum(axis= -1)
        intercept = (Sy - Sx * s) / n
        I0 = numpy.exp(intercept)
        error_square = ((y - x * numpy.outer(s, numpy.ones(y.shape[1])) - numpy.outer(intercept, numpy.ones(y.shape[1]))) ** 2).sum(axis= -1) / n
        print error_square
#        print Sx.shape, Sy.shape, Sxx.shape, Sxy.shape, Syy.shape
#        r = (Sx * Sy - n * Sxy) / numpy.sqrt((n * Sxx - Sx * Sx) * (n * Syy - Sy * Sy))
        best = error_square.argmin()
        print best, n[best], Rg[best], I0[best], start[best], stop[best]
#        import pylab
#        pylab.hist(Rg, 100)
#        pylab.hist(I0, 100)
#        pylab.show()
    else:
        print("No valid region found")
        return
    if not res:
        return
#        print ("no good results ")
#        res = allres
    res.sort(cmp)
    if res:
        return res[-1]



if __name__ == "__main__":
    if "autorg" in sys.argv[0].lower():
            usage = """autorg.py [OPTIONS] <DATAFILE(S)>

Estimation of radius of gyration from SAS data by Guinier approximation.

Output: estimated Rg, standard deviation of Rg, estimated I(0), standard
deviation of I(0), first point of chosen Guinier interval, last point of chosen
Guinier interval, estimated data quality, aggregation check.

Known options:
  -h, --help                print this help, then exit
  -v, --version             print version information, then exit
  -o, --output <FILE>       relative or absolute file path to save result
  -f, --format <FORMAT>     output format, one of: csv, ssv, table
      --mininterval <VALUE> minimum interval length in points (default: 10)
      --smaxrg <VALUE>      maximum Smax*Rg value (default: 1.3)
      --sminrg <VALUE>      maximum Smin*Rg value (default: 1.0)

Report bugs to <jerome.kieffer@esrf.fr>.
"""
            version = "%prog " + __version__
            parser = OptionParser(usage=usage, version=version)
            parser.add_option("-o", "--output", dest="output",
                              type='string', default=None,
                              help="relative or absolute file path to save result")
            parser.add_option("-f", "--format", dest="format",
                              type="string", default=None,
                              help="output format, one of: csv, ssv, table")
            parser.add_option("--mininterval", dest="mininterval",
                              type="int", default=10,
                              help="minimum interval length in points (default: 10)")
            parser.add_option("--smaxrg", dest="smaxrg",
                              type="float", default=1.3,
                              help="maximum Smax*Rg value (default: 1.3)")
            parser.add_option("--sminrg", dest="sminrg",
                              type="float", default=1.0,
                              help="maximum Smin*Rg value (default: 1.0)")
            (options, args) = parser.parse_args()
            if len(args) < 1:
                parser.error("incorrect number of arguments: use -h to get help")
            for afile in args:
                if os.path.isfile(afile):
                    r = autoRg(datfile=afile, mininterval=options.mininterval, qminRg=options.sminrg, qmaxRg=options.smaxrg)
                    if r:
                        print """Rg   =  %5.2f 
I(0) =  %5.1f
Points   %i to %i (%i total)""" % (r["Rg"], r["I0"], r["start"] + 1, r["end"] , r["len"])
                    else:
                        print "No Rg found for '%s'." % afile


#                    fig = guinierPlot(curve_file=afile)

                else:
                    print("No such file %s" % afile)
#            plt.show()
    elif "testall" in sys.argv[0].lower():
        for afile in sys.argv[1:]:
            for line in open(afile):
                if "# AutoRg: Points" in line:
                    d = [int(i) for i in line.split() if i.isdigit()]
                    if len(d) >= 2:
                        first_point = d[0]
                        last_point = d[1]
                        break
                elif "# AutoRg: Rg" in line:
                    Rg = float(line.split()[4])
                elif "# AutoRg: I(0)" in line:
                    I0 = float(line.split()[4])
            t0 = time.time()
            r = autoRg(datfile=afile)
            t1 = time.time()
            if r:
                print("%s: Rg=%.2f(%.2f) I0=%.2f(%.2f) on %i(%i) -> %i(%i). took %.3fs" % (afile, r["Rg"], Rg, r["I0"], I0, r["start"] + 1, first_point, r["end"], last_point, t1 - t0))
            else:
                if first_point == 0 and 0 == last_point:
                    print("OK %s: No Rg, was %i %i.\t took %.3fs" % (afile, first_point, last_point, t1 - t0))
                else:
                    print("!! %s: No Rg, was %i %i.\t took %.3fs" % (afile, first_point, last_point, t1 - t0))

