#!/usr/bin/env python

#=========================================================================
# File Name     : cleaner.py
# Description   : Script to clean all contents in npx4-*/ directories
# Creation Date : 04-21-2016
# Last Modified : Thu 21 Apr 2016 08:52:07 AM CDT
# Created By    : James Bourbeau
#=========================================================================

import os, glob
import myGlobals as my

if __name__ == "__main__":

    my.setupGlobals(verbose=False)
    npxdirectories = ['error','execs','logs','out']
    for directory in npxdirectories:
        print('Cleaning npx4-{}/...'.format(directory))
        removelist = glob.glob('{}/npx4-{}/*'.format(my.npx4,directory))
        for file in removelist:
            os.remove(file)
