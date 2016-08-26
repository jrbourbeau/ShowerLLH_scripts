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
    resourcedir = mypaths.llh_resource

    p = argparse.ArgumentParser(
        description='Merges all count tables in a given directory')
    p.add_argument('--ctdir', dest='ctdir',
                   default=resourcedir + '/counttables',
                   help='Location of \'counttables\' directory to merge')
    p.add_argument('--overwriteCounts', action='store_true', dest='overwriteCounts',
                   default=False, help='Overwrite existing merged files')
    p.add_argument('--overwriteLLH', action='store_true', dest='overwriteLLH',
                   default=False, help='Overwrite existing merged files')
    p.add_argument('--remove', dest='remove',
                   default=False, action='store_true',
                   help='Remove unmerged counttables .npy files')
    args = p.parse_args()

    # --------
    # Merge counts table
    # --------
    # Build list of simulations
    masterlist = glob.glob(args.ctdir + '/counttable_*_part??????-??????.npy')
    simlist = np.unique(['_'.join(f.split('_')[:-1]) for f in masterlist])

    for sim in simlist:
        outfile = '{}.npy'.format(sim)
        if not args.overwriteCounts and os.path.exists(outfile):
            print('\n{} already exists. Skipping...'.format(outfile))
            continue
        filelist = glob.glob(sim + '_part??????-??????.npy')
        filelist.sort()

        if len(filelist) == 0:
            raise SystemError('No subfiles found for ' + sim + '.')

        print('\nMerging {}...'.format(sim))
        ShowerLLH.merge_counts_tables(filelist, outfile)
        # Remove all un-merged count table files
        if args.remove:
            for f in filelist:
                os.remove(f)

    # --------
    # Convert counts to log-probability
    # --------
    masterlist = glob.glob('{}/counttable_*.npy'.format(args.ctdir))
    mergedlist = [f for f in masterlist if '_part' not in f]

    # Get list of LLH bin schemes used
    binlist = np.unique([re.split('_|\.', f)[-2] for f in mergedlist])

    for bintype in binlist:

        outfile = '{}/LLH_tables_{}.npy'.format(mypaths.llh_resource, bintype)
        if not args.overwriteLLH and os.path.exists(outfile):
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
        print('Making {} LLH tables...\n'.format(bintype))
        table.make_LLH_tables(filelist, outfile)
