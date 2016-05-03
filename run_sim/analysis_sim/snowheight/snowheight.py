#!/usr/bin/env python

import numpy as np
import matplotlib.pyplot as plt
import argparse
from usefulFunctions import checkdir
import colormaps as cmaps
from plotFunctions import cmap_discretize

if __name__ == "__main__":

    # Global variables setup for path names
    # my.setupShowerLLH(verbose=False)

    p = argparse.ArgumentParser(
            description='Builds binned histograms for use with ShowerLLH')
    p.add_argument('-f', '--infile', dest='infile',
            help='Input filelist to run over')
    p.add_argument('-o', '--outfile', dest='outfile',
            help='Output filename')
    args = p.parse_args()
    opts = vars(args).copy()

    # Extract tank position and snoweight information
    data = np.load(opts['infile'])
    data = data.item()
    positions = data['positions']
    x,y,z = np.transpose(positions)
    snowheights = data['snowheights']
    #Snow bins in meters
    bins = np.array([0.0, .001, .5, .85])
    bins = np.append(bins, np.inf)

    # fig = plt.figure()
    # ax = plt.gca()
    fig, ax = plt.subplots(1,1)
    # cb = fig.colorbar(ax.get_images()[0], ax=ax)
    # colormap = plt.cm.jet
    colormap = cmaps.plasma
    # colormap = cmap_discretize(plt.cm.jet,bins)
    # colormap = cmaps.viridis
    # cb.set_label("Foo", labelpad=-1)
    sc = plt.scatter(x,y,s=40,c=snowheights,alpha=0.9,cmap=colormap)
    plt.colorbar(sc)
    tPars = {'fontsize':16}
    plt.title('Snow height on IceTop tanks',**tPars)
    ax.set_xlabel(r'X [m]', **tPars)
    ax.set_ylabel(r'Y [m]',**tPars)
    ax.set_xlim(-650,650)
    # plt.show()
    # plt.legend()
    outfile = '/home/jbourbeau/public_html/figures/snowheights/{}.png'.format(opts['outfile'])
    # checkdir(outfile)
    plt.savefig(outfile, dpi=300, bbox_inches='tight')
