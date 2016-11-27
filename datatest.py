
from classes import *
import elementtree.ElementTree 
from xml.dom import minidom
from elementtree.ElementTree import Element, SubElement, Comment
#import ROOT
#from ROOT import TGraph
import sys, select, os, array
from array import array
import ROOT
from ROOT import TGraph, TCanvas, gPad, TFile

import numpy as np

import matplotlib.pyplot as plt
from matplotlib.pyplot import show, plot

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default	=	'calibrated',
dest	=	'setting',
help	=	'settings ie default, calibration, testbeam etc')
(options, args) = parser.parse_args()



a = uasic(connection="file://connections_MuMod.xml",device="board0")
mapsa = MAPSA(a)
read = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(read)


#a._hw.getNode("Control").getNode("logic_reset").write(0x1)
#a._hw.dispatch()
a._hw.getNode("Control").getNode("MPA_clock_enable").write(0x1)
a._hw.dispatch()


smode = 0x0

configR = mapsa.config(Config=1,string=options.setting+"Right",njump=0)
configR.modifyperiphery('OM',[3,3,3,3,3,3])
configR.upload(show = 1, UL = "Right")


configL = mapsa.config(Config=1,string=options.setting+"Left",njump=0)
configL.modifyperiphery('OM',[3,3,3,3,3,3])
configL.upload(show = 1, UL = "Left")

n=3
m=2
c=0
u=1




time.sleep(.01)
configR.write(UL = "Right",n=n,m=m,c=c,u=u)

x=0
snum = 100
sdel = 0xFFF
slen = 0xF
sdist = 0xF
configR.modifyperiphery('THDAC',[130,130,130,130,130,130])
configL.modifyperiphery('THDAC',[130,130,130,130,130,130])


y=0
mapsa.daq().Strobe_settings(snum,sdel,slen,sdist,1)
rt =0 
while True:
	rt+=1
	#print rt%4

	if x%250==0:
		x=0
	x+=1
	y+=1
	if y%50==0:
		print y
	time.sleep(.01)
	print x%250
	configR.modifyperiphery('THDAC',[x%250]*6)
	configR.modifyperiphery('CALDAC',[100]*6) 
	configR.upload(show = 0, UL = "Right")


	#print "--------"
	#print "THDAC ",x%250



	time.sleep(.01)
	mapsa.daq().Sequencer_init(smode,3000000)
	time.sleep(.01)
	#print "xxx"
	print "Right"
	pix,mem = mapsa.daq().read_data(buffer_num=1,UL="Right",nmpa =3)
	#print pix
	for p in pix:
		p.pop(0)
		p.pop(0)
		print p

	for i in range(0,3):
		if mem[i][0]!='000000000000000000000000000000000000000000000000000000000000000000000000':
			print "MPA: ",i
			print mem[i][0]
			print mem[i][1]
			print mem[i][2]




	print "xxx"
	print "Left"


	configL.modifyperiphery('THDAC',[x%250]*6)
	configL.modifyperiphery('CALDAC',[100]*6) 
	configL.upload(show = 0, UL = "Left")

	#configL.write(UL = "Left",n=n,m=m,c=c,u=u)
	pix,mem = mapsa.daq().read_data(buffer_num=1,UL="Left",nmpa =3)
	#print pix
	for p in pix:
		p.pop(0)
		p.pop(0)
		print p
	for i in range(0,3):

		if mem[i][0]!='000000000000000000000000000000000000000000000000000000000000000000000000':
			print "MPA: ",i
			print mem[i][0]
			print mem[i][1]
			print mem[i][2]




	#print mem[1][2]
	#print mem[1][3]
	#print mem[1][4]
	#print mem[1][5]
	#print mem[1][6]

	#print "L"
	#pix,mem = mapsa.daq().read_data(buffer_num=1,UL="Left",nmpa =1)
	#for p in pix:
	#	print p 
	configR.write(UL = "Right",n=n,m=m,c=c,u=u)
