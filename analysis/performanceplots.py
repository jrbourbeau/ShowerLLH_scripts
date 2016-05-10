#!/usr/bin/env python

#=========================================================================
# File Name     : performanceplots.py
# Description   : Contains functions that generate various ShowerLLH
#                 performance related plots
# Creation Date : 05-06-2016
# Last Modified : Fri 06 May 2016 02:41:11 PM CDT
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
from ShowerLLH_scripts.analysis.load_sim import load_sim

def get_Ebins(reco=False):
    ebins = np.arange(4, 9.51, 0.05)
    if reco:
        ebins = ebins[20:]
    return ebins

def lower_error(y):
    error = np.percentile(y,q=16)
    return error

def upper_error(y):
    error = np.percentile(y,q=84)
    return error

def get_medians(x, y, bins):
    bin_medians, bin_edges, binnumber = stats.binned_statistic(x, y, statistic = 'median', bins = bins)
    err_up, err_up_edges, err_up_binnum = stats.binned_statistic(x, y, statistic = upper_error, bins = bins)
    err_down, err_down_edges, err_down_binnum = stats.binned_statistic(x, y, statistic = lower_error, bins = bins)
    error = [bin_medians-err_down,err_up-bin_medians]
    bin_centers = bin_edges[:-1]+0.05
    return bin_centers, bin_medians, error

def energyres(data, cuts, **opts):
    energyMC = data['MC_energy'][cuts]
    energyLLH = data['ML_energy'][cuts]
    energy_res = np.log10(energyLLH/energyMC)
    # Energy bins in Log10(Energy/GeV)
    # energy_bins = np.arange(4, 9.501, 0.05)
    energy_bins = get_Ebins()
    energy_bins = np.linspace(energy_bins.min(), energy_bins.max(), opts['numbins']+1)

    bin_centers, bin_medians, error = get_medians(np.log10(energyMC), energy_res, energy_bins)

    plt.errorbar(bin_centers, bin_medians, yerr=error, marker='.', color='b')
    plt.xlabel('$log_{10}(E_{\mathrm{true}}/\mathrm{GeV})$')
    plt.ylabel('$log_{10}(E_{LLH}/E_{\mathrm{true}})$')
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    plt.xlim([5.5, 9.5])
    outfile = opts['outdir']+'energy_res_LLHcuts.png'
    plt.savefig(outfile)
    plt.close()
    # bin_centers = bin_edges[:-1] + (1-0.05*index)*(energy_bins[1] - energy_bins[0])/2.

def eres_position(data, cuts, **opts):
    energyMC = data['MC_energy'][cuts]
    energyLLH = data['ML_energy'][cuts]
    energy_res = np.log10(energyLLH/energyMC)
    MC_x = data['MC_x'][cuts]
    MC_y = data['MC_y'][cuts]
    core_pos = np.sqrt(MC_x**2+MC_y**2)

    # Distance bins in [m]
    distance_bins = np.append(np.arange(0,600,10), np.arange(600,1051,50))

    bin_centers, bin_medians, error = get_medians(core_pos, energy_res, distance_bins)

    plt.errorbar(bin_centers, bin_medians, yerr=error, marker='.', color='b')
    plt.xlim([0,1000])
    plt.xlabel('$\mathrm{Core \ Position} \ [m]$')
    plt.ylabel('$log_{10}(E_{LLH}/E_{\mathrm{true}})$')
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    outfile = opts['outdir']+'eres_pos_LLHcuts.png'
    plt.savefig(outfile)
    plt.close()
    # bin_centers = bin_edges[:-1] + (1-0.05*index)*(energy_bins[1] - energy_bins[0])/2.

def coreres(data, cuts, **opts):
    MC_x = data['MC_x'][cuts]
    MC_y = data['MC_y'][cuts]
    ML_x = data['ML_x'][cuts]
    ML_y = data['ML_y'][cuts]
    core_res = np.sqrt((ML_x-MC_x)**2+(ML_y-MC_y)**2)

    # Energy bins in Log10(Energy/GeV)
    # energy_bins = np.arange(4, 9.501, 0.05)
    energy_bins = get_Ebins()
    energy_bins = np.linspace(energy_bins.min(), energy_bins.max(), opts['numbins']+1)
    energyMC = data['MC_energy'][cuts]

    bin_centers, bin_medians, error = get_medians(np.log10(energyMC), core_res, energy_bins)

    plt.errorbar(bin_centers, bin_medians, yerr=error, marker = '.', color='b')
    plt.xlabel('$log_{10}(E_{\mathrm{true}}/\mathrm{GeV})$')
    plt.ylabel('$\\vec{x}_{LLH}-\\vec{x}_{\mathrm{true}} \ [m]$')
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    plt.xlim([5.5, 9.5])
    plt.ylim([0, 90])
    outfile = opts['outdir']+'core_res_LLHcuts.png'
    plt.savefig(outfile)
    plt.close()

def LLHenergy_MCenergy(data, cuts, **opts):
    energyMC = np.log10(data['MC_energy'])[cuts]
    energyLLH = np.log10(data['ML_energy'])[cuts]
    # Energy bins in Log10(Energy/GeV)
    bins = np.arange(4, 9.501, 0.05)

    energy2d = dashi.factory.hist2d((energyMC, energyLLH), (bins, bins))
    # colormap = cmaps.plasma
    # colormap = cmaps.viridis
    colormap = plt.get_cmap('OrRd')
    energy2d.imshow(norm=LogNorm(), cmap=colormap)
    plt.xlabel('$log_{10}(E_{\mathrm{true}}/\mathrm{GeV})$')
    plt.ylabel('$log_{10}(E_{LLH}/\mathrm{GeV})$')
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    # plt.xlim([4, 6.0])
    plt.xlim([5, 9])
    plt.ylim([5, 9])
    cb = plt.colorbar(label='Counts')
    outfile = opts['outdir']+'LLHenergy_vs_MCenergy.png'
    plt.savefig(outfile)
    plt.close()

if __name__ == "__main__":
    # Global variables setup for path names
    my.setupShowerLLH(verbose=False)

    p = argparse.ArgumentParser(
        description='Creates performance plots for ShowerLLH')
    p.add_argument('-c', '--config', dest='config',
                   default='IT73',
                   choices=['IT73', 'IT81'],
                   help='Detector configuration')
    p.add_argument('-o', '--outdir', dest='outdir',
                   default='/home/jbourbeau/public_html/figures/showerLLHstudy/', help='Output directory')
    p.add_argument('-b', '--bintype', dest='bintype',
                   default='standard',
                   choices=['standard', 'nozenith', 'logdist'],
                   help='Option for a variety of preset bin values')
    p.add_argument('-n', '--numbins', dest='numbins', type=float,
                   default=30, help='Number of energy bins')
    args = p.parse_args()
    opts = vars(args).copy()

    # datafile = my.llh_data + \
    #     '/{}_sim/SimPlot_{}.npy'.format(args.config, args.bintype)
    # data = (np.load(datafile)).item()
    # print(data.keys())
    data = load_sim(config=args.config, bintype=args.bintype)
    cuts = data['cuts']['llh']

    energyres(data, cuts, **opts)
    coreres(data, cuts, **opts)
    eres_position(data, cuts, **opts)
    LLHenergy_MCenergy(data, cuts, **opts)
    # event_dist(data)
    # energy_dist(data, emin=5., emax=6.)
    # energy_dist(data,cuts)
