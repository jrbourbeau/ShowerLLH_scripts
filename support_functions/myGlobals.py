#!/usr/bin/env python

def setupGlobals(verbose=True):

    globalVals = globals().keys()
    global npx4, env, offline
    npx4    = '/home/jbourbeau/npx4'
    env     = '/data/user/jbourbeau/offline/icerec/V04-08-00/build/env-shell.sh'
    offline = '/data/user/jbourbeau/offline/icerec/V04-08-00'

    # Option to print changes to global variables
    if verbose:
        print 'New global variables:'
        for key in globals().keys():
            if key not in globalVals:
                print '  %s = %s' % (key, globals()[key])


def setupShowerLLH(verbose=True):

    globalVals = globals().keys()
    global llh_home, llh_data, llh_resource
    llh_home     = '/home/jbourbeau/showerllh'
    llh_data     = '/data/user/jbourbeau/showerllh'
    llh_resource = '/data/user/jbourbeau/showerllh/resources'

    # Option to print changes to global variables
    if verbose:
        print 'New global variables:'
        for key in globals().keys():
            if key not in globalVals:
                print '  %s = %s' % (key, globals()[key])
