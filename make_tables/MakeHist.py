#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v1/icetray-start
#METAPROJECT /data/user/jbourbeau/metaprojects/icerec/V05-00-00/build

#############################################################################
# Makes the probability tables using FillHist and records as .npy files
#############################################################################

import numpy as np
import argparse
import time

from icecube import icetray, dataio, ShowerLLH
from I3Tray import I3Tray


if __name__ == "__main__":

    p = argparse.ArgumentParser(
        description='Builds binned histograms for use with ShowerLLH')
    p.add_argument('-f', '--files', dest='files', nargs='*',
                   help='Input filelist to run over')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='standard',
                   choices=['standard', 'nozenith', 'logdist','nosnow'],
                   help='Option for a variety of preset bin values')
    p.add_argument('-o', '--outFile', dest='outFile',
                   help='Output filename')
    args = p.parse_args()

    # Starting parameters
    recoPulses = 'CleanedHLCTankPulses'

    # Get LLHBins
    LLH_bins = ShowerLLH.LLHBins(args.bintype)

    # Construct list of non-truncated files to process
    good_file_list = []
    for test_file in args.files:
        try:
            test_tray = I3Tray()
            test_tray.Add('I3Reader', FileName=test_file)
            test_tray.Execute()
            test_tray.Finish()
            good_file_list.append(test_file)
        except:
            print('file {} is truncated'.format(test_file))
            pass
    del test_tray

    # Execute FillHist on good files
    t0 = time.time()
    tray = I3Tray()
    tray.Add('I3Reader', FileNameList=good_file_list)
    tray.Add(ShowerLLH.FillHist,
             binDict=LLH_bins.bins,
             bintype=LLH_bins.bintype,
             recoPulses=recoPulses,
             outFile=args.outFile)
    tray.Execute()
    tray.Finish()

    print('Time taken: {}'.format(time.time() - t0))
