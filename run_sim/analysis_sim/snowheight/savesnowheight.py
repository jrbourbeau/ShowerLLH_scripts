#!/usr/bin/env python

from icecube import icetray, phys_services, dataio
from icecube import dataclasses as dc
from I3Tray import I3Tray
import numpy as np
import argparse
from usefulFunctions import checkdir

class SaveSnowHeight(icetray.I3Module):
    def __init__(self, context):
        icetray.I3Module.__init__(self, context)
        self.AddOutBox('OutBox')
        self.AddParameter('outFile', 'Input name for output file', 'test')

    def Configure(self):
        self.outFile = self.GetParameter('outFile')
        pass

    def Geometry(self, frame):
    # Load I3Geometry to be used later
        self.geometry = frame['I3Geometry']
        self.PushFrame(frame)

    def DetectorStatus(self, frame):
    # Load I3DetectorStatus to gather positions and snow heights
    # for active tanks
        self.om2index = {}
        self.tankpositions = []
        self.snowheight = []
        self.status = frame['I3DetectorStatus']
        self.dom = self.status.dom_status
        index = 0
        for number, station in self.geometry.stationgeo:
            for tank in station:
                omList = tank.omkey_list
                if not any([om in self.dom.keys() for om in omList]):
                    continue
                for om in omList:
                    self.om2index[om] = index
                self.tankpositions.append(dc.i3position_to_tuple(tank.position))
                self.snowheight.append(tank.snowheight)
                index += 1

        if len(self.tankpositions) < 5: # or some arbitrary low number
            raise ValueError("Not enough tanks found!")

        self.snowheight = np.array(self.snowheight)
        self.PushFrame(frame)

    def Finish(self):
        if self.outFile:
            d = {}
            d['positions']   = self.tankpositions
            d['snowheights'] = self.snowheight
            checkdir(self.outFile)
            np.save(self.outFile, d)
        return

if __name__ == "__main__":

    # Global variables setup for path names
    # my.setupShowerLLH(verbose=False)

    p = argparse.ArgumentParser(
            description='Builds binned histograms for use with ShowerLLH')
    p.add_argument('-f', '--file', dest='file',
            help='Input filelist to run over')
    p.add_argument('-o', '--outFile', dest='outFile',
            help='Output filename')
    args = p.parse_args()

    # Execute
    tray = I3Tray()
    tray.Add('I3Reader', FileName=args.file)
    tray.Add(SaveSnowHeight,
        outFile=args.outFile)
    tray.Execute()
    tray.Finish()
