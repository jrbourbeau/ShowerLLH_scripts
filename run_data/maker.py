#!/usr/bin/env python

import os
import argparse
import glob

import support_functions.paths as paths
import support_functions.dataFunctions as df
import support_functions.GoodRunList as grl
import support_functions.simFunctions as simFunctions
from support_functions.dag_submitter import py_submit
# from support_functions.submit_npx4 import py_submit
from support_functions.checkdir import checkdir

if __name__ == "__main__":

    # Setup global path names
    mypaths = paths.Paths()

    p = argparse.ArgumentParser(
        description='Mass runs MakeShowerLLH.py on cluster')
    p.add_argument('--resources', dest='resources',
                   default=mypaths.llh_dir + '/resources',
                   help='Path to ShowerLLH resources directory')
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
    LLH_file = '{}/LLH_table_{}.npy'.format(args.resources, args.bintype)
    outdir = '{}/{}_data/files'.format(mypaths.llh_dir, args.config)
    checkdir(outdir + '/')
    outp = "${_CONDOR_SCRATCH_DIR}/simple-dst"
    if not args.n:
        if args.config == 'IT59':
            args.n = 1
        if args.config in ['IT73', 'IT81-2011']:
            args.n = 20
        if args.config in ['IT81-2012']:  # some jobs held, lower this
            args.n = 80
        if args.config in ['IT81-2013', 'IT81-2014', 'IT81-2015']:
            args.n = 40
        if args.test and args.config != 'IT59':
            args.n = 2

    g = grl.GoodRunList(config=args.config)
    good_date_list = g.get_good_dates()
    date_2_goodrun_num = g.date_to_goodrun_num()
    # goodDates = [i for i in good_date_list if i[:len(args.date)] == args.date]
    good_date_list = [i for i in good_date_list if i[:len(args.date)] == args.date]
    if args.test:
        good_date_list = good_date_list[:2]

    cwd = os.getcwd()
    cmd = '{}/MakeShowerLLH.py'.format(cwd)
    jobID = 'ShowerLLH_{}_{}_data'.format(args.bintype, args.config)
    arglist = []

    gcd = simFunctions.getGCD(args.config)
    for yyyymmdd in good_date_list:

        # Get list of files for the day yyyymmdd
        run_nums = date_2_goodrun_num[yyyymmdd]
        files, gcd_files = df.get_IT_data_files(
            g, args.config, yyyymmdd, gcd=True)
        files.sort()
        gcd_files.sort()
        # List of existing files to possibly check against
        existing_files = glob.glob('{}/DataLLH_{}_{}_*.hdf5'.format(
            outdir, yyyymmdd, args.bintype))
        existing_files.sort()

        # Split each data run taken on yyymmdd into batches
        for run in date_2_goodrun_num[yyyymmdd]:
            run_files = [
                file for file in files if 'Run00{}'.format(run) in file]
            run_gcd_files = [
                file for file in gcd_files if 'Run00{}'.format(run) in file]
            if len(run_gcd_files) > 1:
                SystemError('More than one gcd file for Run {} on {}'.format(
                    run, yyyymmdd))
            batches = [run_files[i:i + args.n]
                       for i in range(0, len(run_files), args.n)]
            if args.test:
                batches = batches[:2]

            for bi, batch in enumerate(batches):

                batch.insert(0, run_gcd_files[0])

                # Name outfile
                out = '{}/DataLLH_{}_{}'.format(outdir, yyyymmdd, args.bintype)
                start = batch[1].split('_')[-2].replace('Part', '')
                end = batch[-1].split('_')[-2].replace('Part', '')
                out += '_part{}-{}.hdf5'.format(start, end)

                # # Check only for missing files
                # if args.missing:
                #     outtest = '%s/%s' % (outdir, os.path.basename(out))
                #     if outtest in existing_files:
                #         continue

                arglist += ['-c {} -o {} --llhFile {} --files {}'.format(
                    args.config,
                    out,
                    LLH_file,
                    ' '.join(batch))]
    if args.test:
        arglist = arglist[:2]

    # Submit jobs
    py_submit(cmd, arglist, mypaths.llh_dir +
              '/condor', test=args.test, jobID=jobID)
