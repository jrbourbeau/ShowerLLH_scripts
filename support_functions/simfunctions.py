#!/usr/bin/env python

import glob
import os


def getSimDict():

    # Simulation info for various detector configurations and compositions
    s = {}
    s['IT81'] = {'P': ['9166'], 'Fe': ['9165']}
    s['IT73'] = {}
    # Note - need to look into the lowE simulation. Appears to be more.
    s['IT73']['P'] = ['7351', '7006', '7579']
    s['IT73']['He'] = ['7483', '7241', '7263', '7791']
    s['IT73']['O'] = ['7486', '7242', '7262', '7851']
    s['IT73']['Fe'] = ['7394', '7007', '7784']

    return s


def getSimOutput():

    # Custom help output for argparse
    s = getSimDict()
    simOutput = '\nIceTop simulation datasets:\n'
    for config in sorted(s.keys()):
        simOutput += '  %s\n' % config
        for comp in sorted(s[config].keys()):
            simOutput += '  %4s : %s\n' % (comp, s[config][comp])

    return simOutput


def getErange(inverted=False):
    e = {}
    e['low'] = ['7351', '7483', '7486', '7394']
    e['mid'] = ['9166', '9165', '7006', '7007', '7241', '7263', '7242', '7262']
    e['high'] = ['7579', '7791', '7851', '7784']
    if inverted:
        e = {v: k for k in e for v in e[k]}

    return e


def sim2cfg(sim):

    s = getSimDict()
    inverted_dict = {v: k for k in s for k2 in s[k] for v in s[k][k2]}
    return inverted_dict[sim]


def sim2comp(sim, full=False, convert=False):

    s = getSimDict()
    converter = {'P': 'p', 'He': 'h', 'O': 'o', 'Fe': 'f'}
    if convert:
        inverted_dict = {v: converter[k]
                         for k2 in s for k in s[k2] for v in s[k2][k]}
    else:
        inverted_dict = {v: k for k2 in s for k in s[k2] for v in s[k2][k]}
    comp = inverted_dict[sim]
    fullDict = {'P': 'proton', 'He': 'helium', 'O': 'oxygen', 'Fe': 'iron'}
    if full:
        comp = fullDict[comp]
    return comp


def getStreamErrors():

    import paths
    mypaths = paths.Paths()
    errFile = '{}/streamErrors.txt'.format(mypaths.npx4)
    if not os.path.isfile(errFile):
        return []
    with open(errFile, 'r') as f:
        badFiles = f.readlines()
    badFiles = [f.strip() for f in badFiles]
    return badFiles


def getGCD(config):

    gcd = {}
    gcd['IT59'] = '/data/sim/sim-new/downloads/GCD_20_04_10/' + \
        'GeoCalibDetectorStatus_IC59.55040_official.i3.gz'
    gcd['IT73'] = '/data/sim/sim-new/downloads/GCD_31_08_11/' + \
        'GeoCalibDetectorStatus_IC79.55380_L2a.i3.gz'
    gcd['IT81'] = '/data/sim/sim-new/downloads/GCD/' + \
        'GeoCalibDetectorStatus_IC86.55697_V2.i3.gz'

    return gcd[config]


def getSimFiles(sim):

    config = sim2cfg(sim)
    if config == 'IT73':
        prefix = '/data/sim/IceTop/2010/filtered/level2a/CORSIKA-ice-top/'
        files = glob.glob(prefix + sim + '/*/Level2a_*.i3.bz2')
    if config == 'IT81':
        prefix = '/data/sim/IceTop/2011/filtered/CORSIKA-ice-top/level2/'
        files = glob.glob(prefix + sim + '/*/Level2_*.i3.bz2')

    # Remove files with stream errors
    badFiles = getStreamErrors()
    files = [f for f in files if f not in badFiles]

    return sorted(files)


def recoPulses(config):

    pulses = {}
    pulses['IT59'] = 'IceTopVEMPulses_0'
    for cfg in ['IT73', 'IT81', 'IT81-II', 'IT81-III']:
        pulses[cfg] = 'CleanedHLCTankPulses'

    return pulses[config]


def null_stream(config):
    nullstream = {}
    nullstream['IT73'] = 'nullsplit'
    nullstream['IT81'] = 'in_ice'
    return nullstream[config]


def it_stream(config):

    itstream = {}
    itstream['IT59'] = ''
    itstream['IT73'] = 'top_hlc_clusters'
    for cfg in ['IT81', 'IT81-II', 'IT81-III']:
        itstream[cfg] = 'ice_top'

    return itstream[config]


def filter_mask(config):

    filtermask = {}
    for cfg in ['IT59', 'IT73', 'IT81']:
        filtermask[cfg] = 'FilterMask'
    for cfg in ['IT81-II', 'IT81-III']:
        filtermask[cfg] = 'QFilterMask'

    return filtermask[config]
