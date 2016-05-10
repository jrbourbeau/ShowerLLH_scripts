#!/usr/bin/env python

#=========================================================================
# File Name     : energyres.py
# Description   :
# Creation Date : 04-26-2016
# Last Modified : Tue 26 Apr 2016 03:48:09 PM CDT
# Created By    : James Bourbeau
#=========================================================================

import os,sys
sys.path.append("$HOME/dashi")
import dashi
dashi.visual()  # This is needed to display plots, don't ask me why
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
from scipy import stats
import argparse

import myGlobals as my
import simFunctions_IT as simFunctions
from usefulFunctions import checkdir
import colormaps as cmaps
from geo import loadGeometryTxt
from plotFunctions import diverge_map
from ShowerLLH_scripts.analysis.load_sim import load_sim

#### Plot median values as a colormesh in position (including outer tanks) ####


def energy_dist(data, cuts):
# def energy_dist(data, emin=None, emax=None):
    ratio = np.divide(data['ML_energy'], data['MC_energy'])[cuts]
    bin_vals = np.arange(-1000, 1015, 15)

    x = data['MC_x']
    x = x[cuts]
    y = data['MC_y']
    y = y[cuts]

    # if emin is not None and emax is not None:
    #     print('Made it into the mask if statement')
    #     mask = (np.log10(data['MC_energy'])>=emin)*(np.log10(data['MC_energy'])<=emax)
    #     ratio = ratio[mask]
    #     x = x[mask]
    #     y = y[mask]

    binned_statistic, x_edges, y_edges, binnumber = stats.binned_statistic_2d(
        x, y, ratio, statistic='median', bins=bin_vals)

    X, Y = np.meshgrid(x_edges, y_edges)
    masked_array = np.ma.array(binned_statistic, mask=np.isnan(binned_statistic))
    # masked_array = np.ma.masked_less(masked_array,0.25)
    # cmap = cmaps.plasma
    cmap = plt.get_cmap('RdBu_r')
    # cmap = diverge_map(high=('#A00000'),low=('#3F54C0'))
    cmap.set_bad('w', 1.)
    # plt.pcolormesh(X, Y, masked_array, cmap=cmap)
    # plt.pcolormesh(X, Y, masked_array, vmin=0.75, vmax=1.25, cmap=cmap)
    plt.pcolormesh(X, Y, masked_array, vmin=0.8, vmax=1.2, cmap=cmap)
    plt.xlabel(r'X [m]')
    plt.ylabel(r'Y [m]')
    cb = plt.colorbar(label='$E_{LLH}/E_{MC}$')
    # itgeo = loadGeometryTxt('IT73_Outline.dat')
    itgeo = np.load('/data/user/jbourbeau/showerllh/resources/tankpos.npy')
    itgeo = itgeo.item()
    itgeo = itgeo['IT73']
    plt.scatter(*zip(*itgeo), c = 'white', label = 'Outer IT Tanks', s = 15, linewidth = 0.8, alpha = 0.7)
    plt.xlim([-1000, 1000])
    plt.ylim([-1000, 1000])
    plt.title(r'ShowerLLH - IT73 Energy Resolution')
    outfile = '/home/jbourbeau/public_html/figures/showerLLHstudy/energy_dist.png'
    checkdir(outfile)
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.close()


def energyres(data):
    energyMC = np.log10(data['MC_energy'])
    energyLLH = np.log10(data['ML_energy'])

    # Energy bins in Log10(Energy/GeV)
    bins = np.arange(4, 9.501, 0.05)

    energy2d = dashi.factory.hist2d((energyMC, energyLLH), (bins, bins))
    # colormap = cmaps.plasma
    # colormap = cmaps.viridis
    colormap = plt.get_cmap('OrRd')
    energy2d.imshow(norm=LogNorm(), cmap=colormap)
    plt.xlabel('$log_{10}(E_{MC}/GeV)$')
    plt.ylabel('$log_{10}(E_{LLH}/GeV)$')
    plt.xlim([4, 6.0])
    # plt.xlim([4, 9.50])
    plt.ylim([5, 9])
    # plt.ylim([4, 9.50])
    cb = plt.colorbar(label='Counts')
    plt.plot([4,10],[4,10])
    outfile = '/home/jbourbeau/public_html/figures/showerLLHstudy/dashi.png'
    checkdir(outfile)
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.close()


def event_dist(data):
    x = data['MC_x']
    y = data['MC_y']
    bins = np.arange(-1000, 1025, 15)

    eventdist = dashi.factory.hist2d((x, y), (bins, bins))
    # colormap = cmaps.plasma
    # colormap = cmaps.viridis
    # colormap = plt.get_cmap('OrRd')
    colormap = plt.get_cmap('Oranges')
    eventdist.imshow(cmap=colormap)
    plt.xlabel('X [m]')
    plt.ylabel('Y [m]')
    plt.title(r'ShowerLLH - IT73 Event Distribution')
    plt.xlim([-1000, 1000])
    plt.ylim([-1000, 1000])
    cb = plt.colorbar(label='$Counts$')
    # itgeo = loadGeometryTxt('IT73_Outline.dat')
    itgeo = np.load('/data/user/jbourbeau/showerllh/resources/tankpos.npy')
    itgeo = itgeo.item()
    itgeo = itgeo['IT73']
    plt.scatter(*zip(*itgeo), c = 'white', label = 'Outer IT Tanks', s = 15, linewidth = 0.8, alpha = 0.7)
    outfile = '/home/jbourbeau/public_html/figures/showerLLHstudy/event_dist.png'
    checkdir(outfile)
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.close()


def energyres_old(data):
    energyMC = np.log10(data['MC_energy'])
    energyLLH = np.log10(data['ML_energy'])
    energyfrac = energyLLH / energyMC
    print('energyfrac = {}'.format(energyfrac))
    # print('energyMC = {}'.format(energyMC))
    # print('energyLLH = {}'.format(energyLLH))

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
    Hmasked = np.ma.masked_where(H == 0, H)  # Mask pixels with a value of zero
    print('Hmasked = {}'.format(Hmasked))

    # Plot 2D histogram using pcolor
    fig, ax = plt.subplots(1, 1)
    colormap = cmaps.plasma
    # colormap = cmaps.viridis
    plt.pcolormesh(bins, bins, Hmasked, norm=LogNorm(), cmap=colormap)
    plt.xlabel('$log_10(MC Energy/GeV)$')
    plt.ylabel('$log10(LLH Energy/GeV)$')
    ax.set_xlim(4, 9.50)
    ax.set_ylim(4, 9.50)
    # ax.set_xlim(5, 8)
    # ax.set_ylim(5, 8)
    cbar = plt.colorbar()
    cbar.ax.set_ylabel('Counts')
    outfile = '/home/jbourbeau/public_html/figures/showerLLHstudy/{}.png'.format(
        args.outFile)
    checkdir(outfile)
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":

    # Global variables setup for path names
    my.setupShowerLLH(verbose=False)

    p = argparse.ArgumentParser(
        description='Builds binned histograms for use with ShowerLLH')
    p.add_argument('-c', '--config', dest='config',
                   default='IT73',
                   choices=['IT73', 'IT81'],
                   help='Detector configuration')
    p.add_argument('-o', '--outFile', dest='outFile',
                   help='Output filename')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='standard',
                   choices=['standard', 'nozenith', 'logdist'],
                   help='Option for a variety of preset bin values')
    args = p.parse_args()

    # datafile = my.llh_data + \
    #     '/{}_sim/SimPlot_{}.npy'.format(args.config, args.bintype)
    # data = (np.load(datafile)).item()
    # print(data.keys())
    data = load_sim(config=args.config, bintype=args.bintype)
    cuts = data['cuts']['llh']

    # energyres(data)
    # event_dist(data)
    # energy_dist(data, emin=5., emax=6.)
    energy_dist(data,cuts)
