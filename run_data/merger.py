#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v1/icetray-start
#METAPROJECT /data/user/jbourbeau/metaprojects/icerec/V05-00-00/build

import glob
import os
import argparse
import numpy as np

import support_functions.paths as paths
from submit_condor import DAG_submit

if __name__ == "__main__":

    mypaths = paths.Paths()

    p = argparse.ArgumentParser(description='Merge ShowerLLH .hdf5 files')
    p.add_argument('-c', '--config', dest='config',
                   default='IT73',
                   help='Detector configuration')
    p.add_argument('-d', '--date', dest='date',
                   help='Date to run over (optional)')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='logdist',
                   help='ShowerLLH binning used [standard|nozenith|logdist]')
    p.add_argument('--test', dest='test',
                   default=False, action='store_true',
                   help='Run off cluster to test')
    p.add_argument('--overwrite', dest='overwrite',
                   default=False, action='store_true',
                   help='Overwrite existing merged files')
    args = p.parse_args()

    prefix = '{}/{}_data/files'.format(mypaths.llh_dir, args.config)
    cmd = '{}/build/hdfwriter/resources/scripts/merge.py'.format(
        mypaths.metaproject)
    masterlist = glob.glob(
        '{}/DataLLH_????????_{}_part*.hdf5'.format(prefix, args.bintype))
    masterlist.sort()

    dates = [os.path.basename(f).split('_')[1] for f in masterlist]
    dates = np.unique(dates)
    if args.date:
        dates = [yyyymmdd for yyyymmdd in dates if args.date in yyyymmdd]

    cmd = 'python {}/build/hdfwriter/resources/scripts/merge.py'.format(
        mypaths.metaproject)
    globaljobID = 'ShowerLLH_datamerge_{}_{}'.format(args.config, args.bintype)
    jobID_list = []
    infiles_list = []
    outfile_list = []

    for date in dates:
        outfile = '{}/DataLLH_{}_{}.hdf5'.format(prefix, date, args.bintype)
        # Check if file exists
        if os.path.isfile(outfile) and not args.overwrite:
            print('Outfile {} already exists. Skipping...'.format(outfile))
            continue
        if os.path.isfile(outfile) and args.overwrite:
            print('Outfile {} already exists. Removing...'.format(outfile))
            os.remove(outfile)

        # Build list of files and destination
        files = glob.glob('{}/DataLLH_{}_{}_part*.hdf5'.format(prefix, date, args.bintype))
        files.sort()
        files = ' '.join(files)

        infiles_list.append(files)
        outfile_list.append(outfile)
        jobID_list.append('ShowerLLH_datamerge_{}_{}_{}'.format(args.config, args.bintype, date))

    if args.test:
        infiles_list = infiles_list[:1]
        outfile_list = outfile_list[:1]
        jobID_list = jobID_list[:1]

    # Submit jobs
    sublines = None
    DAG_submit(globaljobID, cmd, jobID_list, outfile_list, infiles_list, mypaths.llh_dir + '/condor',
            test=args.test, sublines=sublines)
