#!/usr/bin/env python
"""
@file    runner.py
@author  Lena Kalleske
@author  Daniel Krajzewicz
@author  Michael Behrisch
@author  Jakob Erdmann
@date    2009-03-26
@version $Id: runner.py 18096 2015-03-17 09:50:59Z behrisch $

Tutorial for traffic light control via the TraCI interface.

SUMO, Simulation of Urban MObility; see http://sumo.dlr.de/
Copyright (C) 2009-2015 DLR/TS, Germany

This file is part of SUMO.
SUMO is free software; you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation; either version 3 of the License, or
(at your option) any later version.
"""

import os
import sys
import optparse
import subprocess
import random

# we need to import python modules from the $SUMO_HOME/tools directory
try:
    sys.path.append(os.path.join(os.path.dirname(
        __file__), '..', '..', '..', '..', "tools"))  # tutorial in tests
    sys.path.append(os.path.join(os.environ.get("SUMO_HOME", os.path.join(
        os.path.dirname(__file__), "..", "..", "..")), "tools"))  # tutorial in docs
    from sumolib import checkBinary
except ImportError as e:
    print e.message
    sys.exit(
        "please declare environment variable 'SUMO_HOME' as the root directory of your sumo installation (it should contain folders 'bin', 'tools' and 'docs')")

import traci

PORT = 8873

NSGREEN = "GGrGGr"
NSYELLOW = "yyrGGr"
WEGREEN = "rrrGGG"
WEYELLOW = "rryGGy"

PROGRAM = [WEYELLOW, WEYELLOW, WEYELLOW, NSGREEN, NSGREEN, NSGREEN,
           NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSGREEN, NSYELLOW, NSYELLOW, WEGREEN]


if not traci.isEmbedded():
    N = 9000
    pAB = 1. / 10
    pAC = 1. / 15
    pBA = 1. / 20
    pBC = 1. / 25
    pCA = 1. / 30
    pCB = 1. / 35
    routes = open("map.rou.xml", "w")
    prior_v = open("prior_log.txt","w")
    print >> routes, """<routes>
    <vType id="typeAB" accel="0.8" decel="4.5" sigma="0.5" length="5" minGap="2.5" maxSpeed="16.67" guiShape="passenger"/>

    <route id="AB" edges="17355127 17362933#0 -17357053" />
    <route id="AC" edges="17355127 17362933#0 17362933#1 159509942" />
    <route id="BC" edges="17357053 17362933#1 159509942" />
    <route id="BA" edges="17357053 17362933#1 17362933#2 17362933#3 -17355127" />
    <route id="CA" edges="159509935 17362933#3 -17355127" />
    <route id="CB" edges="159509935 17362933#3 17362933#0 -17357053" />"""
    lastVeh = 0
    vehNr = 0
    for i in range(N):
        if random.uniform(0, 1) < pAB:
            print >> routes, '    <vehicle id="AB_%i" type="typeAB" route="AB" depart="%i" color="1,0,0" />' % (vehNr, i)
            vehNr += 1
            lastVeh = i
        if random.uniform(0, 1) < pAC:
            print >> routes, '    <vehicle id="AC_%i" type="typeAB" route="AC" depart="%i" color="0,1,0" />' % (vehNr, i)
            vehNr += 1
            lastVeh = i
        if random.uniform(0, 1) < pBA:
            print >> routes, '    <vehicle id="BA_%i" type="typeAB" route="BA" depart="%i" />' % (vehNr, i)
            vehNr += 1
            lastVeh = i
        if random.uniform(0, 1) < pBC:
            print >> routes, '    <vehicle id="BC_%i" type="typeAB" route="BC" depart="%i" />' % (vehNr, i)
            vehNr += 1
            lastVeh = i
        if random.uniform(0, 1) < pCA:
            print >> routes, '    <vehicle id="CA_%i" type="typeAB" route="CA" depart="%i" />' % (vehNr, i)
            vehNr += 1
            lastVeh = i
        if random.uniform(0, 1) < pCB:
            print >> routes, '    <vehicle id="CB_%i" type="typeAB" route="CB" depart="%i" />' % (vehNr, i)
            vehNr += 1
            lastVeh = i
    print >> routes, "</routes>"
    routes.close()

    sumoBinary = 'sumo-gui'
    sumoConfig = "map.sumo.cfg"
    if len(sys.argv) > 1:
        retCode = subprocess.call("%s -c %s --python-script %s" % (sumoBinary, sumoConfig, __file__), shell=True, stdout=sys.stdout)
        sys.exit(retCode)
    else:
        sumoProcess = subprocess.Popen("%s -c %s" % (sumoBinary, sumoConfig), shell=True, stdout=sys.stdout)
        traci.init(PORT)


step = 0
max_d = 0
i=0
edge_density = []
edge_Ids=traci.edge.getIDList()
traffic_lights=traci.trafficlights.getIDList()
time=traci.simulation.getCurrentTime()
print >>log , "Time: ", time, "Traffic Lights: " , traffic_lights, "\n"
print >>log , "Edges are : ", edge_Ids, "\n"
traci.trafficlights.setRedYellowGreenState("179722916", "rrrrrr")

while step == 0 or traci.simulation.getMinExpectedNumber()>0:
    traci.simulationStep()
    for i in xrange(15):
        vehicle_Ids=traci.edge.getLastStepVehicleIDs(edge_Ids[i])
        for vehicle in vehicle_Ids:
            time=traci.simulation.getCurrentTime()
            roadID=traci.vehicle.getRoadID(vehicle)
            typeID=traci.vehicle.getTypeID(vehicle)
            speed=traci.vehicle.getMaxSpeed(vehicle)
            accln=traci.vehicle.getAccel(vehicle)
            decel=traci.vehicle.getDecel(vehicle)
            print >>log, "Time: ", time, "Edge: ", edge_Ids[i], "Vehicle ID: ", vehicle, "Road ID: ", roadID, "Speed: ", speed, "Type: ", typeID, "\n"
    d_1=traci.edge.getLastStepVehicleNumber("17362933#3")
    d_2=traci.edge.getLastStepVehicleNumber("17355127")
    edge_density.append(d_1)
    edge_density.append(d_2)
    max_d= max(edge_density)

    if(max_d ==d_1):
        traci.trafficlights.setRedYellowGreenState("179722916", "rrrGGG")

    else:
        if(max_d ==d_2):
            traci.trafficlights.setRedYellowGreenState("179722916", "GGrGGr")


        step += 1

traci.close()
sys.stdout.flush()

