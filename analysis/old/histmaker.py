#!/usr/bin/env python

from numpy import *
import glob, os, pickle, unfold, powerFit
from llhtools import *
from data import NumToFlux as n2f
from load_data import load_data
from load_sim import load_sim
from eff import getEff
from prob import getProbs
from duration import duration

def histWriter(d, s, out='test'):

    ##=========================================================================
    ## Basic setup

    # Starting information
    r = log10(d['ML_energy'])
    t = duration(d)
    Emids = getEmids()
    w = d['weights']
    cutName = 'llh'
    dcut, scut = d['cuts'][cutName], s['cuts'][cutName]
    eList = ['p', 'f']

    # Get probabilities for unfolding
    p = getProbs(s, scut)
    st = len(Emids) - len(p['Rf|Tf'][0])
    Emids = Emids[st:]

    # Relative errors
    fl = open('unfold_err2.pkl', 'rb')
    chi2, unrel = pickle.load(fl)
    fl.close()

    effarea, sigma, effrel = getEff(s, scut, smooth=True)
    effarea, sigma, effrel = effarea[st:], sigma[st:], effrel[st:]

    ##=========================================================================
    ## Make histograms

    q = {}
    q['Emids'] = Emids
    q['flux'], q['err'], q['chi2'] = {},{},{}
    d['cuts']['none'] = array([True for i in range(len(dcut))])
    nameList = ['none', 'left', 'right', 'odds', 'evens']
    cutList = [d['cuts'][name] for name in nameList]
    niter = 30

    for k in range(len(cutList)):

        name = nameList[k]
        c0 = dcut * cutList[k]
        q['chi2'][name] = []

        # Get counts and starting probabilities
        N_passed = Nfinder(r, c0, w=w).sum()
        N = {}
        for e in eList:
            N[e] = Nfinder(r, c0*d[e], w=w)
            p['R'+e] = N[e] / N_passed
            p['T'+e] = powerFit.powerFit(-2.7, st=st)

        # Bayesian unfolding
        counts, flux, relerr, err = {},{},{},{}
        for i in range(niter):

            # Calculate unfolded fluxes, errors, and chi sqaured values
            old = sum([p['T'+e] for e in eList], axis=0)
            p = unfold.unfold(p)
            new = sum([p['T'+e] for e in eList], axis=0)
            q['chi2'][name].append( 1./(len(Emids)+1) * 
                    sum(((new-old) / unrel[i])**2))

            counts['All'] = new * N_passed
            for e in eList:
                counts[e] = p['T'+e] * N_passed

            for e in eList + ['All']:
                relerr[e] = sqrt(1/counts[e] + effrel**2 + unrel[i]**2)
                flux[e] = n2f(counts[e], effarea, t, st)
                err[e] = flux[e] * relerr[e]
                # Write to dictionary
                q['flux'][name+'_'+e+'_'+str(i+1)] = flux[e]
                q['err'][name+'_'+e+'_'+str(i+1)] = err[e]

                if i < niter-1:
                    p['T'+e] = smoother(p['T'+e])

        # Original (not unfolded) spectrum
        O_counts = (sum([N[e] for e in eList], axis=0))[st:]
        O_relerr = sqrt(1/O_counts + effrel**2)
        q['flux'][name+'_O'] = n2f(O_counts, effarea, t, st)
        q['err'][name+'_O'] = q['flux'][name+'_O'] * O_relerr

    ##=========================================================================
    ## Write to file

    print 'Writing to file...'
    outFile = 'hists/'+out+'_hists.npy'
    save(outFile, q)


if __name__ == "__main__":

    config = 'IT73'
    prefix = '/net/user/fmcnally/ShowerLLH/'+config+'_data/'

    # Load simulation
    print 'Loading simulation...'
    s = load_sim(config)

    # Load data
    fileList = glob.glob(prefix + 'DataPlot_20*.npy')
    ymList = [os.path.basename(f)[9:15] for f in fileList]
    ymList = list(set(ymList))      # Remove duplicates
    ymList.sort()

    for yyyymm in ymList:
        print 'Loading', yyyymm
        d = load_data(config, yyyymm)
        histWriter(d, s, yyyymm=yyyymm)








