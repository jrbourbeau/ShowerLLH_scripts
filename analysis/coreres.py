#!/usr/bin/env python

#=========================================================================
# File Name     : angular-res.py
# Description   :
# Creation Date : 04-26-2016
# Last Modified : Tue 26 Apr 2016 03:48:09 PM CDT
# Created By    : James Bourbeau
#=========================================================================

import sys
sys.path.append("$HOME/dashi")
import dashi
dashi.visual()  # This is needed to display plots, don't ask me why
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import argparse

import myGlobals as my
import simFunctions_IT as simFunctions
from usefulFunctions import checkdir
import colormaps as cmaps
from geo import loadGeometryTxt
from plotFunctions import diverge_map
from ShowerLLH_scripts.analysis.load_sim import load_sim

def core_res(data,cuts):
    MC_x = data['MC_x']
    MC_y = data['MC_y']
    MC_r = np.sqrt(MC_x**2+MC_y**2)[cuts]

    ML_x = data['ML_x']
    ML_y = data['ML_y']
    ML_r = np.sqrt(ML_x**2+ML_y**2)[cuts]

    # Energy bins in Log10(Energy/GeV)
    bins = np.arange(4, 9.501, 0.05)

    energy = data['MC_energy'][cuts]
    # print('ML_r finite = {}'.format(np.isfinite(ML_r).any()))
    # print('ML_r infinite = {}'.format(np.isinf(ML_r).any()))
    # print('ML_r nan = {}'.format(np.isnan(ML_r).any()))
    # badlist = [i for i in range(len(ML_r)) if np.isnan(ML_r[i])]
    # print('badlist = {}'.format(badlist))
    # if emin is not None and emax is not None:
    #     print('Made it into the mask if statement')
    #     mask = (np.log10(data['MC_energy'])>=emin)*(np.log10(data['MC_energy'])<=emax)
    #     MC_r = MC_r[mask]
    #     ML_r = ML_r[mask]
    #     energy = energy[mask]

    # binned_statistic, x_edges, binnumber = stats.binned_statistic(
    #     np.log10(energy), ML_r/MC_r, statistic='median', bins=bins)
    binned_statistic, x_edges, binnumber = stats.binned_statistic(
        np.log10(energy), ML_r/MC_r, statistic=np.nanmedian, bins=bins)
    masked_array = np.ma.array(binned_statistic, mask=np.isnan(binned_statistic))

    cut = np.logical_not(np.isnan(binned_statistic))
    x = bins[:-1]+0.05
    x = x[cut]
    y = binned_statistic[cut]
    plt.errorbar(x, y,linestyle='None',marker='.', markersize=10, color='k')
    plt.xlabel('$log_{10}(E_{MC}/GeV)$')
    plt.ylabel('$R_{LLH}/R_{MC}$')
    plt.title(r'ShowerLLH - IT73 Core Resolution')
    outfile = '/home/jbourbeau/public_html/figures/showerLLHstudy/core_res_emin5_emax6.png'
    checkdir(outfile)
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
    plt.close()

def core_res_dist(data,cuts):
    MC_x = data['MC_x']
    MC_y = data['MC_y']
    MC_r = np.sqrt(MC_x**2+MC_y**2)[cuts]

    ML_x = data['ML_x']
    ML_y = data['ML_y']
    ML_r = np.sqrt(ML_x**2+ML_y**2)[cuts]

    ratio = np.divide(ML_r, MC_r)
    bin_vals = np.arange(-1000, 1015, 15)

    binned_statistic, x_edges, y_edges, binnumber = stats.binned_statistic_2d(
        MC_x[cuts], MC_y[cuts], ratio, statistic=np.nanmedian, bins=bin_vals)
    X, Y = np.meshgrid(x_edges, y_edges)
    masked_array = np.ma.array(binned_statistic, mask=np.isnan(binned_statistic))
    # masked_array = np.ma.masked_less(masked_array,0.25)
    # cmap = cmaps.plasma
    # cmap = plt.get_cmap('seismic')
    cmap = diverge_map(high=('#A00000'),low=('#3F54C0'))
    cmap.set_bad('w', 1.)
    # plt.pcolormesh(X, Y, masked_array, cmap=cmap)
    plt.pcolormesh(X, Y, masked_array, vmin=0.9, vmax=1.1, cmap=cmap)
    plt.xlabel('X [m]')
    plt.ylabel('Y [m]')
    cb = plt.colorbar(label='$R_{LLH}/R_{MC}$')
    itgeo = np.load('/data/user/jbourbeau/showerllh/resources/tankpos.npy')
    itgeo = itgeo.item()
    itgeo = itgeo['IT73']
    plt.scatter(*zip(*itgeo), c = 'white', label = 'Outer IT Tanks', s = 15, linewidth = 0.8, alpha = 0.7)
    plt.xlim([-1000, 1000])
    plt.ylim([-1000, 1000])
    plt.title('ShowerLLH - IT73 Core Resolution')
    outfile = '/home/jbourbeau/public_html/figures/showerLLHstudy/core_res_dist.png'
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
            choices=['IT73','IT81'],
            help='Detector configuration')
    p.add_argument('-o', '--outFile', dest='outFile',
            help='Output filename')
    p.add_argument('-b', '--bintype', dest='bintype',
            default='standard',
            choices=['standard','nozenith','logdist'],
            help='Option for a variety of preset bin values')
    args = p.parse_args()

    # datafile = my.llh_data+'/{}_sim/SimPlot_{}.npy'.format(args.config,args.bintype)
    # data = (np.load(datafile)).item()
    data = load_sim(config=args.config, bintype=args.bintype)
    cuts = data['cuts']['llh']
    core_res(data,cuts)
    # core_res(data,emin=5., emax=6.)
    core_res_dist(data,cuts)
