#!/usr/bin/python
# Written by Jerome Kieffer <jerome.kieffer@esrf.fr> 18/07/2017
#Compress the logs fro edna in /nobackup to free inodes

import sys
import os
import glob
import shutil
import tarfile
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger("compress_log")

for root in glob.glob("/nobackup/*"):
    if not os.path.isdir(root):
        continue
    logdirs = glob.glob(root+"/edna-????????T??????")
    logdirs.sort()

    if len(logdirs)<2:
        logger.info("Nothing to compress, only found %s", logdirs)
        continue

    for logdir in logdirs[:-1]:
        dest = logdir + ".tar.bz2"
        logger.debug("Compressing %s", logdir)
        with tarfile.TarFile(dest, mode="w:bz2") as tar:
            tar.add(logdir, arcname=logdir[len(root):])
        logger.debug("Remove directory %s", logdir)
        shutil.rmtree(logdir)

