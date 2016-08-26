#!/usr/bin/env python

#=========================================================================
# File Name     : GoodRunList.py
# Description   : Classes used to store and process good run list (GRL)
#                 information.
#                 For reference info on good run lists, see
#                 https://wiki.icecube.wisc.edu/index.php/Goodrunlist.
# Creation Date : 05-31-2016
# Created By    : James Bourbeau
#=========================================================================

import sys
import glob
import re
import numpy as np

import support_functions.dataFunctions as df


def get_GRL_file(config):
    if 'IT' in config:
        config = df.ITtoIC(config) 
    detector = config[:4]
    year = config[5:]
    return '/data/ana/CosmicRay/IceTop_GRL/{}_{}_GoodRunInfo_4IceTop.txt'.format(detector, year)


class RunInfo(object):
    ''' Holds info for each run '''

    def __init__(self):
        self.run_id = -1
        self.config = ''
        self.livetime_sec = -1
        self.inice_ok = -1
        self.icetop_ok = -1
        self.icetop_L2_ok = -1
        self.active_strings = -1
        self.active_doms = -1
        self.active_inice = -1
        self.path = ''
        self.comment = ''

    def __str__(self):
        ''' dump the info from this object '''
        return 'Run {}\nDetector {}\nDate {}\nLivetime(sec) {}'.format(
            self.run_id, self.config, "tba", self.livetime_sec)

    def get_date(self):
        ''' extract the date of this run from the folder it is present in '''
        if (self.run_id != -1 and self.path != ''):
            try:
                splitpath = self.path.split('/')
                splitpath = [str.strip(v) for v in splitpath if v not in ['', '\n']]
                yyyy = splitpath[3]
                mmdd = splitpath[6]
                return yyyy + mmdd
                # format (yyyy,mm,dd)
                # return (int(d[3]), int(d[6][:2]), int(d[6][2:]))
            except:
                raise ValueError('Unexpected path format')
        return -1


class GoodRunList(object):

    def __init__(self, config):
        self.run_list = []  # list of all runs in the good run list
        # self.good_run_list = []  # list of all runs that have a good inice
        # entry
        self.configs = ['IT73','IT81-2011','IT81-2012',
                        'IT81-2013','IT81-2014','IT81-2015']
        # self.configs = ['IC86-2011', 'IC86-2012',
        #                 'IC86-2013', 'IC86-2014']
        self.add_GRL(config)

    def add_GRL(self, config):
        ''' add the info from a goodrun_list file '''
        if (not config in self.configs):
            raise ValueError('Detector configuration {} not found. Pick from this list of detector configurations: {}'.format(
                config, str(self.configs)))
        self.config = config

        filepath = get_GRL_file(config)
        with open(filepath) as file:
            lines = file.readlines()
        for i, line in enumerate(lines[4:]):  # First four lines are comments
            splitline = line.split('\t')
            splitline = [v for v in splitline if v not in ['', '\n']]
            try:
                ri = RunInfo()
                ri.config = config
                ri.run_id = int(splitline[0])
                ri.inice_ok = bool(float(splitline[1]))
                ri.icetop_ok = bool(float(splitline[2]))
                ri.icetop_L2_ok = bool(float(splitline[3]))
                ri.livetime_sec = float(splitline[4])
                ri.active_strings = int(splitline[5]) if (not splitline[5]=='-') else -1
                ri.active_doms = int(splitline[6]) if (not splitline[6]=='-') else -1 
                ri.active_inice = int(splitline[7]) if (not splitline[7]=='-') else -1 
                # 2015 good run list OutDir column has unnecessary '//'
                ri.path = splitline[8].replace('//', '/')
                if (len(splitline) > 9):
                    ri.comment = ' '.join(splitline[9:])
                # now append it to the list
                self.run_list.append(ri)
            except:
                print('Line {} in GRL file has an unexpected format in GRL file... Skipping line...').format(i)
                pass

    def get_good_runs(self):
        good_run_list = [i for i in self.run_list if i.icetop_L2_ok]
        return good_run_list

    def get_good_dates(self):
        good_runs = self.get_good_runs()
        good_dates = [i.get_date() for i in good_runs]
        good_dates = np.unique(good_dates)
        return good_dates
    
    def date_to_goodrun_num(self):
        dates = self.get_good_dates()
        # initialize new dictionary with date keys and [] initial values
        date_2_num = dict((date, [])for date in dates)
        runs = self.get_good_runs()
        for run in runs:
            date_2_num[run.get_date()].append(run.run_id)

        return date_2_num
    
    def date_to_goodruns(self):
        dates = self.get_good_dates()
        # initialize new dictionary with date keys and [] initial values
        date_2_num = dict((date, [])for date in dates)
        runs = self.get_good_runs()
        for run in runs:
            date_2_num[run.get_date()].append(run)

        return date_2_num
