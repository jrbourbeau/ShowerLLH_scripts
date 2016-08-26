#!/usr/bin/env python

import os
import sys
import shutil
import argparse


if __name__ == "__main__":

    p = argparse.ArgumentParser(
        description='Sets up "shebang" lines in scripts that use ShowerLLH',
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument('-t', '--toolset', dest='toolset',
                   default='py2-v1',
                   choices=['py2-v2', 'py2-v1', 'standard'],
                   help='Option to specify which cvmfs toolset to use')
    p.add_argument('-m', '--metaproject', dest='metaproject',
                   default='/path/to/metaproject/dir',
                   help='Path to metaproject containing ShowerLLH project')
    p.add_argument('--llhdir', dest='llh_dir',
                   default='/path/to/ShowerLLH/dir',
                   help='Path to ShowerLLH storge directory')
    args = p.parse_args()

    cwd = os.getcwd()
    filelist = ['make_tables/MakeHist.py',
                'make_tables/merger.py',
                'make_tables/normalize.py',
                'run_sim/MakeShowerLLH.py',
                'run_sim/MakeExtras.py',
                'run_sim/MakeMC.py',
                'run_data/merge.py',
                'run_data/MakeShowerLLH.py']

    # Set up 'shebang' line in appropreiate python scripts
    # to allow them to work as stand-alone IceTray scripts
    for file in filelist:
        with open(cwd + '/' + file, 'r') as original_file:
            current_toolset_line = original_file.readline()
            current_metaproject_line = original_file.readline()
            current_toolset = current_toolset_line.split('/')[5]
            current_metaproject = current_metaproject_line.split(' ')[1].replace('/build\n','')
            new_toolset_line = current_toolset_line.replace(current_toolset,
                                                            args.toolset)
            new_metaproject_line = current_metaproject_line.replace(
                current_metaproject,
                args.metaproject)
            with open(cwd + '/' + file, 'w') as new_file:
                new_file.write(new_toolset_line)
                new_file.write(new_metaproject_line)
                shutil.copyfileobj(original_file, new_file)

    # Set up support_functions/paths.py
    with open(cwd + '/support_functions/paths.py', 'r') as original_paths:
        lines = original_paths.readlines()
        current_llhdir_line = lines[7]
        current_llhdir = current_llhdir_line.split()[-1].strip()
        new_llhdir_line = current_llhdir_line.replace(current_llhdir,
                                                        '"'+args.llh_dir+'"')
        current_metaproject_line = lines[6]
        current_metaproject = current_metaproject_line.split()[-1].strip()
        new_metaproject_line = current_metaproject_line.replace(
            current_metaproject,
            '"'+args.metaproject+'"')

        with open(cwd + '/support_functions/paths.py', 'w') as new_paths:
            lines[7] = new_llhdir_line
            lines[6] = new_metaproject_line
            new_paths.writelines(lines)
