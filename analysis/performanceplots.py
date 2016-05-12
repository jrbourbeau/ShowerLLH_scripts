#!/usr/bin/env python

#=========================================================================
# File Name     : performanceplots.py
# Description   : Contains functions that generate various ShowerLLH
#                 performance related plots
# Creation Date : 05-06-2016
# Last Modified : Fri 06 May 2016 02:41:11 PM CDT
# Created By    : James Bourbeau
#=========================================================================

import os
import sys
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LogNorm
import argparse

import myGlobals as my
from load_sim import load_sim
from effective_area import getEff
from LLH_tools import *
from sim import zfix
import colormaps as cmaps

#==================
# Ploting functions
#==================


def plot_vs_energy(y, data, cuts, **kwargs):
    energy_bins = get_energy_bins()
    energy_bins = np.linspace(
        energy_bins.min(), energy_bins.max(), kwargs['numbins'] + 1)
    energyMC = data['MC_energy'][cuts]

    bin_centers, bin_medians, error = get_medians(
        np.log10(energyMC), y, energy_bins)

    plt.errorbar(bin_centers, bin_medians, yerr=error, marker='.', )
    plt.xlabel('$\log_{10}(E_{\mathrm{true}}/\mathrm{GeV})$')
    plt.ylabel(kwargs['ylabel'])
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    # plt.xlim([5.5, 9.5])
    # plt.ylim([0, 90])
    plt.savefig(kwargs['outfile'])
    plt.close()


def plot_vs_zenith(y, data, cuts, **kwargs):
    zenith_bins = np.linspace(0.75, 1.0, 46)
    # energy_bins = np.linspace(
    # energy_bins.min(), energy_bins.max(), kwargs['numbins'] + 1)
    # zenithMC = data['MC_zenith'][cuts]
    zenithLLH = np.cos(np.pi - data['zenith'][cuts])

    # bin_centers, bin_medians, error = get_medians(
    #     np.cos(zenithMC), y, zenith_bins)
    bin_centers, bin_medians, error = get_medians(
        zenithLLH, y, zenith_bins)

    plt.errorbar(bin_centers, bin_medians, yerr=error, marker='.', )
    # plt.xlabel('$\cos(\\theta_{\mathrm{true}})$')
    plt.xlabel('$\cos(\\theta_{\mathrm{reco}})$')
    plt.ylabel(kwargs['ylabel'])
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    # plt.xlim([5.5, 9.5])
    # plt.ylim([0, 90])
    plt.savefig(kwargs['outfile'])
    plt.close()

#========================
# Calculational functions
#========================


def energyres(data, cuts, **opts):
    energyMC = data['MC_energy'][cuts]
    energyLLH = data['ML_energy'][cuts]
    energy_res = np.log10(energyLLH / energyMC)

    opts['ylabel'] = '$\log_{10}(E_{\mathrm{LLH}}/E_{\mathrm{true}})$'
    opts['outfile'] = opts['outdir'] + \
        'energy_res_vs_energy_{}.png'.format(opts['bintype'])
    plot_vs_energy(energy_res, data, cuts, **opts)
    opts['outfile'] = opts['outdir'] + \
        'energy_res_vs_zenith_{}.png'.format(opts['bintype'])
    plot_vs_zenith(energy_res, data, cuts, **opts)


def eres_position(data, cuts, **opts):
    energyMC = data['MC_energy'][cuts]
    energyLLH = data['ML_energy'][cuts]
    energy_res = np.log10(energyLLH / energyMC)
    MC_x = data['MC_x'][cuts]
    MC_y = data['MC_y'][cuts]
    core_pos = np.sqrt(MC_x**2 + MC_y**2)

    # Distance bins in [m]
    distance_bins = np.append(np.arange(0, 600, 15), np.arange(600, 1051, 50))

    bin_centers, bin_medians, error = get_medians(
        core_pos, energy_res, distance_bins)

    plt.errorbar(bin_centers, bin_medians, yerr=error, marker='.', )
    plt.xlim([0, 1000])
    plt.xlabel('$\mathrm{Core \ Position} \ [m]$')
    plt.ylabel('$\log_{10}(E_{\mathrm{LLH}}/E_{\mathrm{true}})$')
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    outfile = opts['outdir'] + \
        'energy_res_vs_pos_{}.png'.format(opts['bintype'])
    plt.savefig(outfile)
    plt.close()


def coreres(data, cuts, **opts):
    MC_x = data['MC_x'][cuts]
    MC_y = data['MC_y'][cuts]
    ML_x = data['ML_x'][cuts]
    ML_y = data['ML_y'][cuts]
    core_res = np.sqrt((ML_x - MC_x)**2 + (ML_y - MC_y)**2)

    opts['ylabel'] = '$\\vec{x}_{LLH}-\\vec{x}_{\mathrm{true}} \ [m]$'
    opts['outfile'] = opts['outdir'] + \
        'core_res_vs_energy_{}.png'.format(opts['bintype'])
    plot_vs_energy(core_res, data, cuts, **opts)
    opts['outfile'] = opts['outdir'] + \
        'core_res_vs_zenith_{}.png'.format(opts['bintype'])
    plot_vs_zenith(core_res, data, cuts, **opts)


def LLHenergy_MCenergy(data, cuts, **opts):
    energyMC = np.log10(data['MC_energy'])[cuts]
    energyLLH = np.log10(data['ML_energy'])[cuts]
    # Energy bins in Log10(Energy/GeV)
    energy_bins = get_energy_bins()

    h, xedges, yedges = np.histogram2d(energyMC, energyLLH, bins=energy_bins,
                                       normed=False, weights=None)
    h = np.rot90(h)
    h = np.flipud(h)
    h = np.ma.masked_where(h == 0, h)
    ntot = np.sum(h, axis=0).astype('float')
    ntot[ntot == 0] = 1.
    h /= ntot
    h = np.log10(h)
    print h.max(), h.min()
    extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]

    colormap = cmaps.viridis
    plt.imshow(h, extent=extent, origin='lower',
               interpolation='none', cmap=colormap)
    plt.xlabel('$\log_{10}(E_{\mathrm{true}}/\mathrm{GeV})$')
    plt.ylabel('$\log_{10}(E_{\mathrm{LLH}}/\mathrm{GeV})$')
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    plt.xlim([4, 9.5])
    plt.ylim([5, 9.5])
    cb = plt.colorbar(
        label='$\log_{10}{P(E_{\mathrm{LLH}}|E_{\mathrm{true}})}$')
    plt.plot([0, 10], [0, 10], linestyle='--', color='k')
    outfile = opts['outdir'] + \
        'LLHenergy_vs_MCenergy_{}.png'.format(opts['bintype'])
    plt.savefig(outfile)
    plt.close()


def LLHzenith_MCzenith(data, cuts, **opts):
    zenithMC = np.cos(data['MC_zenith'][cuts])
    zenithLLH = np.cos(np.pi - data['zenith'][cuts])
    # Energy bins in Log10(Energy/GeV)
    zenith_bins = np.linspace(0.75, 1.0, 51)

    h, xedges, yedges = np.histogram2d(
        zenithMC, zenithLLH, bins=zenith_bins, normed=False, weights=None)
    h = np.rot90(h)
    h = np.flipud(h)
    h = np.ma.masked_where(h == 0, h)
    ntot = np.sum(h, axis=0).astype('float')
    ntot[ntot == 0] = 1.
    h /= ntot
    h = np.log10(h)
    print h.max(), h.min()
    extent = [yedges[0], yedges[-1], xedges[0], xedges[-1]]

    colormap = cmaps.viridis
    plt.imshow(h, extent=extent, origin='lower',
               interpolation='none', cmap=colormap)
    plt.xlabel('$\cos(\\theta_{\mathrm{true}})$')
    plt.ylabel('$\cos(\\theta_{\mathrm{reco}})$')
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    # plt.xlim([4, 9.5])
    # plt.ylim([5, 9.5])
    cb = plt.colorbar(
        label='$\log_{10}{P(\\theta_{\mathrm{reco}}|\\theta_{\mathrm{true}})}$')
    # plt.plot([0, 10], [0, 10], linestyle='--', color='k')
    outfile = opts['outdir'] + \
        'LLHzenith_vs_MCzenith_{}.png'.format(opts['bintype'])
    plt.savefig(outfile)
    plt.close()


def effarea(data, cuts, **opts):
    effarea, sigma, relerr = getEff(data, cuts)
    energy_bins = get_bin_mids(get_energy_bins(reco=True))
    plt.errorbar(energy_bins, effarea, yerr=sigma, marker='.')
    plt.ylabel('$\mathrm{Effective \ Area} \ [\mathrm{m^2}]$')
    plt.xlabel('$\log_{10}(E_{\mathrm{true}}/\mathrm{GeV})$')
    plt.title(r'ShowerLLH - IT73 - {} LLH bins'.format(opts['bintype']))
    # plt.xlim([5.5, 9.5])
    outfile = opts['outdir'] + \
        'effarea_vs_energy_{}.png'.format(opts['bintype'])
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

    data = load_sim(config=args.config, bintype=args.bintype)
    cuts = data['cuts']['llh']

    energyres(data, cuts, **opts)
    coreres(data, cuts, **opts)
    eres_position(data, cuts, **opts)
    LLHenergy_MCenergy(data, cuts, **opts)
    LLHzenith_MCzenith(data, cuts, **opts)
    effarea(data, cuts, **opts)
    # event_dist(data)
    # energy_dist(data, emin=5., emax=6.)
    # energy_dist(data,cuts)
