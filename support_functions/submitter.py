#!/usr/bin/env python

##============================================================================##
## Writes submission script for cluster
##============================================================================##

import os
import time

def py_submit(executable, argfile, npx4dir, 
              jobID=None, sublines=None, test=False):

    # Option for testing off the cluster
    with open(argfile, 'r') as f:
        argList = f.readlines()
    if test:
        print '(...running as test off the cluster...)'
        for a in argList:
            os.system('{} {}'.format(executable, a.strip()))
        raise SystemExit('Completed testing run...')

    # Moderate number of submitted jobs
    njobs = len(argList)
    if njobs > 500:
        yn = raw_input(
            'About to submit {} jobs. You sure? [y|n]: '.format(njobs))
        if yn != 'y':
            raise SystemExit('Aborting...')

    # Add date information
    if jobID is not None:
        jobID += time.strftime('_%Y%m%d')
        othersubmits = glob.glob('{}/npx4-logs/{}_??.log'.format(npx4dir, jobID))
        jobID += '_{:02d}'.format(len(othersubmits)+1)

    # Condor submission script
    lines = [
        "universe = vanilla\n",
        "getenv = true\n",
        "executable = {}\n".format(executable),
        "arguments = $(Item)\n",
        "log = {}/npx4-logs/{}.log\n".format(npx4dir, jobID),
        "output = {}/npx4-out/{}.out\n".format(npx4dir, jobID),
        "error = {}/npx4-error/{}.error\n".format(npx4dir, jobID),
        "notification = Never\n",
        #"notification = Complete\n",
        #"notify_user = james.bourbeau@icecube.wisc.edu\n",
        "queue 1 Item from {}\n".format(argfile)
    ]

    # Option for additional lines to submission script
    if sublines != None:
        for l in sublines:
            lines.insert(-1, '{}\n'.format(l))

    condor_script = '{}/submit-desc.sub'.format(npx4dir)
    with open(condor_script, 'w') as f:
        f.writelines(lines)

    os.system('condor_submit {}'.format(condor_script))
