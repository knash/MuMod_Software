
from classes import *
import sys, select, os, array
from array import array
#import ROOT
#from ROOT import TGraph

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default	=	'none',
dest	=	'setting',
help	=	'setting ie on or off')

(options, args) = parser.parse_args()

a = uasic(connection="file://connections_MuMod.xml",device="board0")
mapsa = MAPSA(a)
read = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(hex(read))

a._hw.getNode("Control").getNode("logic_reset").write(0x1)
a._hw.dispatch()



a._hw.getNode("Control").getNode("testbeam_mode").write(0x0)
a._hw.getNode("Control").getNode("testbeam_clock").write(0x0)
#a._hw.getNode("Control").getNode("MPA_clock_enable").write(0x1)
#a._hw.dispatch()
a._hw.getNode("Utility").getNode("CLKUTIL_freq").write(0x7)
a._hw.dispatch()
if options.setting=='on':
	print "Voltage on..."


	print "VDDPST on"
	mapsa.VDDPST_on()				
	time.sleep(.1)
	print "DVDD on"
	mapsa.DVDD_on()
	time.sleep(.1)
	print "AVDD on"
	mapsa.AVDD_on()
	time.sleep(.1)
	print "PVDD on"
	mapsa.PVDD_on()
	time.sleep(.1)

elif options.setting=='off':
	print "Voltage off..."

	print "PVDD off"
	mapsa.PVDD_off()
	time.sleep(.1)
	print "AVDD off"
	mapsa.AVDD_off()
	time.sleep(.1)
	print "DVDD off"
	mapsa.DVDD_off()
	time.sleep(.1)
	print "VDDPST off"
	mapsa.VDDPST_off()
	time.sleep(.1)
else:
	print "Please select a setting"
print ""
print "Done"
