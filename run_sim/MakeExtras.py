#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v1/icetray-start
#METAPROJECT /data/user/jbourbeau/metaprojects/icerec/V05-00-00/build

##########################################################################
# Runs the grid search on the given files and writes to hdf5 output
##########################################################################

import numpy as np
import time
import glob
import argparse

from icecube import dataio, toprec
from I3Tray import *
from icecube.tableio import I3TableWriter
from icecube.hdfwriter import I3HDFTableService

import support_functions.simfunctions as simfunctions
from support_functions.i3modules import GetStations, PruneIceTop, moveMCPrimary
from support_functions.i3modules import FindLoudestStation, LoudestStationOnEdge
from support_functions.i3modules import LargestTankCharges


if __name__ == "__main__":

    p = argparse.ArgumentParser(
        description='Runs extra modules over a given fileList')
    p.add_argument('-f', '--files', dest='files', nargs='*',
                   help='Files to run over')
    p.add_argument('-c', '--config', dest='config',
                   help='Detector configuration')
    p.add_argument('-o', '--outFile', dest='outFile',
                   help='Output file')
    args = p.parse_args()

    # Starting parameters
    recoPulses = simfunctions.recoPulses(args.config)
    it_stream = simfunctions.it_stream(args.config)

    # Keys to write to frame
    keys = []
    keys += ['I3EventHeader']
    keys += ['ShowerPlane', 'ShowerPlaneParams']
    keys += ['LoudestStation', 'LoudestOnEdge']
    keys += ['SaturationList', 'SaturatedOnEdge']
    keys += ['Q1', 'Q2', 'Q3', 'Q4']
    keys += ['NStations']
    #keys += [recoPulses]
    keys += ['MCPrimary']

    t0 = time.time()

    # Construct list of non-truncated files to process
    good_file_list = []
    for test_file in args.files:
        try:
            test_tray = I3Tray()
            test_tray.context['I3FileStager'] = dataio.get_stagers(staging_directory=os.environ['_CONDOR_SCRATCH_DIR'])
            test_tray.Add('I3Reader', FileName=test_file)
            test_tray.Execute()
            test_tray.Finish()
            good_file_list.append(test_file)
        except:
            print('file {} is truncated'.format(test_file))
            pass
    del test_tray

    tray = I3Tray()
    tray.context['I3FileStager'] = dataio.get_stagers(staging_directory=os.environ['_CONDOR_SCRATCH_DIR'])
    tray.AddModule('I3Reader', FileNameList=good_file_list)
    hdf = I3HDFTableService(args.outFile)

    #====================================================================
    # Clean up events

    tray.AddModule(PruneIceTop,
                   it_stream=it_stream)

    tray.AddModule(moveMCPrimary)

    #====================================================================
    # Cut information

    tray.AddModule(GetStations,
                   InputITpulses=recoPulses,
                   output='NStations')

    tray.AddModule(FindLoudestStation,
                   InputITpulses=recoPulses,
                   SaturationValue=600,
                   output='SaturationList')

    tray.AddModule(LoudestStationOnEdge,
                   InputLoudestStation='LoudestStation',
                   config=args.config,
                   output='LoudestOnEdge')

    tray.AddModule(LoudestStationOnEdge,
                   InputLoudestStation='SaturationList',
                   config=args.config,
                   output='SaturatedOnEdge')

    tray.AddModule(LargestTankCharges,
                   ITpulses=recoPulses)

    #====================================================================
    # Finish

    tray.AddModule(I3TableWriter, tableservice=hdf, keys=keys,
                   SubEventStreams=[it_stream])

    tray.Execute()
    tray.Finish()

    print "Time taken: ", time.time() - t0
