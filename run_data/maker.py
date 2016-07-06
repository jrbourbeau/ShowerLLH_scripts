#!/usr/bin/env python

import os
import argparse
import glob

import support_functions.myGlobals as my
import support_functions.dataFunctions as df
import support_functions.GoodRunList as grl
import support_functions.simFunctions as simFunctions
from support_functions.submitter import py_submit
# from support_functions.submit_npx4 import py_submit
from support_functions.checkdir import checkdir

if __name__ == "__main__":

    # Setup global path names
    my.setupGlobals(verbose=False)

    p = argparse.ArgumentParser(
        description='Mass runs MakeShowerLLH.py on cluster')
    p.add_argument('-c', '--config', dest='config', default='IT73',
                   help='Detector configuration to run over')
    p.add_argument('-d', '--date', dest='date',
                   help='Date to run over (yyyy[mmdd])')
    p.add_argument('-n', '--n', dest='n', type=int,
                   help='Number of files to run per batch')
    p.add_argument('--old', dest='old',
                   default=False, action='store_true',
                   help='Run in old Python implementation')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='standard',
                   # choices=['standard','nozenith','logdist','lap','extras'],
                   help='Choose bin config for llh tables OR other desired info')
    p.add_argument('--missing', dest='missing',
                   default=False, action='store_true',
                   help='Option to only submit files with missing file names')
    p.add_argument('--test', dest='test', action='store_true',
                   default=False,
                   help='Option for running test off cluster')
    args = p.parse_args()

    # Default parameters
    it_geo = df.it_geo(args.config)
    LLH_file = '{}/LLHTables_{}.npy'.format(my.llh_resource, args.bintype)
    outDir = '{}/{}_data/files'.format(my.llh_data, args.config)
    checkdir(outDir)
    outp = "${_CONDOR_SCRATCH_DIR}/simple-dst"
    if not args.n:
        if args.config == 'IT59':
            args.n = 1
        if args.config in ['IT73', 'IT81']:
            args.n = 20
        if args.config in ['IT81-II']:  # some jobs held, lower this
            args.n = 80
        if args.config in ['IT81-III', 'IT81-IV']:
            args.n = 40
        if args.test and args.config != 'IT59':
            args.n = 2

    g = grl.GoodRunList(config=args.config)
    good_date_list = g.get_good_dates()
    date_2_goodrun_num = g.date_to_goodrun_num()
    # goodDates = [i for i in good_date_list if i[:len(args.date)] == args.date]
    if args.test:
        good_date_list = good_date_list[:2]
        # goodDates = goodDates[:2]

    cwd = os.getcwd()
    cmd = '{}/MakeShowerLLH.py'.format(cwd)
    jobID = 'showerLLH_data'
    argList = []

    gcd = simFunctions.getGCD(args.config)
    for yyyymmdd in good_date_list:

        # # Get list of files
        # files, gcdFiles = df.getDataFiles(args.config, yyyymmdd)
        # runList = list(set([df.getRun(f) for f in files]))
        run_nums = date_2_goodrun_num[yyyymmdd]
        # files, gcdFiles = df.get_data_files(args.config, yyyymmdd, run_nums, gcd=True)
        files, gcdFiles = df.get_IT_data_files(g, args.config, yyyymmdd, gcd=True)
        # gcdFiles = [gcd for gcd in gcdFiles if df.getRun(gcd) in run_nums]
        # gcdFiles = [gcd for gcd in gcdFiles if df.getRun(gcd) in runList]
        # files.sort()
        # files = df.getDataFiles(args.config, yyyymmdd)
        # print('files = {}'.format(files))
        
        # List of existing files to possibly check against
        existingFiles = glob.glob('%s/DataLLH_%s_%s_*.hdf5' %
                                  (outDir, yyyymmdd, args.bintype))
        existingFiles.sort()

        # Split into batches
        batches = [files[i:i + args.n] for i in range(0, len(files), args.n)]
        if args.test:
            batches = batches[:2]

        for bi, batch in enumerate(batches):

            # Place GCD files
            gcds, idxs = [], []
            run_prev = '0'
            for i, file in enumerate(batch):
                run = df.getRun(file)
                if run != run_prev:
                    gcds += [gcd for gcd in gcdFiles if run in gcd]
                    idxs += [i]
                    run_prev = run
            for j, idx in enumerate(idxs[::-1]):
                batch.insert(idx, gcds[::-1][j])

            # Name outfile
            out = '%s/DataLLH_%s_%s_new' % (outp, yyyymmdd, args.bintype)
            if args.test:
                out = '%s/DataLLH_%s_%s' % (outDir, yyyymmdd, args.bintype)
            for file in [batch[1], batch[-1]]:
                run = df.getRun(file)
                part = df.getSubRun(file)
                out += '_%s_%s' % (run, part)
            out += '.hdf5'

            # Check only for missing files
            if args.missing:
                outtest = '%s/%s' % (outDir, os.path.basename(out))
                if outtest in existingFiles:
                    continue

            argList += ['-c {} -o {} --llhFile {} --files {}'.format(
                                                                     args.config,
                                                                     out,
                                                                     LLH_file,
                                                                     ' '.join(batch))]
            # cmd += ' -c %s -o %s' % (args.config, out)
            # cmd += ' --llhFile {}'.format(LLH_file)
            # if not args.test:
            #     lfiles = ['%s/%s' % (outp, os.path.basename(f)) for f in batch]
            #     lfiles = ' '.join(lfiles)       asdf
            #     batch = ' '.join(batch)
            #     cmd += ' --files %s' % (lfiles)
            #     ex = [
            #         'mkdir -p %s' % outp,           # Make directory for output
            #         'cp %s %s' % (batch, outp),      # Copy files for local I/O
            #         '%s %s' % (my.env, cmd),        # Process files
            #         'rm -f %s' % lfiles,            # Remove copied i3 files
            #         'mv %s %s' % (out, outDir)      # Move output file
            #     ]
            # else:
            #     batch = ' '.join(batch)
            #     cmd += ' --files %s' % batch
            #     ex = [cmd]

            # exList += [ex]
            # jobIDs += ['showerllh_%s_%s_%i' % (args.config, yyyymmdd, bi)]

    if args.test:
        argList = argList[:2]
    
    # Write arguments to file
    argFile = '{}/arguments/{}_arguments.txt'.format(my.npx4, jobID)
    with open(argFile, 'w') as f:
        for a in argList:
            f.write('{}\n'.format(a))

    # Submit jobs
    print('Submitting {} batches...'.format(len(argList)))
    py_submit(cmd, argFile, my.npx4, test=args.test, jobID=jobID)
