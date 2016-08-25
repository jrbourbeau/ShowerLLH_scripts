#!/usr/bin/env python

import argparse
import glob
import os
import re
import numpy as np
import getpass
import time

import support_functions.paths as paths
from support_functions.checkdir import checkdir
import support_functions.simfunctions as simfunctions
import support_functions.dataFunctions as df
import support_functions.GoodRunList as grl


def get_ShowerLLH_data_argdict(llh_dir, *good_date_list, **args):

    argdict = {}

    # Default parameters
    outdir = '{}/{}_data/files'.format(llh_dir, args['config'])
    checkdir(outdir + '/')
    it_geo = df.it_geo(args['config'])
    LLH_file = '{}/LLH_table_{}.npy'.format(args['resources'], args['config'])
    if not args['n']:
        if args['config'] == 'IT59':
            args['n'] = 1
        if args['config'] in ['IT73', 'IT81-2011']:
            args['n'] = 20
        if args['config'] in ['IT81-2012']:  # some jobs held, lower this
            args['n'] = 80
        if args['config'] in ['IT81-2013', 'IT81-2014', 'IT81-2015']:
            args['n'] = 40
        if args.test and args['config'] != 'IT59':
            args['n'] = 2
    gcd = simfunctions.getGCD(args['config'])

    for yyyymmdd in good_date_list:
        arglist = []

        # Get list of files for the day yyyymmdd
        run_nums = date_2_goodrun_num[yyyymmdd]
        files, gcd_files = df.get_IT_data_files(
            g, args['config'], yyyymmdd, gcd=True)
        files.sort()
        gcd_files.sort()
        # List of existing files to possibly check against
        existing_files = glob.glob('{}/DataLLH_{}_{}_*.hdf5'.format(
            outdir, yyyymmdd, args['bintype']))
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
            batches = [run_files[i:i + args['n']]
                       for i in range(0, len(run_files), args['n'])]
            if args['test']:
                batches = batches[:2]

            for bi, batch in enumerate(batches):

                batch.insert(0, run_gcd_files[0])

                # Name outfile
                out = '{}/DataLLH_{}_{}'.format(outdir, yyyymmdd, args['bintype'])
                start = batch[1].split('_')[-2].replace('Part', '')
                end = batch[-1].split('_')[-2].replace('Part', '')
                out += '_part{}-{}.hdf5'.format(start, end)

                arglist += ['-c {} -o {} --llhFile {} --files {}'.format(
                    args['config'],
                    out,
                    LLH_file,
                    ' '.join(batch))]

        if args['test']:
            arglist = arglist[:2]
        argdict[yyyymmdd] = arglist


    return argdict


def get_merge_argdict(llh_dir, *good_date_list, **args):

    # Build arglist for condor submission
    merge_argdict = {}

    prefix = '{}/{}_data/files'.format(llh_dir, args['config'])
    # masterlist = glob.glob(
    #     '{}/DataLLH_????????_{}_part*.hdf5'.format(prefix, args['bintype']))
    # masterlist.sort()

    # dates = [os.path.basename(f).split('_')[1] for f in masterlist]
    # dates = np.unique(dates)
    # if args['date']:
    #     dates = [yyyymmdd for yyyymmdd in dates if args['date'] in yyyymmdd]

    for date in good_date_list:
        date_variables = {}

        outfile = '{}/DataLLH_{}_{}.hdf5'.format(prefix, date, args['bintype'])
        # Check if file exists
        if os.path.isfile(outfile) and not args['overwrite']:
            print('Outfile {} already exists. Skipping...'.format(outfile))
            continue
        if os.path.isfile(outfile) and args['overwrite']:
            print('Outfile {} already exists. Removing...'.format(outfile))
            os.remove(outfile)

        # Build list of files and destination
        files = glob.glob('{}/DataLLH_{}_{}_part*.hdf5'.format(prefix, date, args['bintype']))
        files.sort()
        infiles = ' '.join(files)

        date_variables['outfile'] = outfile
        date_variables['infiles'] = infiles
        merge_argdict[date] = date_variables

    return merge_argdict


def make_submit_script(executable, jobID, script_path, condordir):

    checkdir(script_path)

    lines = ["universe = vanilla\n",
             "getenv = true\n",
             "executable = {}\n".format(executable),
             "arguments = $(ARGS)\n",
             "log = {}/logs/{}.log\n".format(condordir, jobID),
             # "log = /scratch/{}/logs/{}.log\n".format(getpass.getuser(), jobID),
             "output = {}/outs/{}.out\n".format(condordir, jobID),
             "error = {}/errors/{}.error\n".format(condordir, jobID),
             "notification = Never\n",
             "+AccountingGroup=\"long.$ENV(USER)\"\n",
             "queue \n"]

    condor_script = script_path
    with open(condor_script, 'w') as f:
        f.writelines(lines)

    return


def make_merge_submit_script(executable, jobID, script_path, condordir):

    checkdir(script_path)

    lines = ["universe = vanilla\n",
             "getenv = true\n",
             "executable = {}\n".format(executable),
             "arguments = $(CMD) $(OUTFILE) $(INFILES)\n",
             "log = {}/logs/{}.log\n".format(condordir, jobID),
             "output = {}/outs/{}.out\n".format(condordir, jobID),
             "error = {}/errors/{}.error\n".format(condordir, jobID),
             "notification = Never\n",
             "+AccountingGroup=\"long.$ENV(USER)\"\n",
             "queue \n"]

    condor_script = script_path
    with open(condor_script, 'w') as f:
        f.writelines(lines)

    return

def getjobID(jobID, llh_dir):
    jobID += time.strftime('_%Y%m%d')
    othersubmits = glob.glob(
        '{}/condor/submit_scripts/{}_??.submit'.format(llh_dir, jobID))
    jobID += '_{:02d}'.format(len(othersubmits) + 1)
    return jobID

if __name__ == '__main__':

    # Setup global path names
    mypaths = paths.Paths()

    p = argparse.ArgumentParser(
        description='Mass runs MakeShowerLLH.py on cluster')
    p.add_argument('--resources', dest='resources',
                   default=mypaths.llh_dir + '/resources',
                   help='Path to ShowerLLH resources directory')
    p.add_argument('-c', '--config', dest='config', default='IT73',
                   help='Detector configuration to run over')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='logdist',
                   choices=['standard', 'nozenith', 'logdist', 'nosnow'],
                   help='Option for a variety of preset bin values')
    p.add_argument('-d', '--date', dest='date',
                   help='Date to run over (yyyy[mmdd])')
    p.add_argument('-n', dest='n', type=int, default=20,
                   help='Number for files to run per submission batch')
    p.add_argument('--nomerge', dest='nomerge', action='store_true',
                   default=False,
                   help='Option to not merge counttables parts files')
    p.add_argument('--overwrite', action='store_true', dest='overwrite',
                   default=False, help='Overwrite existing merged files')
    p.add_argument('--remove', dest='remove',
                   default=False, action='store_true',
                   help='Remove unmerged counttables .npy files')
    p.add_argument('--test', dest='test', action='store_true',
                   default=False,
                   help='Option for running off cluster to test')
    p.add_argument('--maxjobs', dest='maxjobs', type=int, default=3000,
                   help='Maximum number of jobs to have running at any given time')
    args = p.parse_args()
    opts = vars(args)

    g = grl.GoodRunList(config=args.config)
    good_date_list = g.get_good_dates()
    date_2_goodrun_num = g.date_to_goodrun_num()
    if args.date:
        good_date_list = [i for i in good_date_list if args.date in i]
    if args.test:
        good_date_list = good_date_list[:1]

    cwd = os.getcwd()
    # Set up MakeShowerLLH.py condor script and arguments
    ShowerLLH_data_jobID = 'MakeShowerLLH_data_{}_{}'.format(args.config, args.bintype)
    if args.date:
        ShowerLLH_data_jobID += '_{}'.format(date)
    ShowerLLH_data_jobID = getjobID(ShowerLLH_data_jobID, mypaths.llh_dir)
    ShowerLLH_data_cmd = '{}/MakeShowerLLH.py'.format(cwd)
    ShowerLLH_data_argdict = get_ShowerLLH_data_argdict(mypaths.llh_dir, *good_date_list, **opts)
    ShowerLLH_data_condor_script = '{}/condor/submit_scripts/MakeShowerLLH_data_condor_script.submit'.format(
        mypaths.llh_dir)
    make_submit_script(ShowerLLH_data_cmd, ShowerLLH_data_jobID,
                       ShowerLLH_data_condor_script, mypaths.llh_dir + '/condor')

    # Set up merge condor script and arguments
    if not args.nomerge:
        merge_jobID = 'ShowerLLH_datamerge_{}_{}'.format(args.config, args.bintype)
        if args.date:
            merge_jobID += '_{}'.format(args.date)
        merge_jobID = getjobID(merge_jobID, mypaths.llh_dir)
        merge_cmd = '{}/run_data/merge.sh'.format(cwd)
        merge_argdict = get_merge_argdict(mypaths.llh_dir, *good_date_list, **opts)
        merge_condor_script = '{}/condor/submit_scripts/ShowerLLH_datamerge_condor_script.submit'.format(
            mypaths.llh_dir)
        make_merge_submit_script(merge_cmd, merge_jobID, merge_condor_script,
                           mypaths.llh_dir + '/condor')

    # Set up dag file
    jobID = 'ShowerLLH_data_{}_{}'.format(args.config, args.bintype)
    if args.date:
        jobID += '_{}'.format(date)
    jobID = getjobID(jobID, mypaths.llh_dir)
    dag_file = '{}/condor/submit_scripts/{}.submit'.format(
        mypaths.llh_dir, jobID)
    checkdir(dag_file)
    with open(dag_file, 'w') as dag:
        for yyyymmdd in ShowerLLH_data_argdict.keys():
            parent_string = 'Parent '
            for i, arg in enumerate(ShowerLLH_data_argdict[yyyymmdd]):
                dag.write('JOB LLHdata_{}_p{} '.format(yyyymmdd, i) +
                            ShowerLLH_data_condor_script + '\n')
                dag.write('VARS LLHdata_{}_p{} '.format(yyyymmdd, i) +
                            'ARGS="' + arg + '"\n')
                parent_string += 'LLHdata_{}_p{} '.format(yyyymmdd, i)
            if not args.nomerge:
                hdf5_merge = '{}/build/hdfwriter/resources/scripts/merge.py'.format(mypaths.metaproject)
                dag.write('JOB merge_{} '.format(
                    yyyymmdd) + merge_condor_script + '\n')
                dag.write('VARS merge_{} '.format(yyyymmdd) +
                          'VARS merge_{} '.format(yyyymmdd) + 'CMD="' + hdf5_merge + '"\n' +
                          'VARS merge_{} '.format(yyyymmdd) + 'OUTFILE="' + merge_argdict[yyyymmdd]['outfile'] + '"\n' +
                          'VARS merge_{} '.format(yyyymmdd) + 'INFILES="' + merge_argdict[yyyymmdd]['infiles'] + '"\n')
                child_string = 'Child merge_{}'.format(yyyymmdd)
                dag.write(parent_string + child_string + '\n')


    # # Submit jobs
    # os.system('condor_submit_dag -maxjobs {} {}'.format(args.maxjobs, dag_file))
