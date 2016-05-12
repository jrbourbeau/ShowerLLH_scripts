#!/usr/bin/env python

import glob
import argparse
import os
import numpy as np

import ShowerLLH_scripts.support_functions.myGlobals as my

if __name__ == "__main__":

    # Global variables setup for path names
    my.setupShowerLLH(verbose=False)
    resourcedir = my.llh_resource

    p = argparse.ArgumentParser(
        description='Merges all count tables in a given directory')
    p.add_argument('-p', '--prefix', dest='prefix',
                   default=resourcedir + '/CountTables/',
                   help='Location of CountTables to merge')
    p.add_argument('--overwrite', action='store_true', dest='overwrite',
                   default=False, help='Overwrite existing merged files')
    args = p.parse_args()

    # Build list of simulations
    masterlist = glob.glob(args.prefix + 'CountTable_*_Part??????-??????.npy')
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

        d = {}
        print('\nMerging {}...'.format(os.path.basename(sim)))
        for i, file in enumerate(filelist):
            q = np.load(file)
            q = q.item()
            if i == 0:
                d['bins'] = q['bins']
                d['counts'] = np.zeros(q['counts'].shape)
            d['counts'] += q['counts']

        np.save(outfile, d)
        print('{} saved.'.format(outfile))
