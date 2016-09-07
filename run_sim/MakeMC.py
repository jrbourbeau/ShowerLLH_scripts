#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v1/icetray-start
#METAPROJECT /data/user/jbourbeau/metaprojects/icerec/V05-00-00/build

##########################################################################
# Runs the grid search on the given files and writes to hdf5 output
##########################################################################

import argparse
import time

from icecube import icetray, dataio, toprec
from I3Tray import I3Tray
from icecube.tableio import I3TableWriter
from icecube.hdfwriter import I3HDFTableService

import support_functions.simfunctions as simfunctions


if __name__ == "__main__":

    p = argparse.ArgumentParser(
        description='Extracts MC primary information from fileList')
    p.add_argument('-c', '--config', dest='config',
                   help='Detector configuration')
    p.add_argument('-f', '--files', dest='files', nargs='*',
                   help='Files to run over')
    p.add_argument('-o', '--outFile', dest='outFile',
                   help='Output file')
    args = p.parse_args()

    # Keys to write to frame
    keys = ['MCPrimary']
    subeventstream = simfunctions.null_stream(args.config)

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
    tray.AddModule('I3Reader', 'reader', FileNameList=good_file_list)
    hdf = I3HDFTableService(args.outFile)
    tray.AddModule(I3TableWriter, 'writer', tableservice=hdf, keys=keys,
                   SubEventStreams=[subeventstream])
    tray.Execute()
    tray.Finish()

    print('Time taken: {}'.format(time.time() - t0))
