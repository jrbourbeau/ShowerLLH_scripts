#!/usr/bin/env python

import argparse
import glob
import os
import re
import numpy as np

import support_functions.myGlobals as my
import support_functions.simFunctions as simFunctions
from support_functions.submit_npx4 import py_submit
from support_functions.checkdir import checkdir

if __name__ == "__main__":

    # Global variables setup for path names
    my.setupGlobals(verbose=False)
    simOutput = simFunctions.getSimOutput()

    p = argparse.ArgumentParser(
        description='Makes binned histograms for use with ShowerLLH',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=simOutput)
    p.add_argument('-s', '--sim', dest='sim', nargs='*',
                   help='Simulation dataset to run over')
    p.add_argument('-n', '--n', dest='n', type=int,
                   default=100,
                   help='Number for files to run per submission batch')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='standard',
                   choices=['standard', 'nozenith', 'logdist','nosnow'],
                   help='Option for a variety of preset bin values')
    p.add_argument('--test', dest='test', action='store_true',
                   default=False,
                   help='Option for running off cluster to test')
    args = p.parse_args()

    # Default parameters
    outDir = '{}/CountTables/'.format(my.llh_resource)
    checkdir(outDir)
    if args.test and args.n == 100:
        args.n = 1

    cwd = os.getcwd()
    exList, jobIDs = [], []

    for sim in args.sim:

        # Build fileList
        config = simFunctions.sim2cfg(sim)
        files = simFunctions.getSimFiles(sim)
        gcd = simFunctions.getGCD(config)
        # Split into batches
        batches = [files[i:i + args.n] for i in range(0, len(files), args.n)]
        if args.test:
            batches = batches[:2]

        for bi, batch in enumerate(batches):

            start = re.split('\.', batch[0])[-3]
            end = re.split('\.', batch[-1])[-3]
            outFile = '{}CountTable_{}_{}'.format(outDir, sim, args.bintype)
            outFile += '_Part' + start + '-' + end + '.npy'

            batch.insert(0, gcd)
            batch = ' '.join(batch)

            cmd = 'python {}/MakeHist.py'.format(cwd)
            ex = '{} -f {} -b {} -o {}'.format(cmd,
                                               batch, args.bintype, outFile)
            if not args.test:
                ex = ' '.join([my.env, ex])
            exList += [[ex]]
            jobIDs += ['counttables_%s_%04i' % (sim, bi)]

    # Moderate number of submitted jobs
    njobs = len(exList)
    if njobs > 500:
        yn = raw_input(
            'About to submit {} jobs. You sure? [y|n]: '.format(njobs))
        if yn != 'y':
            raise SystemExit('Aborting...{}'.format(njobs))

    # Submit jobs
    print('Submitting {} batches...'.format(njobs))
    for ex, jobID in zip(exList, jobIDs):
        py_submit(ex, test=args.test, jobID=jobID)