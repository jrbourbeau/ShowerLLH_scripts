#!/usr/bin/env python

#=======================================================================
# File Name     : checkdir.py
# Description   : Checks whether the path to a file or directory exists.
#                 If the directory doesn't exist, it is created. 
# Creation Date : 04-20-2016
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
