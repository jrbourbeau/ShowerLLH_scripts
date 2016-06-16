#!/usr/bin/env python

import glob
import argparse
import os
import re
import numpy as np

from icecube import ShowerLLH
import support_functions.myGlobals as my

if __name__ == "__main__":

    # Global variables setup for path names
    my.setupGlobals(verbose=False)
    resourcedir = my.llh_resource

    p = argparse.ArgumentParser(
        description='Merges all count tables in a given directory')
    p.add_argument('--ctdir', dest='ctdir',
                   default=resourcedir + '/CountTables',
                   help='Location of CountTables to merge')
    p.add_argument('--overwrite', action='store_true', dest='overwrite',
                   default=False, help='Overwrite existing merged files')
    args = p.parse_args()

    # --------
    # Merge counts table
    # --------
    # Build list of simulations
    masterlist = glob.glob(args.ctdir + '/CountTable_*_Part??????-??????.npy')
    simlist = np.unique(['_'.join(f.split('_')[:-1]) for f in masterlist])

    for sim in simlist:
        outfile = '{}.npy'.format(sim)
        if not args.overwrite and os.path.exists(outfile):
            print('\n{} already exists. Skipping...'.format(outfile))
            continue
        filelist = glob.glob(sim + '_Part??????-??????.npy')
        filelist.sort()

        if len(filelist) == 0:
            raise SystemError('No subfiles found for ' + sim + '.')

        print('\nMerging {}...'.format(sim))
        ShowerLLH.merge_counts_tables(filelist, outfile)
        # Remove all un-merged count table files
        for f in filelist:
            os.remove(f)

    # --------
    # Convert counts to log-probability
    # --------
    masterlist = glob.glob('{}/CountTable_*.npy'.format(args.ctdir))
    mergedlist = [f for f in masterlist if '_Part' not in f]

    # Get list of LLH bin schemes used
    binlist = np.unique([re.split('_|\.', f)[-2] for f in mergedlist])

    for bintype in binlist:

        outfile = '{}/LLHTables_{}.npy'.format(my.llh_resource, bintype)
        if not args.overwrite and os.path.exists(outfile):
            print('\n{} already exists. Skipping...'.format(outfile))
            continue

        filelist = [f for f in mergedlist if bintype in f]
        filelist.sort()
        # Exclude specific simuation sets
        # These simulation sets are not used to build the likelihood tables
        # Instead, they are used to test test ShowerLLH reconstructions
        filelist = [f for f in filelist if '_7394_' not in f]
        filelist = [f for f in filelist if '_7483_' not in f]
        filelist = [f for f in filelist if '_7486_' not in f]
        filelist = [f for f in filelist if '_7351_' not in f]
        if len(filelist) == 0:
            print('\nNo meged count tables for {} LLH bin scheme...'.format(bintype))
            continue

        table = ShowerLLH.LLHTable(bintype=bintype)
        table.make_LLH_tables(filelist, outfile)
