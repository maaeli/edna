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

import os
import numpy
from scipy import stats
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

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

    end = min(q.size, (-1.5 / slope > q).sum())
    q = q[:end]
    I = I[:end]
    q2 = q2[:end]
    logI = logI[:end]


    fig1 = plt.figure(figsize=(6, 5))
    ax1 = fig1.add_subplot(1, 1, 1)
    ax1.plot(q2, logI, label="Experimental curve")
    ax1.plot(q2[first_point:last_point], logI[first_point:last_point], marker='D', markersize=5, label="Guinier region")
    ax1.annotate("qRg$_{min}$=%.1f" % (-slope * q[first_point]), (q2[first_point], logI[first_point]), xytext=None, xycoords='data',
         textcoords='data')
    ax1.annotate("qRg$_{max}$=%.1f" % (-slope * q[last_point]), (q2[last_point], logI[last_point]), xytext=None, xycoords='data',
         textcoords='data')

    ax1.plot(q2, intercept + slope * q2, label="ln[$I(q)$] = %.2f %.2f * $q^2$" % (intercept, slope))
    ax1.set_ylabel('ln[$I(q)$]')
    ax1.set_xlabel('$q^2$ (%s$^{-2}$)' % unit)
    ax1.set_title("Guinier plot")
    ax1.legend(loc=8)
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

