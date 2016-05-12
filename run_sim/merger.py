#!/usr/bin/env python

import argparse
import glob
import os
import support_functions.simFunctions as simFunctions
import support_functions.myGlobals as my

if __name__ == "__main__":

    # Import global path names
    my.setupGlobals(verbose=False)
    my.setupShowerLLH(verbose=False)

    p = argparse.ArgumentParser(description='Merges simulation hdf5 files')
    p.add_argument('--overwrite', dest='overwrite',
                   default=False, action='store_true',
                   help='Overwrite existing merged files')
    p.add_argument('--prefix', dest='prefix',
                   help='Path to sim file to be merged')
    args = p.parse_args()

    # Make comprehensive list of all sim subfiles
    if args.prefix:
        masterList = glob.glob(args.prefix + '/files/SimLLH_*_part*.hdf5')
    else:
        masterList = glob.glob(
            '%s/*_sim/files/SimLLH_*_part*.hdf5' % my.llh_data)
    masterList.sort()

    # Reduce list to set of all leading filenames (exclude parts)
    params = ['_'.join(f.split('_')[:-1]) for f in masterList]
    params = sorted(list(set(params)))

    for fileStart in params:

        outFile = '%s.hdf5' % fileStart
        if os.path.isfile(outFile) and not args.overwrite:
            print 'Outfile %s already exists. Skipping...' % outFile
            continue
        if os.path.isfile(outFile) and args.overwrite:
            print 'Outfile %s already exists. Overwriting...' % outFile
            os.remove(outFile)

        fileList = glob.glob(fileStart + '_part*-*.hdf5')
        fileList.sort()

        fileList = ' '.join(fileList)
        hdf = '%s/build/hdfwriter/resources' % my.offline
        ex = 'python %s/scripts/merge.py -o %s %s' % (hdf, outFile, fileList)
        os.system(ex)
