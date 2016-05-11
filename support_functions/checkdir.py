#!/usr/bin/env python

#=======================================================================
# File Name     : usefulFunctions.py
# Description   : Contain useful function to avoid errors in python
# Creation Date : 04-20-2016
# Last Modified : Wed 20 Apr 2016 10:30:38 AM CDT
# Created By    : James Bourbeau
#=======================================================================

import sys, os

def checkdir(outfile):
    outdir = os.path.dirname(outfile)
    if outdir == '':
        outdir = os.getcwd()
    if not os.path.isdir(outdir):
        print('\nThe directory {} doesn\'t exist...'.format(outdir)\
            + 'creating it...\n')
        os.makedirs(outdir)
    return
