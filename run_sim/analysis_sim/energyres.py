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
from matplotlib.colors import LogNorm
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

    energyMC = np.log10(data['MC_energy'])
    energyLLH = np.log10(data['ML_energy'])
    print('energyMC = {}'.format(energyMC))
    print('energyLLH = {}'.format(energyLLH))

    x = data['MC_x']
    y = data['MC_y']

    # Energy bins in Log10(Energy/GeV)
    bins = np.arange(4, 9.501, 0.05)
    print('bins = {}'.format(bins))

    H, xedges, yedges = np.histogram2d(energyMC, energyLLH, bins=bins)
    print('H = {}'.format(H))
    print('H.shape = {}'.format(H.shape))
    print('bins.shape = {}'.format(bins.shape))
    # H needs to be rotated and flipped
    H = np.rot90(H)
    H = np.flipud(H)
    # Mask zeros
    Hmasked = np.ma.masked_where(H==0,H) # Mask pixels with a value of zero
    print('Hmasked = {}'.format(Hmasked))

    # Plot 2D histogram using pcolor
    fig, ax = plt.subplots(1,1)
    colormap = cmaps.plasma
    # colormap = cmaps.viridis
    plt.pcolormesh(bins,bins,Hmasked,norm=LogNorm(),cmap=colormap)
    plt.xlabel('log10(MC Energy/GeV)')
    plt.ylabel('log10(LLH Energy/GeV)')
    ax.set_xlim(4, 9.50)
    ax.set_ylim(4, 9.50)
    # ax.set_xlim(5, 8)
    # ax.set_ylim(5, 8)
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')
    outfile = '/home/jbourbeau/public_html/figures/showerLLHstudy/{}.png'.format(args.outFile)
    checkdir(outfile)
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
