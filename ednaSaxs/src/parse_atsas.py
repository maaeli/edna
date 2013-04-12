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

from __future__ import with_statement

__authors__ = ["Jérôme Kieffer"]
__license__ = "GPLv3+"
__copyright__ = "ESRF"
__date__ = "20130412"
__status__ = "Development"
__version__ = "0.1"
__doc__ = "parse some of the atsas files"
import os, sys, time, logging
from StringIO import  StringIO

################################################################################
# #Those functions should be in try/except to be able to properly report bugs
################################################################################

def SqrtChi(firFile=None):
    sqrtChi = 42 #what else ?
    if not firFile or not os.path.exists(firFile):
        raise(RuntimeError("In parse for sqrt(Chi): .fir file %s does not exist" % firFile))
    with open(firFile) as ff:
        sqrtChi = float(ff.readline().split('=')[-1])
    return sqrtChi
    

def RFactor(logFile=None):
    tmpRfactor = 42 #what else ?
    if not logFile or not os.path.exists(logFile):
        raise(RuntimeError("In parse for RFactor: .log file %s does not exist"%logFile))
    with open(logFile) as ff:
        for line in ff:
            wordsLine = line.split()
            if wordsLine and wordsLine[0] == "Rf:":
                tmpRfactor = float(wordsLine[1][:-1])
    return tmpRfactor

def parsePDB(pdbFile=None):
    """
    parse PDB file for Rfactor, Dmax, Volume and Rg 
    """
    res = {}
    if not logFile or not os.path.exists(pdbFile):
        raise(RuntimeError("In parse PDB: file %s does not exist" % pdbFile))
    with open(pdbFile) as ff:
        for line in ff:
            if line.startswith("REMARK 265"):
                if "Final R-factor" in line:
                    res["Rfactor"] = float(line.split(":")[-1])
                elif "Total excluded DAM volume" in line:
                    res["volume"] = float(line.split(":")[-1])
                elif "Phase radius of gyration" in line:
                    res["Rg"] = float(line.split(":")[-1])
                elif "Maximum phase diameter" in line:
                    res["Dmax"] = float(line.split(":")[-1])
    return res
