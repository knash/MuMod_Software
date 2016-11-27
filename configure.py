
from classes import *
import sys, select, os, array
from array import array
import copy
#import ROOT
#from ROOT import TGraph

from optparse import OptionParser
parser = OptionParser()
parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default	=	'default',
dest	=	'setting',
help	=	'configuration setting ie default')


parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	1,
dest	=	'number',
help	=	'configuration number')

parser.add_option('-m', '--mpa', metavar='F', type='int', action='store',
default	=	0,
dest	=	'mpa',
help	=	'mpa to configure (0 for all)')

(options, args) = parser.parse_args()



a = uasic(connection="file://connections_MuMod.xml",device="board0")
mapsa = MAPSA(a)
read = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(read)


a._hw.getNode("Control").getNode("MPA_clock_enable").write(0x1)
a._hw.dispatch()

a._hw.getNode("Utility").getNode("CLKUTIL_freq").write(0x7)
a._hw.dispatch()
a._hw.getNode("Configuration_Left").getNode("flip").write(0x0)
a._hw.getNode("Configuration_Right").getNode("flip").write(0x0)
mpa_number = options.mpa
x=0
yy=0
verbose=True
matchedR = 0
shiftedR = 0
randomR = 0

matchedL = 0
shiftedL = 0
randomL = 0

count=0
if mpa_number ==0:

   while True:


	#time.sleep(.2)
	config = mapsa.config(Config=options.number,string=options.setting,njump=0)
	ff = x%220
	#yy+=1
	#config.modifypixel(x%24,'TRIMDACR',[(x%2)*31]*6)
	#if yy%2==0:
	x+=1


	#curs = config.upload(show = 1, UL = "Left")
	uplh = [0xffafafaf]
	for i in range(0,24):
		if i==23:
#			uplh.append(0xfafaf) 			
			uplh.append(0xf0000) 			
		else:
			uplh.append(0xf0000) 




	uplhshift = [(uplh[0]<<1)&(0xffffffff)]
	savebit = ((uplh[0]<<1)&(0x100000000))>>32
	for i in range(0,24):

		uplhshift.append((uplh[i+1]<<1)&(0xfffff))
		uplhshift[i+1]+=savebit
		savebit=((uplh[i+1]<<1)&(0x100000))>>16
		



	upll = [0x1]
	for i in range(0,24):
		upll.append(0x0) 

	curs = [uplh,uplh,uplh,uplh,uplh,uplh]
	curshift = [uplhshift,uplhshift,uplhshift,uplhshift,uplhshift,uplhshift]
	
	a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA1").getNode("config_1").writeBlock(curs[0])
	a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA2").getNode("config_1").writeBlock(curs[1])
	a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA3").getNode("config_1").writeBlock(curs[2])
	a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA4").getNode("config_1").writeBlock(curs[3])
	a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA5").getNode("config_1").writeBlock(curs[4])
	a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA6").getNode("config_1").writeBlock(curs[5])


	
		
	
	a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA1").getNode("config_1").writeBlock(curs[0])
	a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA2").getNode("config_1").writeBlock(curs[1])
	a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA3").getNode("config_1").writeBlock(curs[2])
	a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA4").getNode("config_1").writeBlock(curs[3])
	a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA5").getNode("config_1").writeBlock(curs[4])
	a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA6").getNode("config_1").writeBlock(curs[5])

	




	#curs = config.upload(show = 0, UL = "Right")
	
	#n=3
	#m=2
	n=3
	m=2
	c=0
	u=1

	#config.write(UL = "Left",n=n,m=m,c=c,u=u)
	#time.sleep(.01)
	config.write(UL = "Right",n=n,m=m,c=c,u=u)

	#time.sleep(.2)
	for c in range(1,4):
		a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA1").getNode("config_"+str(c)).writeBlock(curs[0])
		a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA2").getNode("config_"+str(c)).writeBlock(curs[1])
		a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA3").getNode("config_"+str(c)).writeBlock(curs[2])
		a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA4").getNode("config_"+str(c)).writeBlock(curs[3])
		a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA5").getNode("config_"+str(c)).writeBlock(curs[4])
		a._hw.getNode("Configuration_Right").getNode("Memory_DataConf").getNode("MPA6").getNode("config_"+str(c)).writeBlock(curs[5])

		a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA1").getNode("config_"+str(c)).writeBlock(curs[0])
		a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA2").getNode("config_"+str(c)).writeBlock(curs[1])
		a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA3").getNode("config_"+str(c)).writeBlock(curs[2])
		a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA4").getNode("config_"+str(c)).writeBlock(curs[3])
		a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA5").getNode("config_"+str(c)).writeBlock(curs[4])
		a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA6").getNode("config_"+str(c)).writeBlock(curs[5])


#	a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA1").getNode("config_1").writeBlock(upll)
#	a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA2").getNode("config_1").writeBlock(upll)
#	a._hw.getNode("Configuration_Left").getNode("Memory_DataConf").getNode("MPA3").getNode("config_1").writeBlock(upll)



	#time.sleep(.01)

	if verbose:
		print ""
		print ""
		print ""
		print ""

		print "run ", x

		print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
		print "Intermediate data"
	for i in range(1,2):
		for c in range(1,2):
       			readL = a._hw.getNode("Configuration_Left").getNode("Memory_OutConf").getNode("MPA"+str(i)).getNode("config_"+str(c)).readBlock(0x19)	
			a._hw.dispatch()

       			readR = a._hw.getNode("Configuration_Right").getNode("Memory_OutConf").getNode("MPA"+str(i)).getNode("config_"+str(c)).readBlock(0x19)	
			a._hw.dispatch()
			#print read
			#taco = []

			#print "read Left: " 
			#taco = []
			#for r in range(0,len(readL)):
			#	if r==0:
			#		taco.append(binary(readL[r]))
			#	else:
			#		taco.append(binary(readL[r])[12:])
			#tstr = ''
			#for t in taco:
			#	tstr+= t
			#print tstr



			if verbose:
				print "read Right: " 
				print 
			taco = []

			for r in range(0,len(readR)):
				if r==len(readR)-1:
					taco.append(binary(readR[-(r+1)]))
				else:
					taco.append(binary(readR[-(r+1)])[12:])
			tstr = ''
			for t in taco:
				tstr+= ';'
				tstr+= t
			if verbose:
				print tstr

	if verbose:
		print 'xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx'
		print "RUN ", x
		print
		print

	config.write(UL = "Right",n=n,m=m,c=c,u=u)

	if verbose:
		print "-------------------------------------------"

		print "Checking config"
	for i in range(1,4):
		count+=1
		if verbose:
			print "MPA ", i
			print '+++++'
		for c in range(1,2):
       			readL = a._hw.getNode("Configuration_Left").getNode("Memory_OutConf").getNode("MPA"+str(i)).getNode("config_"+str(c)).readBlock(0x19)	
			a._hw.dispatch()

       			readR = a._hw.getNode("Configuration_Right").getNode("Memory_OutConf").getNode("MPA"+str(i)).getNode("config_"+str(c)).readBlock(0x19)	
			a._hw.dispatch()
			#print read
			#taco = []

			taco = []

			for r in range(0,len(readL)):
				if r==len(readL)-1:
					taco.append(binary(readL[-(r+1)]))
				else:
					taco.append(binary(readL[-(r+1)])[12:])
			tstrL = ''
			for t in taco:
				tstrL+= ';'
				tstrL+= t
			if verbose:
				print "read Left: " 
				print tstrL
				print 





			taco = []

			for r in range(0,len(readR)):
				if r==len(readR)-1:
					taco.append(binary(readR[-(r+1)]))
				else:
					taco.append(binary(readR[-(r+1)])[12:])
			tstrR = ''
			for t in taco:
				tstrR+= ';'
				tstrR+= t
			if verbose:
				print "Read Right: " 
				print tstrR
				print 

				print "Uploaded: " 
			taco = []
			for r in range(0,len(curs[i-1])):
				if r==len(curs[i-1])-1:
					taco.append(binary(curs[i-1][-(r+1)]))
				else:
					taco.append(binary(curs[i-1][-(r+1)])[12:])
			tstr = ''
			for t in taco:
				tstr+= ';'
				tstr+= t
			if verbose:
				print tstr
				print "Shifted: " 
			Shiftmatch=False

			tacoshift = []
			for r in range(0,len(curshift[i-1])):
				if r==len(curshift[i-1])-1:
					tacoshift.append(binary(curshift[i-1][-(r+1)]))
				else:
					tacoshift.append(binary(curshift[i-1][-(r+1)])[12:])
			tstrshift = ''
			for t in tacoshift:
				
				tstrshift+= ';'
				tstrshift+= t

			if tstrshift==tstrR:
				shiftedR+=1
			elif tstr==tstrR:
				matchedR+=1
			else:
				randomR+=1

			if tstrshift==tstrL:
				shiftedL+=1
			elif tstr==tstrL:
				matchedL+=1
			else:
				randomL+=1
	
			if (count%100)==0:
				print 
				print "Right"
				print "shifted ",shiftedR
				print "matched ",matchedR
				print "random ",randomR
				print "total ",count 
				print "Left"
				print "shifted ",shiftedL
				print "matched ",matchedL
				print "random ",randomL
				print "total ",count 
			if verbose:	
				print tstrshift

				print "-------------------------------------------"

else:
	mpa_index = mpa_number-1
	
	mpa = []  
	for i in range(1,7):
		mpa.append(mapsa.getMPA(i))

	Confnum=options.number
	configarr = []

	writesetting=6-mpa_number

	print "Configuring MPA number " + str(mpa_number)

	curconf = mpa[mpa_index].config(xmlfile="data/Conf_"+options.setting+"_MPA"+str(mpa_number)+"_config"+str(Confnum)+".xml")
	
	print curconf.upload()
	a._hw.dispatch()
	
	print ""
	print "Done"
