#!/bin/sh /cvmfs/icecube.opensciencegrid.org/py2-v1/icetray-start
#METAPROJECT /data/user/jbourbeau/metaprojects/icerec/V05-00-00/build

import glob
import argparse
import os
import re
import numpy as np

from icecube import ShowerLLH
import support_functions.paths as paths

if __name__ == "__main__":

    # Global variables setup for path names
    mypaths = paths.Paths()

    p = argparse.ArgumentParser(
        description='Merges all count tables in a given directory')
    p.add_argument('--resources', dest='resources',
                   default=mypaths.llh_dir+'/resources',
                   help='Path to ShowerLLH resources directory')
    p.add_argument('-s', '--sim', dest='sim',
                   help='Simulation dataset to run over')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='logdist',
                   choices=['standard', 'nozenith', 'logdist', 'nosnow'],
                   help='Option for a variety of preset bin values')
    p.add_argument('--overwrite', action='store_true', dest='overwrite',
                   default=False, help='Overwrite existing merged files')
    p.add_argument('--remove', dest='remove',
                   default=False, action='store_true',
                   help='Remove unmerged counttables .npy files')
    args = p.parse_args()

    ctdir = args.resources + '/counttables'
    outfile = '{}/counttable_{}_{}.npy'.format(ctdir, args.sim, args.bintype)
    if not args.overwrite and os.path.exists(outfile):
        SystemExit('\n{} already exists. Skipping...'.format(outfile))
    filelist = glob.glob(
        ctdir + '/counttable_{}_{}_part??????-??????.npy'.format(args.sim, args.bintype))
    filelist.sort()

    if len(filelist) == 0:
        raise SystemError('No subfiles found for {} with {} bins.'.format(args.sim, args.bintype))

    print('\nMerging {} {}...'.format(args.sim, args.bintype))
    ShowerLLH.merge_counts_tables(filelist, outfile)
    # Remove all un-merged count table files
    if args.remove:
        for f in filelist:
            os.remove(f)
