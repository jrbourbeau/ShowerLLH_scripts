#!/usr/bin/env python

#############################################################################
# Converts individual count tables into a single normalized LLH table
#############################################################################

import numpy as np
import glob
import re
import os
import support_functions.myGlobals as my
import support_functions.simFunctions as simFunctions

from icecube.ShowerLLH import LLHTable


def makeLLH(filelist, outfile):
    if isinstance(filelist, basestring):
        filelist = [filelist]
    cumulative, norm = {}, {}
    # Sum all CountTables
    for i, file in enumerate(filelist):
        # print('Loading '+file)
        q = np.load(file)
        q = q.item()
        # Record and check binning
        if i == 0:
            bins = q['bins']
        # Get composition from simulation
        sim = re.split('_|\.', os.path.basename(file))[1]
        comp = simFunctions.sim2comp(sim, full=True)
        # Add to cumulative table
        if comp not in cumulative.keys():
            cumulative[comp] = np.zeros(q['counts'].shape, dtype=float)
        cumulative[comp] += q['counts']

    # Normalize and log tables (log10(Hist/Hist.sum()))
    # print('Normalizing tables...')
    for comp in cumulative.keys():
        cumulative[comp] += .1    # baseline so zeros don't give errors
        norm[comp] = np.zeros(cumulative[comp].shape, dtype=float)
        for idx in np.ndindex(cumulative[comp].shape[:-1]):
            # if sum(cumulative[comp][idx])!=2.9:
            #     print(sum(cumulative[comp][idx]))
            #     # print('idx = {}'.format(idx))
            #     # print('cumulative[comp][idx] = {}'.format(cumulative[comp][idx]))
            #     # print('sum = {}'.format(sum(cumulative[comp][idx])))
            norm[comp][idx] = np.log10(
                cumulative[comp][idx] / sum(cumulative[comp][idx]))

    # Write to file
    np.save(outfile, {'bins': bins, 'llhtables': norm})
    print('{} saved.'.format(outfile))


if __name__ == "__main__":

    # Global variables setup for path names
    my.setupShowerLLH(verbose=False)

    masterlist = glob.glob(
        '{}/CountTables/CountTable_*.npy'.format(my.llh_resource))
    mergedlist = [f for f in masterlist if '_Part' not in f]
    # masterlist = [f for f in masterlist if '_Part' not in f]

    # Get list of LLH bin schemes used
    binlist = np.unique([re.split('_|\.', f)[-2] for f in mergedlist])

    for bintype in binlist:
        filelist = [f for f in mergedlist if bintype in f]
        filelist.sort()
        # Exclude specific simuation sets
        # These simulation sets are not used to build the likelihood tables
        # Instead, they are used to test test ShowerLLH reconstructions
        filelist = [f for f in filelist if '_7394_' not in f]
        filelist = [f for f in filelist if '_7483_' not in f]
        filelist = [f for f in filelist if '_7486_' not in f]
        filelist = [f for f in filelist if '_7351_' not in f]

        outfile = '{}/LLHTables_{}.npy'.format(my.llh_resource, bintype)

        table = LLHTable(bintype=bintype)

        if len(filelist) != 0:
            print('\nMaking table for {} LLH bin scheme...'.format(bintype))
            makeLLH(filelist, outfile)
