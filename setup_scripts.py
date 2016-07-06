#!/usr/bin/env python

#=========================================================================
# File Name     : setup_scripts.py
# Description   : Set up 'shebang' line in appropreiate python scripts
# Creation Date : 07-05-2016
# Created By    : James Bourbeau
#=========================================================================

import os
import sys
import shutil
import argparse

if __name__ == "__main__":

    p = argparse.ArgumentParser(
        description='Sets up "shebang" lines in scripts that use ShowerLLH',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-t', '--toolset', dest='toolset',
                   choices=['py2-v2','py2-v1','standard'],
                   help='Toolset to use')
    p.add_argument('-m', '--metaproject', dest='metaproject',
                   help='Metaproject to use')
    args = p.parse_args()

    cwd = os.getcwd()
    filelist = ['/make_tables/MakeHist.py',
                '/make_tables/makeLLHtables.py',
                '/run_sim/MakeShowerLLH.py',
                '/run_sim/MakeExtras.py',
                '/run_sim/MakeMC.py',
                '/run_data/MakeShowerLLH.py']

    for file in filelist:
        with open(cwd+file, 'r') as original_file:
            current_toolset_line = original_file.readline()
            current_metaproject_line = original_file.readline()
            current_toolset = current_toolset_line.split('/')[5]
            current_metaproject = current_metaproject_line.split(' ')[1]
            new_toolset_line = current_toolset_line.replace(current_toolset,
                                                            args.toolset)
            new_metaproject_line = current_metaproject_line.replace(
                                                    current_metaproject,
                                                    args.metaproject+'\n')
            with open(cwd+file, 'w') as new_file:
                new_file.write(new_toolset_line)
                new_file.write(new_metaproject_line)
                shutil.copyfileobj(original_file, new_file)
