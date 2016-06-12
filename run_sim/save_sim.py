#!/usr/bin/env python

import sys
import argparse
import time
import tables
import glob
import re
import numpy as np
from collections import defaultdict

import support_functions.myGlobals as my
import support_functions.simFunctions as simFunctions


def eventID(branch):

    run = branch.col('Run').astype('S')
    evt = branch.col('Event').astype('S')
    sub = branch.col('SubEvent').astype('S')
    eventID = ['%s_%s_%s' % (run[i], evt[i], sub[i]) for i in range(len(run))]
    return eventID


def saveLLH(fileList, outFile):

    d = defaultdict(list)
    rDict = {'proton': 'p', 'helium': 'h', 'oxygen': 'o', 'iron': 'f'}

    t0 = time.time()
    for file in fileList:

        print('Working on {}'.format(file))
        basename = re.split('/', file)[-1]
        sim = re.split('_|\.', basename)[1]
        t = tables.openFile(file)
        q = {}

        # Get reconstructed compositions from list of children in file
        children = []
        for node in t.walk_nodes('/'):
            try:
                children += [node.name]
            except tables.NoSuchNodeError:
                continue
        children = list(set(children))
        compList = [n.split('_')[-1] for n in children if 'ShowerLLH_' in n]

        # Get ShowerLLH cuts and info
        rrc = t.root.ShowerLLH_proton.col('exists').astype('bool')
        for comp in compList:
            r = rDict[comp]
            for value in ['x', 'y', 'energy']:
                q[r + 'ML_' +
                    value] = t.getNode('/ShowerLLH_' + comp).col(value)
            q[r + 'LLH'] = t.getNode('/ShowerLLHParams_' + comp).col('maxLLH')

        # Other reconstruction info
        q['eventID'] = np.asarray(eventID(t.root.ShowerLLH_proton))
        for value in ['zenith', 'azimuth']:
            q[value] = t.root.ShowerLLH_proton.col(value)

        # MCPrimary information
        for value in ['x', 'y', 'energy', 'zenith', 'azimuth']:
            q['MC_' + value] = t.root.MCPrimary.col(value)
        q['sim'] = np.array([sim for i in range(len(q['MC_x']))])
        q['comp'] = np.array([simFunctions.sim2comp(s) for s in q['sim']])

        # Append to existing arrays (only keep events where ShowerLLH ran)
        for key in q.keys():
            d[key] += q[key][rrc].tolist()

        t.close()

    # Convert value lists to arrays (faster than using np.append?)
    for key in d.keys():
        d[key] = np.asarray(d[key])

    # Get most likely composition
    rList = [rDict[comp] for comp in compList]
    full_llhs = np.array([d[r + 'LLH'] for r in rList])
    max_llh = np.amax(full_llhs, axis=0)
    d['llh_comp'] = np.array(['' for i in range(len(d['sim']))])
    for r in rList:
        d['llh_comp'][d[r + 'LLH'] == max_llh] = r

    for key in ['x', 'y', 'energy']:
        d['ML_' + key] = np.array([d[r + 'ML_' + key][i]
                                   for i, r in enumerate(d['llh_comp'])])

    # Check for multiple most-likely compositions
    badVals = np.sum(full_llhs == max_llh, axis=0)
    badVals = (badVals - 1).astype('bool')
    d['llh_comp'][badVals] = ''
    for key in ['x', 'y', 'energy']:
        d['ML_' + key][badVals] = np.nan

    print "Time taken:", time.time() - t0
    print "Average time per run:", (time.time() - t0) / len(fileList)

    np.save(outFile, d)


def saveExtras(fileList, outFile, bintype):

    d0 = np.load(outFile)
    d0 = d0.item()
    d = defaultdict(list)

    t0 = time.time()
    for file in fileList:

        print "Working on", file
        t = tables.openFile(file)
        q = {}

        # Get Laputop info
        # for value in ['x', 'y', 'zenith', 'azimuth']:
        #    q['lap_'+value] = t.root.Laputop.col(value)
        # for value in ['s125', 'e_proton', 'e_iron', 'beta']:
        #    q['lap_'+value] = t.root.LaputopParams.col(value)

        # Get extra information
        for key in ['NStations', 'LoudestOnEdge', 'Q1', 'Q2', 'Q3', 'Q4']:
            q[key] = t.getNode('/' + key).col('value')

        t.close()

        # Load ShowerLLH file to get cut
        t = tables.openFile(file.replace('extras', bintype))
        rrc = t.root.ShowerLLH_proton.col('exists').astype('bool')
        t.close()

        # Append to existing arrays (only keep events where ShowerLLH ran)
        for key in q.keys():
            d[key] += q[key][rrc].tolist()

    # Add all new keys to original dictionary
    for key in d.keys():
        d0[key] = np.asarray(d[key])

    print "Time taken:", time.time() - t0
    print "Average time per run:", (time.time() - t0) / len(fileList)

    np.save(outFile, d0)


if __name__ == "__main__":

    # Import global path names
    my.setupShowerLLH(verbose=False)

    p = argparse.ArgumentParser(
        description='Pulls desired info from hdf5 to npy for rapid reading')
    p.add_argument('-c', '--config', dest='config',
                   default='IT73',
                   help='Detector configuration for simulation')
    p.add_argument('-s', '--sim', dest='sim',
                   help='Simulation number to save')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='logdist',
                   help='Desired binning')
    p.add_argument('--prefix', dest='prefix',
            help='Path to sim file to be merged')
    args = p.parse_args()

    if args.prefix:
        prefix = '{}/{}_sim'.format(args.prefix, args.config)
    else:
        prefix = '{}/{}_sim'.format(my.llh_data, args.config)
    if args.sim:
        allfiles = glob.glob(
            '{}/files/SimLLH_{}*.hdf5'.format(prefix, args.sim))
    else:
        allfiles = glob.glob('{}/files/SimLLH_*.hdf5'.format(prefix))
    mergedfiles = [f for f in allfiles if '_part' not in f]
    filelist = [f for f in mergedfiles if args.bintype in f]
    low_energy_sim_list = ['7351', '7483', '7486', '7394']
    filelist = [f for f in filelist if not any(i in f for i in low_energy_sim_list)]
    filelist.sort()
    # print('filelist = {}'.format(filelist))
    # sys.exit()
    extraList = [f.replace(args.bintype, 'extras') for f in filelist]

    if args.sim:
        outFile = '{}/SimPlot_{}_{}.npy'.format(prefix, args.sim, args.bintype)
    else:
        outFile = '{}/SimPlot_{}.npy'.format(prefix, args.bintype)
    if len(filelist) == 0:
        raise SystemError('There are no files that'
                          ' match {} bins for the {} configuration...'.format(args.bintype, args.config))
    saveLLH(filelist, outFile)
    saveExtras(extraList, outFile, args.bintype)
