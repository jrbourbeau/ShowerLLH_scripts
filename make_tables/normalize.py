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
                   default=mypaths.llh_dir + '/resources',
                   help='Path to ShowerLLH resources directory')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='logdist',
                   choices=['standard', 'nozenith', 'logdist', 'nosnow'],
                   help='Option for a variety of preset bin values')
    p.add_argument('--overwrite', action='store_true', dest='overwrite',
                   default=False, help='Overwrite existing merged files')
    args = p.parse_args()

    ctdir = args.resources + '/counttables'
    masterlist = glob.glob('{}/counttable_*_{}.npy'.format(ctdir, args.bintype))
    filelist = [f for f in masterlist if '_part' not in f]
    filelist.sort()

    outfile = '{}/LLH_table_{}.npy'.format(args.resources, args.bintype)
    if not args.overwrite and os.path.exists(outfile):
        SystemExit('\n{} already exists. Skipping...'.format(outfile))

    # Exclude specific simuation sets
    # These simulation sets are not used to build the likelihood tables
    # Instead, they are used to test test ShowerLLH reconstructions
    filelist = [f for f in filelist if '_7394_' not in f]
    filelist = [f for f in filelist if '_7483_' not in f]
    filelist = [f for f in filelist if '_7486_' not in f]
    filelist = [f for f in filelist if '_7351_' not in f]
    if len(filelist) == 0:
        SystemError('\nNo meged count tables for {} LLH bin scheme...'.format(bintype))

    table = ShowerLLH.LLHTable(bintype=args.bintype)
    print('Making {} LLH tables...\n'.format(args.bintype))
    table.make_LLH_tables(filelist, outfile)
