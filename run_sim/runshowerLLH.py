#!/usr/bin/env python

import glob
import re
import os
import argparse

import support_functions.paths as paths
import support_functions.simfunctions as simfunctions
from support_functions.dag_submitter import py_submit
from support_functions.checkdir import checkdir

if __name__ == "__main__":

    # Setup global path names
    mypaths = paths.Paths()
    simOutput = simfunctions.getSimOutput()

    p = argparse.ArgumentParser(
        description='Mass runs MakeLLHFiles.py on cluster',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=simOutput)
    p.add_argument('--resources', dest='resources',
                   default=mypaths.llh_dir + '/resources',
                   help='Path to ShowerLLH resources directory')
    p.add_argument('-s', '--sim', dest='sim', nargs='*',
                   help='Simulation to run over')
    p.add_argument('-n', '--n', dest='n', type=int,
                   default=100,
                   help='Number of files to run per batch')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='logdist',
                   help='Choose bin config for llh tables OR other desired info', choices=['standard', 'nozenith', 'logdist', 'nosnow', 'MC', 'lap', 'extras'])
    p.add_argument('--missing', dest='missing',
                   default=False, action='store_true',
                   help='Option to only submit files with missing file names')
    p.add_argument('--test', dest='test', action='store_true',
                   default=False,
                   help='Option for running test off cluster')
    p.add_argument('--cpp', dest='cpp',
                   default=False, action='store_true',
                   help='Run in C++ (static) mode')
    args = p.parse_args()

    cwd = os.getcwd()
    jobID = 'showerLLH_sim'
    if args.bintype == 'MC':
        cmd = '{}/MakeMC.py'.format(cwd)
    elif args.bintype == 'lap':
        cmd = '{}/MakeLaputop.py'.format(cwd)
    elif args.bintype == 'extras':
        cmd = '{}/MakeExtras.py'.format(cwd)
    else:
        cmd = '{}/MakeShowerLLH.py'.format(cwd)
    arglist = []
    for sim in args.sim:

        # Get config and simulation files
        config = simfunctions.sim2cfg(sim)
        files = simfunctions.getSimFiles(sim)
        gcd = simfunctions.getGCD(config)

        # Default parameters
        llhFile = '{}/LLH_table_{}.npy'.format(args.resources, args.bintype)
        outdir = '{}/{}_sim/files'.format(mypaths.llh_dir, config)
        checkdir(outdir + '/')
        if args.test:
            args.n = 2

        # List of existing files to possibly check against
        existing_files = glob.glob('%s/SimLLH_%s_%s_*.hdf5' %
                                  (outdir, sim, args.bintype))
        existing_files.sort()

        # Split into batches
        batches = [files[i:i + args.n] for i in range(0, len(files), args.n)]
        if args.test:
            batches = batches[:2]

        for bi, batch in enumerate(batches):

            # Name outfile
            start = re.split('\.', batch[0])[-3]
            end = re.split('\.', batch[-1])[-3]
            out = '%s/SimLLH_%s_%s' % (outdir, sim, args.bintype)
            out += '_part%s-%s.hdf5' % (start, end)

            if args.missing:
                if out in existing_files:
                    continue

            batch.insert(0, gcd)
            batch = ' '.join(batch)

            if args.bintype == 'MC':
                arg = '--files {} -c {} -o {}'.format(batch, config, out)
            elif args.bintype == 'lap':
                arg = '--files {} -c {} -o {}'.format(batch, config, out)
            elif args.bintype == 'extras':
                arg = '--files {} -c {} -o {}'.format(batch, config, out)
            else:
                if args.cpp:
                    cmd += ' -cpp'
                    out = out.replace('.hdf5', '_cpp.hdf5')
                arg = '--files {} -c {} -o {}'.format(batch, config, out)
                arg += ' --llhFile {}'.format(llhFile)

            arglist.append(arg)

    # Submit jobs
    py_submit(cmd, arglist, mypaths.llh_dir+'/condor',
              test=args.test, jobID=jobID)
