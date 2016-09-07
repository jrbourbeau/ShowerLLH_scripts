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


def get_counttables_argdict(**args):

    if args['test']:
        args['n'] = 1

    counttables_argdict = {}
    for sim in args['sim']:
        # Build arglist for condor submission
        counttables_arglist = []

        # Build fileList
        config = simfunctions.sim2cfg(sim)
        files = simfunctions.getSimFiles(sim)
        gcd = simfunctions.getGCD(config)
        # Split into batches
        batches = [files[i:i + args['n']]
                   for i in range(0, len(files), args['n'])]

        if args['test']:
            batches = batches[:1]

        for bi, batch in enumerate(batches):

            start = re.split('\.', batch[0])[-3]
            end = re.split('\.', batch[-1])[-3]
            outfile = '{}/counttable_{}_{}'.format(
                outdir, sim, args['bintype'])
            outfile += '_part' + start + '-' + end + '.npy'

            batch.insert(0, gcd)
            batch = ' '.join(batch)

            counttables_arglist += ['-f {} -b {} -o {}'.format(
                batch, args['bintype'], outfile)]

        # Assign the arglist for this sim to the argdict
        counttables_argdict[sim] = counttables_arglist
    return counttables_argdict


def get_merge_argdict(**args):

    # Build arglist for condor submission
    merge_argdict = {}
    for sim in args['sim']:
        merge_args = '-s {} -b {}'.format(sim, args['bintype'])
        merge_args += ' --resources {}'.format(args['resources'])
        if args['overwrite']:
            merge_args += ' --overwrite'
        if args['remove']:
            merge_args += ' --remove'
        merge_argdict[sim] = merge_args

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


if __name__ == '__main__':

    # Setup global path names
    mypaths = paths.Paths()
    sim_output = simfunctions.getSimOutput()
    default_sim_list = ['7006', '7579', '7241', '7263', '7791',
                        '7242', '7262', '7851', '7007', '7784']

    p = argparse.ArgumentParser(
        description='Makes binned histograms for use with ShowerLLH',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=sim_output)
    p.add_argument('--resources', dest='resources',
                   default=mypaths.llh_dir + '/resources',
                   help='Path to ShowerLLH resources directory')
    p.add_argument('-s', '--sim', dest='sim', nargs='*',
                   default=default_sim_list,
                   help='Simulation dataset to run over')
    p.add_argument('-n', dest='n', type=int, default=75,
                   help='Number for files to run per submission batch')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='logdist',
                   choices=['standard', 'nozenith', 'logdist', 'nosnow'],
                   help='Option for a variety of preset bin values')
    p.add_argument('--nomerge', dest='nomerge', action='store_true',
                   default=False,
                   help='Option to not merge counttables parts files')
    p.add_argument('--nonormalize', dest='nonormalize', action='store_true',
                   default=False,
                   help='Option to not normalize counttables files to LLH tables')
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

    # Default parameters
    outdir = '{}/counttables'.format(args.resources)
    checkdir(outdir + '/')

    # Set up jobID for multiple submissions
    jobID = 'ShowerLLH_makeLLHtables_{}'.format(args.bintype)
    jobID += time.strftime('_%Y%m%d')
    othersubmits = glob.glob(
        '{}/condor/submit_scripts/{}_??.submit'.format(mypaths.llh_dir, jobID))
    jobID += '_{:02d}'.format(len(othersubmits) + 1)

    cwd = os.getcwd()
    # Set up count tables condor script and arguments
    counttables_cmd = '{}/make_tables/MakeHist.py'.format(cwd)
    counttables_argdict = get_counttables_argdict(**opts)
    counttables_condor_script = '{}/condor/submit_scripts/counttables_condor_script.submit'.format(
        mypaths.llh_dir)
    make_submit_script(counttables_cmd, jobID,
                       counttables_condor_script, mypaths.llh_dir + '/condor')

    # Set up merge condor script and arguments
    if not args.nomerge:
        merge_cmd = '{}/make_tables/merger.py'.format(cwd)
        merge_argdict = get_merge_argdict(**opts)
        merge_condor_script = '{}/condor/submit_scripts/merge_condor_script.submit'.format(
            mypaths.llh_dir)
        make_submit_script(merge_cmd, jobID, merge_condor_script,
                           mypaths.llh_dir + '/condor')

    # Set up normalize condor script and arguments
    if not args.nonormalize:
        normalize_cmd = '{}/make_tables/normalize.py'.format(cwd)
        normalize_args = '-b {}'.format(args.bintype)
        normalize_args += ' --resources {}'.format(args.resources)
        if args.overwrite:
            normalize_args += ' --overwrite'
        normalize_condor_script = '{}/condor/submit_scripts/normalize_condor_script.submit'.format(
            mypaths.llh_dir)
        make_submit_script(normalize_cmd, jobID, normalize_condor_script,
                           mypaths.llh_dir + '/condor')

    # Set up dag file
    dag_file = '{}/condor/submit_scripts/{}.submit'.format(
        mypaths.llh_dir, jobID)
    checkdir(dag_file)
    with open(dag_file, 'w') as dag:
        for sim in counttables_argdict.keys():
            parent_string = 'Parent '
            sim_arglist = counttables_argdict[sim]
            for i, arg in enumerate(sim_arglist):
                dag.write('JOB ct_{}_p{} '.format(sim, i) +
                          counttables_condor_script + '\n')
                dag.write('VARS ct_{}_p{} '.format(sim, i) +
                          'ARGS="' + arg + '"\n')
                parent_string += 'ct_{}_p{} '.format(sim, i)
            if not args.nomerge:
                dag.write('JOB merge_{} '.format(
                    sim) + merge_condor_script + '\n')
                dag.write('VARS merge_{} '.format(sim) +
                          'ARGS="' + merge_argdict[sim] + '"\n')
                child_string = 'Child merge_{}'.format(sim)
                dag.write(parent_string + child_string + '\n')
        if not args.nonormalize:
            parent_string = 'Parent '
            for sim in counttables_argdict.keys():
                parent_string += 'merge_{} '.format(sim)
            dag.write('JOB normalize_{} '.format(args.bintype) +
                      normalize_condor_script + '\n')
            dag.write('VARS normalize_{} '.format(args.bintype) +
                      'ARGS="' + normalize_args + '"\n')
            child_string = 'Child normalize_{}'.format(args.bintype)
            dag.write(parent_string + child_string + '\n')

    # Submit jobs
    os.system('condor_submit_dag -maxjobs {} {}'.format(args.maxjobs, dag_file))
