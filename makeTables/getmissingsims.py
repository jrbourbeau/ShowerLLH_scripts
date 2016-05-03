#!/usr/bin/env python

#=========================================================================
# File Name     : checker.py
# Description   :
# Creation Date : 05-02-2016
# Last Modified : Mon 02 May 2016 10:44:03 AM CDT
# Created By    : James Bourbeau
#=========================================================================

import os, glob
import numpy as np

if __name__ == "__main__":

    filelist = glob.glob('/data/user/jbourbeau/showerllh/resources/CountTables/*.npy')
    filelist = [os.path.basename(f).replace('.npy','') for f in filelist if 'Part' not in f]
    simsused = {'standard':[], 'nozenith':[], 'logdist':[]}
    simlist = [7006, 7579, 7241, 7263, 7791, 7242, 7262, 7851, 7007, 7784]
    for f in filelist:
        sim = f.split('_')[1]
        bintype = f.split('_')[2]
        simsused[bintype].append(int(sim))
    # print('simsused = {}'.format(simsused))

    missingsims = {'standard':[], 'nozenith':[], 'logdist':[]}
    for key in missingsims:
        sims = simsused[key]
        missingsims[key] = list(set(simlist)-set(sims))
    print('missingsims = {}'.format(missingsims))
