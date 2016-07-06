#!/usr/bin/env python

# An attempt at rewriting submit_npx4.sh in python
import os, stat, subprocess, random

import support_functions.myGlobals as my

def py_submit(exelines, jobID=None, sublines=None, test=False):

	# Option for testing off cluster
	if test:
		if len(exelines) > 1:
			raise SystemExit('Multiple exelines not available in test')
		os.system(exelines[0])
		return

	# Setup global variables
	my.setupGlobals(verbose=False)

	if jobID == None:
		randint = random.randint(0,100000)
		jobID = 'npx4-{:05f}'.format(randint)

	outexe = '{}/npx4-execs/{}.sh'.format(my.npx4, jobID)
	condor_script = '{}/submit-desc.sub'.format(my.npx4)

	# Run eval statement as it doesn't run by default when fed to script
	setPath = "echo eval `/cvmfs/icecube.opensciencegrid.org/py2-v1/setup.sh`"
	p = subprocess.Popen(setPath, stdout=subprocess.PIPE, shell=True)
	path, err = p.communicate()
	path = path.strip()

	# Setup execution script
	lines = [
		"#!/bin/bash",
		"date",
		"hostname",
		"",
		#"cd %s" % os.getcwd(),
		#"eval `/cvmfs/icecube.opensciencegrid.org/setup.sh`",
		# "{}".format(path),
		""
	]
	lines += exelines
	lines += ["date"]
	lines = [l + '\n' for l in lines]

	#print(lines)
	with open(outexe, 'w') as f:
		f.writelines(lines)

	# Make file executable
	st = os.stat(outexe)
	os.chmod(outexe, st.st_mode | stat.S_IEXEC)

	# Condor submission script
	lines = [
		"Universe = vanilla\n",
		"Executable = {}/npx4-execs/{}.sh\n".format(my.npx4, jobID),
		"Log = {}/npx4-logs/{}.log\n".format(my.npx4, jobID),
		"Output = {}/npx4-out/{}.out\n".format(my.npx4, jobID),
		"Error = {}/npx4-error/{}.error\n".format(my.npx4, jobID),
		"Notification = Never\n",
		#"Notification = Complete\n",
		#"notify_user = james.bourbeau@icecube.wisc.edu\n",
        "getenv = True\n",
		"Queue\n"
	]

	# Option for additional lines to submission script
	if sublines != None:
		for l in sublines:
			lines.insert(-1, '%s\n' % l)

	with open(condor_script, 'w') as f:
		f.writelines(lines)

	os.system('condor_submit %s' % condor_script)
