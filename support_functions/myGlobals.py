#!/usr/bin/env python

def setupGlobals(verbose=True):

    globalVals = globals().keys()
    global npx4, env, offline
    global llh_home, llh_data, llh_resource
    offline = '/data/user/jbourbeau/metaprojects/icerec/V05-00-00'
    env = '/data/user/jbourbeau/metaprojects/icerec/V05-00-00/build/env-shell.sh'

    llh_home = '/home/jbourbeau/ShowerLLH_scripts'
    llh_data = '/data/user/jbourbeau/ShowerLLH'
    llh_resource = '/data/user/jbourbeau/ShowerLLH/resources'
    npx4 = llh_home + '/support_functions/npx4'

    # Option to print changes to global variables
    if verbose:
        print 'New global variables:'
        for key in globals().keys():
            if key not in globalVals:
                print '  %s = %s' % (key, globals()[key])
