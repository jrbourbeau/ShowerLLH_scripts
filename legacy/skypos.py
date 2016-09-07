#!/usr/bin/env python

import numpy as np
from icecube import astro
from icecube import dataclasses as dc

def getDecRA(d, verbose=True):

    if verbose:
        print('Calculating equatorial coordinates...')
    nevents = len(d['zenith'])
    t = dc.I3Time()
    # t = astro.Time()
    # local = astro.LocalCoord()
    # ice = astro.IceCubeDetector()
    ra, dec = np.zeros((2, nevents))

    for i in range(nevents):

        zen = d['zenith'][i]
        azi = d['azimuth'][i]
        mjd = d['mjd'][i]

        # t.set_mod_julian_time_double(mjd)
        # t.SetTime(mjd)
        # local.SetLocalRad(zen, azi)
        # eqApparent = ice.LocalToEquatorial(local, t)
        # dec[i] = eqApparent.GetDecRad()
        # ra[i]  = eqApparent.GetRaRad()
        ra, dec = astro.dir_to_equa(zen, azi, mjd)

    dec = np.pi/2. - dec
    while ra.min() < 0:
        ra[ra < 0] += 2*np.pi

    if verbose:
        print('Finished')

    return dec, ra

        
