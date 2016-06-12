#!/usr/bin/env python

from icecube import icetray, dataio, toprec
from icecube import dataclasses as dc

##============================================================================
## Generally useful modules

""" Output number of stations triggered in IceTop """
def GetStations(frame, InputITpulses, output):
    nstation = 0
    if InputITpulses in frame:
        vemPulses = frame[InputITpulses]
        if vemPulses.__class__ == dc.I3RecoPulseSeriesMapMask:
            vemPulses = vemPulses.apply(frame)
        stationList = set([pulse.key().string for pulse in vemPulses])
        nstation = len(stationList)
    frame[output] = icetray.I3Int(nstation)

##============================================================================
## Potentially outdated modules -- LOOK INTO THIS MORE

""" Remove old IceTop reconstructions from nullsplit frames """
def PruneIceTop(frame, it_stream):

    if frame['I3EventHeader'].sub_event_stream != it_stream:
        frame.Delete('ShowerCOG')
        frame.Delete('ShowerCombined')
        frame.Delete('ShowerCombinedParams')
        frame.Delete('ShowerPlane')
        frame.Delete('ShowerPlaneParams')


""" Rename LaputopSmall as Laputop
    WARN: Not sure if this is correct use of isSmall...
"""
def moveSmall(frame):
    isSmall = False
    if frame.Has('IsSmallShower'):
        if frame['IsSmallShower'].value == True:
            isSmall = True
    elif frame.Has('SmallShowerFilterPassed'):
        isSmall = True
    if isSmall:
        frame.Delete('LaputopStandard')
        frame.Delete('LaputopStandardParams')
        frame['LaputopStandard'] = frame['LaputopSmallShower']
        frame['LaputopStandardParams'] = frame['LaputopSmallShowerParams']

##============================================================================
## Modules used for ShowerLLH cuts

""" Move MCPrimary from P to Q frame """
class moveMCPrimary(icetray.I3PacketModule):

    def __init__(self, ctx):
        icetray.I3PacketModule.__init__(self, ctx, icetray.I3Frame.DAQ)
        self.AddOutBox("OutBox")

    def Configure(self):
        pass

    def FramePacket(self, frames):
        qframe = frames[0]
        if len(frames) <= 1 or 'MCPrimary' in qframe:
            for frame in frames:
                self.PushFrame(frame)
            return

        # prim, prim_info = 0,0
        pframes = frames[1:]
        primary_found = False
        for frame in pframes:
            if 'MCPrimary' in frame:
                # if prim != 0:
                if primary_found:
                    raise RuntimeError("MCPrimary in more than one P frame!")
                prim = frame['MCPrimary']
                primary_found = True
                #prim_info = frame['MCPrimaryInfo']
                del frame['MCPrimary']
                del frame['MCPrimaryInfo']

        qframe['MCPrimary'] = prim
        #qframe['MCPrimaryInfo'] = prim_info

        self.PushFrame(qframe)
        for frame in pframes:
            self.PushFrame(frame)


""" Find the loudest station and station with loudest tank """
class FindLoudestStation(icetray.I3Module):

    def __init__(self, context):
        icetray.I3Module.__init__(self, context)
        self.AddParameter('InputITpulses','Which IceTop Pulses to use',0)
        self.AddParameter('SaturationValue','Saturation value (VEM)',600)
        self.AddParameter('output','Name of vector with saturated stations','')
        self.AddOutBox('OutBox')

    def Configure(self):
        self.pulses = self.GetParameter('InputITpulses')
        self.saturation = self.GetParameter('SaturationValue')
        self.outputName = self.GetParameter('output')

    def Physics(self, frame):

        if self.pulses not in frame:
            self.PushFrame(frame)
            return

        vem = frame[self.pulses]
        if vem.__class__ == dc.I3RecoPulseSeriesMapMask:
            vem = vem.apply(frame)

        loudPulse, loudStaCharge, avStaCharge = 0,0,0
        loudStation1, loudStation2, loudStation3 = 0,0,0
        prevSta, staCharge = 0,0
        sat_stations = []

        for key, series in vem:
            for tank in series:             #will be one waveform anyway

                # if NaN : rely on waveform in other tank, so skip
                if tank.charge != tank.charge:
                    continue

                # Keep track of largest single pulse
                if tank.charge > loudPulse:
                    loudPulse = tank.charge
                    loudStation1 = key.string

                # Calculate total station charge
                if key.string != prevSta:
                    staCharge = tank.charge
                else:
                    staCharge += tank.charge

                if staCharge > loudStaCharge:
                    loudStaCharge = staCharge
                    loudStation2 = key.string
                prevSta = key.string

                # LG saturaton bookkeeping :
                if tank.charge > self.saturation:
                    sat_stations.append(key.string)

        # Write to frame
        frame['StationWithLoudestPulse'] = dc.I3Double(loudStation1)
        frame['LoudestStation'] = dc.I3Double(loudStation2)
        # Option for writing saturated stations
        if self.outputName != '':
            sat_stations = set(sat_stations)
            sta_list = dc.I3VectorInt()
            for sta in sat_stations:
                sta_list.append(sta)
            frame[self.outputName] = sta_list

        self.PushFrame(frame)

# Is the loudest station OR any saturated station on the edge
class LoudestStationOnEdge(icetray.I3Module):

    def __init__(self, context):
        icetray.I3Module.__init__(self, context)
        self.AddParameter('InputLoudestStation',
                'Loudest Station (or I3Vector of saturated stations)', 0)
        self.AddParameter('config','Which detectorConfig? IT40/59/73/81? ',0)
        self.AddParameter('output','Output bool in the frame',0)
        self.AddOutBox('OutBox')

    def Configure(self):
        self.loudest = self.GetParameter('InputLoudestStation')
        self.config = self.GetParameter('config')
        self.outputName = self.GetParameter('output')
        IT40edges  = [21,30,40,50,59,67,74,73,72,78,77,76,75,68,60,52,53]
        IT40edges += [44,45,46,47,38,29]
        IT59edges  = [2,3,4,5,6,13,21,30,40,50,59,67,74,73,72,78,77,76,75]
        IT59edges += [68,60,52,53,44,45,36,26,17,9]
        IT73edges  = [2,3,4,5,6,13,21,30,40,50,59,67,74,73,72,78,77,76,75]
        IT73edges += [68,60,51,41,32,23,15,8]
        IT81edges  = [2,3,4,5,6,13,21,30,40,50,59,67,74,73,72,78,77,76,75]
        IT81edges += [68,60,51,41,31,22,14,7,1]
        self.edgeDict = dict({'IT40':IT40edges, 'IT59':IT59edges})
        self.edgeDict.update({'IT73':IT73edges, 'IT81':IT81edges})

    def Physics(self, frame):

        if self.loudest not in frame:
            self.PushFrame(frame)
            return

        loud = frame[self.loudest]  ## is an I3Double or I3VectorInt
        edge = False
        if self.config not in self.edgeDict.keys():
            raise RuntimeError('Unknown config, Please choose from IT40-IT81')

        edgeList = self.edgeDict[self.config]

        # Check if loudest station on edge
        if loud.__class__ == dc.I3Double:
            if loud.value in edgeList:
                edge = True
        # Check if any saturated stations on edge
        elif loud.__class__ == dc.I3VectorInt:
            for station in loud:
                if station in edgeList:
                    edge = True

        output = icetray.I3Bool(edge)
        frame[self.outputName] = output

        self.PushFrame(frame)


# Calculate the largest n pulses and neighbor to the largest one (Q1b)
class LargestTankCharges(icetray.I3Module):
    def __init__(self, context):
        icetray.I3Module.__init__(self, context)
        self.AddParameter('nPulses',
                'Book largest N pulses for TailCut (+neighbor of largest)',4)
        self.AddParameter('ITpulses','IT pulses Name',0)
        self.AddOutBox('OutBox')

    def Configure(self):
        self.nPulses = self.GetParameter('nPulses')
        self.recoPulses = self.GetParameter('ITpulses')
        self.counter=0

    def Physics(self, frame):

        if self.recoPulses not in frame:
            self.PushFrame(frame)
            return

        tank_map = frame[self.recoPulses]
        if tank_map.__class__ == dc.I3RecoPulseSeriesMapMask:
            tank_map = tank_map.apply(frame)

        # Build list of charges and corresponding om's
        charge_map = []
        for om, pulses in tank_map:
            for wave in pulses:
                # If nan, use charge in other tank as best approximation
                if wave.charge != wave.charge:
                    # Get neighboring charge
                    omList = [om1 for om1, pulses in tank_map if om1!=om]
                    stringList = [om1.string for om1 in omList]
                    try: index = stringList.index(om.string)
                    except ValueError:      # pulse cleaning removed one tank
                        continue
                    om_neighbor = omList[index]
                    pulses = tank_map[om_neighbor]
                    charge = pulses[0].charge
                else:
                    charge = wave.charge
                charge_map.append((charge, om))

        if len(charge_map) < 1:
            self.PushFrame(frame)
            return

        charge_map = sorted(charge_map, reverse=True)
        q1 = charge_map[0][0]
        q1_dom = charge_map[0][1]

        # Get charge in neighbor to largest pulse (Q1b)
        omList = [om1 for om1, pulses in tank_map if om1!=q1_dom]
        stringList = [om1.string for om1 in omList]
        if q1_dom.string in stringList:
            index = stringList.index(q1_dom.string)
            q1b_dom = omList[index]
            q1b = tank_map[q1b_dom][0].charge
            frame['Q1b'] = dc.I3Double(q1b)

        # Write charges to frame
        bookedN = 0
        while (bookedN < self.nPulses) and (bookedN < charge_map.__len__()):
            name = 'Q%i' % (bookedN+1)
            frame[name] = dc.I3Double(charge_map[bookedN][0])
            bookedN += 1

        self.PushFrame(frame)

##============================================================================
## Potentially useful

class ChangeSnowHeight(icetray.I3Module):
    def __init__(self, ctx):
        import csv
        icetray.I3Module.__init__(self,ctx)
        self.AddParameter('filename','Filename w/ snow values for each tank',
0)
        self.AddOutBox('OutBox')

    def Configure(self):
        self.snowfile = self.GetParameter('filename')
        self.newheights = self._readFile(self.snowfile)

    def Geometry(self, frame):
        if 'I3Geometry' in frame:
            geom = frame['I3Geometry']
            stageo = geom.stationgeo
            for e,st in stageo:
                updated_heights = dc.I3StationGeo()
                if not self.newheights.has_key(e):
                    print 'Did not find station', e, 'in new snowheight dict'
                    continue
                #ok we have I3TankGeo here... look it up
                ## assume first is A and second is B
                st[0].snowheight = max((self.newheights[e][0],0.))
                st[1].snowheight = max((self.newheights[e][1],0.))
                updated_heights.append(st[0])
                updated_heights.append(st[1])
                stageo[e] = updated_heights
            del frame['I3Geometry']
            frame['I3Geometry'] = geom
        else:
            print 'No geometry found'
        self.PushFrame(frame,'OutBox')

    def _readFile(self, filename):
        file = open(filename)
        ## error catching should go here...

        newheights = {}
        for row in csv.reader(file,delimiter=' '):
            # Deal with Takao's files:
            if len(row) > 1 :        ## skips first line
                height = float(row[len(row)-1])
                tank = row[0]
                station = int(tank[:2])
                id = tank[2]
                if station not in newheights:
                    newheights[station] = [0,0]
                if id == 'A':
                    newheights[station][0] = height
                elif id == 'B':
                    newheights[station][1] = height
                else:
                    print 'unknown tankid'
        return newheights
