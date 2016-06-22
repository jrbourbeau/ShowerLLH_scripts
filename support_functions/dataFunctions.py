#!/usr/bin/env python

import glob
import os
from anisotropy.simpleDST.goodrunlist.goodrunfunctions import fileCleaner


def ICtoIT(ic_config):

    if ic_config == 'IC59':
        return 'IT59'
    if ic_config == 'IC79':
        return 'IT73'
    if 'IC86' in ic_config:
        return ic_config.replace('IC86','IT81')
    raise SystemExit('Unrecognized detector configuration')

def ITtoIC(it_config):

    if it_config == 'IT59':
        return 'IC59'
    if it_config == 'IT73':
        return 'IC79-2010'
    if 'IT81' in it_config:
        return it_config.replace('IT81','IC86')
    raise SystemExit('Unrecognized detector configuration')

def getConfigs(it):
    if it == 'IC':
        return ['IC59', 'IC79', 'IC86', 'IC86-II', 'IC86-III', 'IC86-IV']
    if it == 'IT':
        return ['IT59', 'IT73', 'IT81', 'IT81-II', 'IT81-III', 'IT81-IV']


def get_data_files(config, yyyymmdd, runlist, gcd=False):

    yyyy, mmdd = yyyymmdd[:4], yyyymmdd[4:]
    prefix = '/data/exp/IceCube/{}/filtered'.format(yyyy)

    # Collect files and reduce according to good run list
    files = []
    for run in runlist:
        # DSTfiles = '{}/level2a/{}/{}/Level2a_*_IT.i3.bz2'.format(
        #     prefix, mmdd, 'Run00' + str(run))
        if config == 'IT59':
            it59prefix = '/data/ana/CosmicRay/IceTop_level3/exp/IC59'
            DSTfiles = '{}/{}/IT59*.i3.gz'.format(it59prefix, yyyymmdd)
            gcdFormat = '{}/level2/{}/Level1_*GCD.i3.gz'.format(prefix, mmdd)
        if config == 'IT73':
            DSTfiles = '{}/level2a/{}/Level2a_*_Run00{}_*_IT.i3.bz2'.format(prefix, mmdd, run)
            gcdFormat = '{}/level2a/{}/Level2a_*_GCD.i3.bz2'.format(prefix, mmdd)
        if config == 'IT81-2011':
            DSTfiles = '{}/level2/{}/Level2_*Part*_IT.i3.bz2'.format(prefix, mmdd)
            gcdFormat = '{}/level2/{}/Level2_*_GCD.i3.gz'.format(prefix, mmdd)
        if config == 'IT81-2012':
            DSTfiles = '{}/level2/{}/Level2_*Subrun*_IT.i3.bz2'.format(prefix, mmdd)
            gcdFormat = '{}/level2/{}/Level2_*_GCD.i3.gz'.format(prefix, mmdd)
        if config in ['IT81-2013', 'IT81-2014']:
            DSTfiles = '{}/level2/{}/Run????????/Level2_*Subrun*_IT.i3.bz2'.format\
                (prefix, mmdd)
            gcdFormat = '{}/level2/{}/Run????????/Level2_*_GCD.i3.gz'.format(prefix, mmdd)
        files += glob.glob(DSTfiles)
        # print(glob.glob(DSTfiles))
        # print(DSTfiles)
    
    # Eliminate duplicates (happens with '_0' directories)
    baseList, outFiles = [], []
    for f in files:
        basename = os.path.basename(f)
        if basename not in baseList:
            baseList += [basename]
            outFiles += [f]

    if not gcd:
        return outFiles

    # Repeat for GCD files
    gcd = sorted(glob.glob(gcdFormat))
    baseList, gcdFiles = [], []
    for f in gcd:
        basename = os.path.basename(f)
        if basename not in baseList:
            baseList += [basename]
            gcdFiles += [f]

    return outFiles, gcdFiles

def getDataFiles(config, yyyymmdd, runlist, gcd=False):

    yyyy, mmdd = yyyymmdd[:4], yyyymmdd[4:]
    prefix = '/data/exp/IceCube/{}/filtered'.format(yyyy)

    if config == 'IT59':
        it59prefix = '/data/ana/CosmicRay/IceTop_level3/exp/IC59'
        DSTfiles = '{}/{}/IT59*.i3.gz'.format(it59prefix, yyyymmdd)
        # gcdFormat = '{}/level2/{}/Level1_*GCD.i3.gz'.format(prefix, mmdd)
    if config == 'IT73':
        DSTfiles = '{}/level2a/{}/Level2a_*_IT.i3.bz2'.format(prefix, mmdd)
        # gcdFormat = '{}/level2a/{}/Level2a_*_GCD.i3.bz2'.format(prefix, mmdd)
    if config == 'IT81-2011':
        DSTfiles = '{}/level2/{}/Level2_*Part*_IT.i3.bz2'.format(prefix, mmdd)
        # gcdFormat = '{}/level2/{}/Level2_*_GCD.i3.gz'.format(prefix, mmdd)
    if config == 'IT81-2012':
        DSTfiles = '{}/level2/{}/Level2_*Subrun*_IT.i3.bz2'.format(prefix, mmdd)
        # gcdFormat = '{}/level2/{}/Level2_*_GCD.i3.gz'.format(prefix, mmdd)
    if config in ['IT81-2013', 'IT81-2014']:
        DSTfiles = '{}/level2/{}/Run????????/Level2_*Subrun*_IT.i3.bz2'.format\
            (prefix, mmdd)
        # gcdFormat = '{}/level2/{}/Run????????/Level2_*_GCD.i3.gz'.format(
            # prefix, mmdd)
    
        # Collect files and reduce according to good run list
    files = glob.glob(DSTfiles)
    files = sorted(fileCleaner(config, files))

    # Eliminate duplicates (happens with '_0' directories)
    baseList, outFiles = [], []
    for f in files:
        basename = os.path.basename(f)
        if basename not in baseList:
            baseList += [basename]
            outFiles += [f]

    if not gcd:
        return outFiles

    # Repeat for GCD files
    gcd = sorted(glob.glob(gcdFormat))
    baseList, gcdFiles = [], []
    for f in gcd:
        basename = os.path.basename(f)
        if basename not in baseList:
            baseList += [basename]
            gcdFiles += [f]

    return outFiles, gcdFiles


def getDSTfiles(config):

    it = 'IceCube' if config[:2] == 'IC' else 'IceTop'
    cfg = cfgconvert(config)
    # GET PERMISSION TO MOVE THESE TO DATA/ANA
    if cfg == 'IC59':
        fpath = '/data/exp/IceCube/2010/filtered/DST_IC59/simple-dst'
    elif cfg == 'IC79':
        fpath = '/data/exp/IceCube/2010/filtered/DST_IC79/simple_dst'
    # IN THE RIGHT LOCATIONS
    else:
        fpath = '/data/ana/CosmicRay/Anisotropy/%s/%s' % (it, cfg)
        if config[:2] == 'IC':
            fpath += '/simple-dst'

    fileList = glob.glob('%s/*.root' % fpath)
    return sorted(fileList)


def cfgconvert(config):
    newconfig = config
    if config in ['IT81', 'IC86']:
        newconfig = '%s-2011' % config
    if config in ['IT81-II', 'IC86-II']:
        newconfig = config.replace('-II', '-2012')
    if config in ['IT81-III', 'IC86-III']:
        newconfig = config.replace('-III', '-2013')
    if config in ['IT81-IV', 'IC86-IV']:
        newconfig = config.replace('-IV', '-2014')
    return newconfig


def getRun(file):
    st = file.find('Run') + 3
    run = file[st:st + 8]
    return run


def getSubRun(file):
    subrun = 'Part' if 'Part' in file else 'Subrun'
    st = file.find(subrun) + len(subrun)
    sub = file[st:st + 8]
    return sub


def recoPulses(config):
    pulses = {}
    pulses['IT59'] = 'IceTopVEMPulses_0'
    for cfg in ['IT73', 'IT81', 'IT81-II', 'IT81-III', 'IT81-IV']:
        pulses[cfg] = 'CleanedHLCTankPulses'
    return pulses[config]


def recoTrack(config):
    track = {}
    for cfg in ['IT73', 'IT81', 'IT81-II']:
        track[cfg] = 'ShowerPlane'
    for cfg in ['IT81-III', 'IT81-IV']:
        track[cfg] = 'LaputopStandard'
    return track[config]


def it_stream(config):
    itstream = {}
    itstream['IT59'] = ''
    itstream['IT73'] = 'top_hlc_clusters'
    for cfg in ['IT81', 'IT81-II']:
        itstream[cfg] = 'ice_top'
    for cfg in ['IT81-III', 'IT81-IV']:
        itstream[cfg] = 'IceTopSplit'
    return itstream[config]


def filter_mask(config):
    filtermask = {}
    for cfg in ['IT59', 'IT73', 'IT81']:
        filtermask[cfg] = 'FilterMask'
    for cfg in ['IT81-II', 'IT81-III', 'IT81-IV']:
        filtermask[cfg] = 'QFilterMask'
    return filtermask[config]


def filter_names(config):
    f = {}
    f['IT73'] = ['IceTopSTA3_10', 'IceTopSTA3_InIceSMT_10', 'IceTopSTA8_10']
    f['IT81'] = ['IceTopSTA3_11', 'IceTopSTA3_InIceSMT_11', 'IceTopSTA8_11']
    f['IT81-II'] = ['IceTopSTA3_12', 'IceTopSTA5_12']
    f['IT81-III'] = ['IceTopSTA3_13', 'IceTopSTA5_13']
    f['IT81-IV'] = ['IceTopSTA3_13', 'IceTopSTA5_13']
    #f['IT81-IV']  = ['IceTopSTA3_14','IceTopSTA5_14']
    return f[config]


def it_weights(filtermask):
    w = {}
    # IT73
    w['IceTopSTA3_10'] = 3
    w['IceTopSTA3_InIceSMT_10'] = 1.5
    w['IceTopSTA8_10'] = 1
    # IT81-2011
    w['IceTopSTA3_11'] = 3
    w['IceTopSTA3_InIceSMT_11'] = 1.5
    w['IceTopSTA8_11'] = 1
    # IT81-2012
    w['IceTopSTA3_12'] = 10
    w['IceTopSTA5_12'] = 1
    # IT81-2013
    w['IceTopSTA3_13'] = 10
    w['IceTopSTA5_13'] = 1
    # IT81-2014
    w['IceTopSTA3_14'] = 10
    w['IceTopSTA5_14'] = 1

    return w[filtermask]


def it_geo(it):
    detector_geo = 'IT81' if 'IT81' in it else it
    return detector_geo
