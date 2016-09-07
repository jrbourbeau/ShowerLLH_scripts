#!/usr/bin/env python

import glob
import re
import os
import argparse
import time
import getpass

import support_functions.paths as paths
import support_functions.simfunctions as simfunctions
from support_functions.dag_submitter import py_submit
from support_functions.checkdir import checkdir

def get_ShowerLLH_sim_argdict(llh_dir, **args):

    argdict = dict.fromkeys(args['sim'])
    for sim in args['sim']:

        arglist = []

        # Get config and simulation files
        config = simfunctions.sim2cfg(sim)
        files = simfunctions.getSimFiles(sim)
        gcd = simfunctions.getGCD(config)

        # Default parameters
        llhFile = '{}/LLH_table_{}.npy'.format(args['resources'], args['bintype'])
        outdir = '{}/{}_sim/files'.format(llh_dir, config)
        checkdir(outdir + '/')
        if args['test']:
            args['n'] = 2

        # List of existing files to possibly check against
        existing_files = glob.glob('{}/SimLLH_{}_{}_*.hdf5'.format(
            outdir, sim, args['bintype']))
        existing_files.sort()

        # Split into batches
        batches = [files[i:i + args['n']] for i in range(0, len(files), args['n'])]
        if args['test']:
            batches = batches[:2]

        for bi, batch in enumerate(batches):

            # Name outfile
            start = re.split('\.', batch[0])[-3]
            end = re.split('\.', batch[-1])[-3]
            out = '%s/SimLLH_%s_%s' % (outdir, sim, args['bintype'])
            out += '_part%s-%s.hdf5' % (start, end)

            if args['missing']:
                if out in existing_files:
                    continue

            batch.insert(0, gcd)
            batch = ' '.join(batch)

            if args['bintype'] == 'MC':
                arg = '--files {} -c {} -o {}'.format(batch, config, out)
            elif args['bintype'] == 'lap':
                arg = '--files {} -c {} -o {}'.format(batch, config, out)
            elif args['bintype'] == 'extras':
                arg = '--files {} -c {} -o {}'.format(batch, config, out)
            else:
                if args['cpp']:
                    cmd += ' -cpp'
                    out = out.replace('.hdf5', '_cpp.hdf5')
                arg = '--files {} -c {} -o {}'.format(batch, config, out)
                arg += ' --llhFile {}'.format(llhFile)

            arglist.append(arg)

        argdict[sim] = arglist

    return argdict

def get_merge_argdict(**args):

    # Build arglist for condor submission
    merge_argdict = dict.fromkeys(args['sim'])
    for sim in args['sim']:
        merge_args = '-s {} -b {}'.format(sim, args['bintype'])
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
             "log = /scratch/{}/logs/{}.log\n".format(getpass.getuser(), jobID),
             "output = {}/outs/{}.out\n".format(condordir, jobID),
             "error = {}/errors/{}.error\n".format(condordir, jobID),
             "notification = Never\n",
             # "+AccountingGroup=\"long.$ENV(USER)\"\n",
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

if __name__ == "__main__":

    # Setup global path names
    mypaths = paths.Paths()
    simOutput = simfunctions.getSimOutput()
    default_sim_list = ['7006', '7579', '7241', '7263', '7791',
                        '7242', '7262', '7851', '7007', '7784']

    p = argparse.ArgumentParser(
        description='Mass runs MakeLLHFiles.py on cluster',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=simOutput)
    p.add_argument('--resources', dest='resources',
                   default=mypaths.llh_dir + '/resources',
                   help='Path to ShowerLLH resources directory')
    p.add_argument('-s', '--sim', dest='sim', nargs='*',
                   choices=default_sim_list,
                   default=default_sim_list,
                   help='Simulation to run over')
    p.add_argument('-n', '--n', dest='n', type=int,
                   default=100,
                   help='Number of files to run per batch')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='logdist',
                   help='Choose bin config for llh tables OR other desired info',
                   choices=['standard', 'nozenith', 'logdist', 'nosnow', 'MC', 'lap', 'extras'])
    p.add_argument('--missing', dest='missing',
                   default=False, action='store_true',
                   help='Option to only submit files with missing file names')
    p.add_argument('--test', dest='test', action='store_true',
                   default=False,
                   help='Option for running test off cluster')
    p.add_argument('--cpp', dest='cpp',
                   default=False, action='store_true',
                   help='Run in C++ (static) mode')
    p.add_argument('--maxjobs', dest='maxjobs', type=int,
                   default=3000,
                   help='Maximum number of jobs to run at a given time.')
    p.add_argument('--overwrite', dest='overwrite',
                   default=False, action='store_true',
                   help='Overwrite existing merged files')
    p.add_argument('--remove', dest='remove',
                   default=False, action='store_true',
                   help='Remove unmerged hdf5 files')
    args = p.parse_args()

    cwd = os.getcwd()
    ShowerLLH_sim_jobID = 'ShowerLLH_sim_{}'.format(args.bintype)
    ShowerLLH_sim_jobID = getjobID(ShowerLLH_sim_jobID, mypaths.llh_dir)
    if args.bintype == 'MC':
        ShowerLLH_sim_cmd = '{}/run_sim/MakeMC.py'.format(cwd)
    elif args.bintype == 'lap':
        ShowerLLH_sim_cmd = '{}/run_sim/MakeLaputop.py'.format(cwd)
    elif args.bintype == 'extras':
        ShowerLLH_sim_cmd = '{}/run_sim/MakeExtras.py'.format(cwd)
    else:
        ShowerLLH_sim_cmd = '{}/run_sim/MakeShowerLLH.py'.format(cwd)
    ShowerLLH_sim_argdict = get_ShowerLLH_sim_argdict(
        mypaths.llh_dir, **vars(args))
    ShowerLLH_sim_condor_script = '{}/condor/submit_scripts/{}.submit'.format(
        mypaths.llh_dir, ShowerLLH_sim_jobID)
    make_submit_script(ShowerLLH_sim_cmd, ShowerLLH_sim_jobID,
                       ShowerLLH_sim_condor_script, mypaths.llh_dir + '/condor')

    merge_jobID = 'ShowerLLH_merge_{}'.format(args.bintype)
    merge_jobID = getjobID(merge_jobID, mypaths.llh_dir)
    merge_cmd = '{}/run_sim/merge.py'.format(cwd)
    merge_argdict = get_merge_argdict(**vars(args))
    merge_condor_script = '{}/condor/submit_scripts/{}.submit'.format(
        mypaths.llh_dir, merge_jobID)
    make_submit_script(merge_cmd, merge_jobID, merge_condor_script,
                                mypaths.llh_dir + '/condor')

    # Set up dag file
    jobID = 'reconstruct_sim_{}'.format(args.bintype)
    jobID = getjobID(jobID, mypaths.llh_dir)
    dag_file = '{}/condor/submit_scripts/{}.submit'.format(
        mypaths.llh_dir, jobID)
    checkdir(dag_file)
    with open(dag_file, 'w') as dag:
        for sim in ShowerLLH_sim_argdict.keys():
            parent_string = 'Parent '
            for i, arg in enumerate(ShowerLLH_sim_argdict[sim]):
                dag.write('JOB LLHsim_{}_p{} '.format(sim, i) +
                          ShowerLLH_sim_condor_script + '\n')
                dag.write('VARS LLHsim_{}_p{} '.format(sim, i) +
                          'ARGS="' + arg + '"\n')
                parent_string += 'LLHsim_{}_p{} '.format(sim, i)
            dag.write('JOB merge_{} '.format(
                sim) + merge_condor_script + '\n')
            dag.write('VARS merge_{} '.format(sim) +
                        'ARGS="' + merge_argdict[sim] + '"\n')
            child_string = 'Child merge_{}'.format(sim)
            dag.write(parent_string + child_string + '\n')

    # Submit jobs
    os.system('condor_submit_dag -maxjobs {} {}'.format(args.maxjobs, dag_file))
