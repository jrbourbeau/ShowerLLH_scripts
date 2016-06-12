#!/usr/bin/env python

#############################################################################
# Makes the probability tables using AddToHist and records as .npy files
#############################################################################

import numpy as np
import argparse
import time

from icecube import icetray, dataio
from I3Tray import I3Tray
import AddToHist
import support_functions.myGlobals as my

if __name__ == "__main__":

    # Global variables setup for path names
    my.setupGlobals(verbose=False)

    p = argparse.ArgumentParser(
        description='Builds binned histograms for use with ShowerLLH')
    p.add_argument('-f', '--files', dest='files', nargs='*',
                   help='Input filelist to run over')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='standard',
                   choices=['standard', 'nozenith', 'logdist'],
                   help='Option for a variety of preset bin values')
    p.add_argument('-o', '--outFile', dest='outFile',
                   help='Output filename')
    args = p.parse_args()

    # Starting parameters
    recoPulses = 'CleanedHLCTankPulses'

    # Import ShowerLLH bins
    binFile = '{}/ShowerLLH_bins.npy'.format(my.llh_resource)
    binDict = np.load(binFile)
    binDict = binDict.item()
    binDict = binDict[args.bintype]

    # Execute
    t0 = time.time()
    tray = I3Tray()
    tray.Add('I3Reader', FileNameList=args.files)
    tray.Add(AddToHist.fillHist,
             binDict=binDict,
             recoPulses=recoPulses,
             outFile=args.outFile)
    tray.Execute()
    tray.Finish()

    print('Time taken: {}'.format(time.time() - t0))
