#!/usr/bin/env python

import argparse
import glob
import os
import re
import numpy as np

import support_functions.paths as paths
from support_functions.dag_submitter import py_submit
from support_functions.checkdir import checkdir
import support_functions.simfunctions as simfunctions

if __name__ == "__main__":

    # Setup global path names
    mypaths = paths.Paths()
    sim_output = simfunctions.getSimOutput()

    p = argparse.ArgumentParser(
        description='Makes binned histograms for use with ShowerLLH',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=sim_output)
    p.add_argument('-s', '--sim', dest='sim', nargs='*',
                   help='Simulation dataset to run over')
    p.add_argument('-n', '--n', dest='n', type=int,
                   default=100,
                   help='Number for files to run per submission batch')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='standard',
                   choices=['standard', 'nozenith', 'logdist', 'nosnow'],
                   help='Option for a variety of preset bin values')
    p.add_argument('--test', dest='test', action='store_true',
                   default=False,
                   help='Option for running off cluster to test')
    args = p.parse_args()

    # Default parameters
    outdir = '{}/counttables'.format(mypaths.llh_resource)
    checkdir(outdir + '/')
    if args.test and args.n == 100:
        args.n = 1

    cwd = os.getcwd()
    cmd = '{}/MakeHist.py'.format(cwd)
    for sim in args.sim:
        # Build arglist for condor submission
        arglist = []

        # Build fileList
        config = simfunctions.sim2cfg(sim)
        files = simfunctions.getSimFiles(sim)
        gcd = simfunctions.getGCD(config)
        # Split into batches
        batches = [files[i:i + args.n] for i in range(0, len(files), args.n)]

        if args.test:
            batches = batches[:1]

        for bi, batch in enumerate(batches):

            start = re.split('\.', batch[0])[-3]
            end = re.split('\.', batch[-1])[-3]
            outFile = '{}/counttable_{}_{}'.format(outdir, sim, args.bintype)
            outFile += '_part' + start + '-' + end + '.npy'

            batch.insert(0, gcd)
            batch = ' '.join(batch)

            arglist += ['-f {} -b {} -o {}'.format(
                batch, args.bintype, outFile)]

        # Submit jobs
        jobID = 'ShowerLLH_counttables_{}_{}'.format(sim, args.bintype)
        py_submit(cmd, arglist, mypaths.npx4, test=args.test,
                  jobID=jobID)
