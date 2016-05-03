#!/usr/bin/env python

#=========================================================================
# File Name     : angular-res.py
# Description   :
# Creation Date : 04-26-2016
# Last Modified : Tue 26 Apr 2016 03:48:09 PM CDT
# Created By    : James Bourbeau
#=========================================================================

import sys
import numpy as np
import matplotlib.pyplot as plt
import argparse

import myGlobals as my
import simFunctions_IT as simFunctions
from usefulFunctions import checkdir
import colormaps as cmaps

if __name__ == "__main__":

    # Global variables setup for path names
    my.setupShowerLLH(verbose=False)

    p = argparse.ArgumentParser(
            description='Builds binned histograms for use with ShowerLLH')
    p.add_argument('-c', '--config', dest='config',
            default='IT73',
            choices=['IT73','IT81'],
            help='Detector configuration')
    p.add_argument('-o', '--outFile', dest='outFile',
            help='Output filename')
    p.add_argument('-b', '--bintype', dest='bintype',
            default='standard',
            choices=['standard','nozenith','logdist'],
            help='Option for a variety of preset bin values')
    args = p.parse_args()

    datafile = my.llh_data+'/{}_sim/SimPlot_{}.npy'.format(args.config,args.bintype)
    data = (np.load(datafile)).item()
    print(data.keys())

    zenithMC = data['MC_zenith']
    zenithLLH = data['zenith']
    print('zenithMC = {}'.format(zenithMC))
    print('zenithLLH = {}'.format(np.cos(zenithLLH)))

    # Zenith Bins in radians (made with equal solid angle bins)
    bins = np.linspace(1, np.cos(40*np.pi/180.), 4)
    bins = np.append(np.arccos(bins), np.pi/2)
    print('bins = {}'.format(bins))

    H, xedges, yedges = np.histogram2d(zenithMC, zenithLLH, bins=bins)
    print('H = {}'.format(H))
    # H needs to be rotated and flipped
    H = np.rot90(H)
    H = np.flipud(H)
    # Mask zeros
    Hmasked = np.ma.masked_where(H==0,H) # Mask pixels with a value of zero
    print('Hmasked = {}'.format(Hmasked))

    # Plot 2D histogram using pcolor
    fig2 = plt.figure()
    plt.pcolormesh(bins,bins,Hmasked)
    plt.xlabel('x')
    plt.ylabel('y')
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')
    # fig, ax = plt.subplots(1,1)
    # # plt.scatter(zenithMC,zenithLLH)
    # plt.hist2d(zenithMC,zenithLLH, bins=40)
    # colormap = cmaps.viridis
    # plt.colorbar(cmap = colormap)
    # # colormap = cmaps.plasma
    # # colormap = cmap_discretize(plt.cm.jet,bins)
    # # colormap = cmaps.viridis
    # # cb.set_label("Foo", labelpad=-1)
    # tPars = {'fontsize':16}
    # plt.title('Zenith comparison',**tPars)
    # ax.set_xlabel(r'MC Zenith $[^{\circ}]$', **tPars)
    # ax.set_ylabel(r'LLH Zenith $[^{\circ}]$',**tPars)
    # # ax.set_xlim(-650,650)
    # plt.show()
    # # plt.legend()
    # # outfile = '/home/jbourbeau/public_html/figures/snowheights/{}.png'.format(opts['outfile'])
    # # checkdir(outfile)
    # # plt.savefig(outfile, dpi=300, bbox_inches='tight')
