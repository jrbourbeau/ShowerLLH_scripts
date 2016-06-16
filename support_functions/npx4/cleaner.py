#!/usr/bin/env python

#=========================================================================
# File Name     : cleaner.py
# Description   : Script to clean all contents in npx4-*/ directories
# Creation Date : 04-21-2016
# Last Modified : Thu 21 Apr 2016 08:52:07 AM CDT
# Created By    : James Bourbeau
#=========================================================================

import os
import glob
import argparse
import support_functions.myGlobals as my

if __name__ == "__main__":

    p = argparse.ArgumentParser(
        description='Removes files from npx4-*/ directories')
    p.add_argument('--type', dest='type', nargs='*',
                   choices=['showerllh', 'counttables', 'npx'], help='types of jobs to delete')
    args = p.parse_args()

    my.setupGlobals(verbose=False)
    npxdirectories = ['error', 'execs', 'logs', 'out']
    for jobtype in args.type:
        for directory in npxdirectories:
            print('Cleaning npx4-{}/...'.format(directory))
            removelist = glob.glob(
                '{}/npx4-{}/{}*'.format(my.npx4, directory, jobtype))
            for file in removelist:
                os.remove(file)
