#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v1/icetray-start
#METAPROJECT /data/user/jbourbeau/metaprojects/icerec/V05-00-00/build

##########################################################################
# Runs the grid search on the given files and writes to hdf5 output
##########################################################################

import numpy as np
import time
import glob
import argparse

from icecube import dataio, toprec, ShowerLLH
from I3Tray import *
from icecube.tableio import I3TableWriter
from icecube.hdfwriter import I3HDFTableService

import support_functions.simfunctions as simfunctions
from support_functions.checkdir import checkdir
from support_functions.i3modules import PruneIceTop, moveMCPrimary


if __name__ == "__main__":

    p = argparse.ArgumentParser(
        description='Runs ShowerLLH over a given fileList')
    p.add_argument('-f', '--files', dest='files', nargs='*',
                   help='Files to run over')
    p.add_argument('-c', '--config', dest='config',
                   help='Detector configuration')
    p.add_argument('--llhFile', dest='llhFile',
                   help='File with llh tables for reconstruction')
    p.add_argument('-o', '--outFile', dest='outFile',
                   help='Output file')
    p.add_argument('--test', dest='test',
                   default=False, action='store_true',
                   help='Option for running test sample off cluster')
    p.add_argument('--cpp', dest='cpp',
                   default=False, action='store_true',
                   help='Run in (static) c++ mode')
    args = p.parse_args()

    # Starting parameters
    recoPulses = simfunctions.recoPulses(args.config)
    it_stream = simfunctions.it_stream(args.config)

    # Load grids for grid scan, llh tables, and bins
    LLH_grid = ShowerLLH.LLHGrid(config=args.config)
    grids = LLH_grid.search_grid
    LLH_file = np.load(args.llhFile)
    LLH_file = LLH_file.item()
    LLH_tables = LLH_file['llhtables']
    LLH_bins = ShowerLLH.LLHBins(LLH_file['bintype'])
    binDict = LLH_bins.bins


    # Keys to write to frame
    keys = []
    keys += ['I3EventHeader']
    for comp in LLH_tables.keys():
        keys += ['ShowerLLH_' + comp, 'ShowerLLHParams_' + comp]
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
    checkdir(args.outFile)
    hdf = I3HDFTableService(args.outFile)

    #====================================================================
    # Clean up events

    tray.AddModule(PruneIceTop,
                   it_stream=it_stream)

    tray.AddModule(moveMCPrimary)

    #====================================================================
    # Run the reconstruction

    # C++ mode faster
    if args.cpp:
        gridx, gridy = np.transpose(grids[0])
        for comp in LLH_tables.keys():
            llh = list(LLH_tables[comp].flatten())
            tray.AddModule('ShowerLLH', 'ShowerLLH_' + comp,
                           recoPulses=recoPulses,
                           comp=comp,
                           ebins=list(binDict[0][1]),
                           # zbins=list(binDict[1][1]),
                           sbins=list(binDict[1][1]),
                           dbins=list(binDict[2][1]),
                           cbins=list(binDict[3][1]),
                           gridx=gridx, gridy=gridy,
                           llhTable=llh)

    # Python implementation fast enough to run on simulation
    # (and more flexible for binning tests)
    else:
        tray.AddModule(ShowerLLH.GridLLH, 'ShowerLLHGrid',
                       LLHTables=LLH_tables,
                       binDict=binDict,
                       grids=grids,
                       recoPulses=recoPulses)

    #====================================================================
    # Finish

    tray.AddModule(I3TableWriter, tableservice=hdf, keys=keys,
                   SubEventStreams=[it_stream])

    tray.Execute()
    tray.Finish()

    print "Time taken: ", time.time() - t0
