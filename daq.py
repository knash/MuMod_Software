from classes import *
import elementtree.ElementTree 
from xml.dom import minidom
from elementtree.ElementTree import Element, SubElement, Comment
import ROOT
from ROOT import TH2F, TCanvas, TTree, TBranch, TFile
#from ROOT import TGraph
import sys, select, os, array,subprocess
from array import array
#import ROOT
#from ROOT import TGraph
import datetime
saveout = sys.stdout
from optparse import OptionParser
parser = OptionParser()

parser.add_option('-s', '--setting', metavar='F', type='string', action='store',
default	=	'default',
dest	=	'setting',
help	=	'settings ie default,  testbeam etc')

parser.add_option('-C', '--calib', metavar='F', type='string', action='store',
default	=	'False',
dest	=	'calib',
help	=	'calibration')

parser.add_option('-r', '--readout', metavar='F', type='string', action='store',
default	=	'both',
dest	=	'readout',
help	=	'readout which data ie counters, memory, both')

parser.add_option('-f', '--format', metavar='F', type='string', action='store',
default	=	'noprocessing',
dest	=	'format',
help	=	'memout format noprocessing, stubfinding, centroid, stripemulator ')

parser.add_option('-m', '--mpa', metavar='F', type='int', action='store',
default	=	1,
dest	=	'mpa',
help	=	'mpa to configure (0 for all)')



parser.add_option('-c', '--charge', metavar='F', type='int', action='store',
default	=	0,
dest	=	'charge',
help	=	'Charge for caldac')

parser.add_option('-t', '--thresh', metavar='F', type='int', action='store',
default	=	90,
dest	=	'thresh',
help	=	'threshold')


parser.add_option('-T', '--testclock', metavar='F', type='string', action='store',
default	=	'glib',
dest	=	'testclock',
help	=	'test beam clock')



parser.add_option('-n', '--number', metavar='F', type='int', action='store',
default	=	0x0,
dest	=	'number',
help	=	'number of calcstrobe pulses to send')




parser.add_option('-x', '--record', metavar='F', type='string', action='store',
default	=	'True',
dest	=	'record',
help	=	'record this daq cycle')

parser.add_option('-y', '--daqstring', metavar='F', type='string', action='store',
default	=	'none',
dest	=	'daqstring',
help	=	'string to append on daq folder name')

parser.add_option('-z', '--monitor', metavar='F', type='string', action='store',
default	=	'False',
dest	=	'monitor',
help	=	'start event monitor in background')


parser.add_option('-w', '--shutterdur', metavar='F', type='int', action='store',
default	=	0xFFFFF,
dest	=	'shutterdur',
help	=	'shutter duration')


parser.add_option('-v', '--skip', metavar='F', type='string', action='store',
default	=	'True',
dest	=	'skip',
help	=	'skip zero counts')

parser.add_option('-u', '--autospill', metavar='F', type='string', action='store',
default	=	'True',
dest	=	'autospill',
help	=	'write every spill')

parser.add_option('-N', '--norm', metavar='F', type='string', action='store',
default	=	'False',
dest	=	'norm',
help	=	'use normalization mpa scheme')

parser.add_option('-D', '--direction', metavar='F', type='string', action='store',
default	=	'glib',
dest	=	'direction',
help	=	'strip direction (glib or mpa)')

parser.add_option('-L', '--loops', metavar='F', type='int', action='store',
default	=	-1,
dest	=	'loops',
help	=	'number of daq loops')


parser.add_option('-p', '--phase', metavar='F', type='int', action='store',
default	=	0,
dest	=	'phase',
help	=	'beam phase offset')

parser.add_option('-j', '--njump', metavar='F', type='int', action='store',
default	=	0,
dest	=	'njump',
help	=	'Number of MPAs that are jumped')


(options, args) = parser.parse_args()

sys.stdout = saveout


daqver=1



a = uasic(connection="file://connections_MuMod.xml",device="board0")
mapsa = MAPSA(a)
firmver = a._hw.getNode("Control").getNode('firm_ver').read()
a._hw.dispatch()
print "Running firmware version " + str(hex(firmver))


sdur = options.shutterdur

snum = options.number
sdel = 0xFF
slen = 0xF
sdist = 0xFF

njump = options.njump


formarr = ['stubfinding','stripemulator' ,'centroid','noprocessing']
memmode = formarr.index(options.format)

#a._hw.getNode("Control").getNode("logic_reset").write(0x1)
#a._hw.dispatch()
a._hw.getNode("Control").getNode("MPA_clock_enable").write(0x1)
a._hw.dispatch()

mpa_number = options.mpa
mpa_index = mpa_number-1
nmpas=1


mpa = []  
for i in range(1,7):
		mpa.append(mapsa.getMPA(i))



rbuffer=1
timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")

if options.daqstring!='':
	dstr= '_'+options.daqstring

foldername = 'daqout_'+options.setting+'_'+options.format+'_'+timestr+dstr


CE=0
if options.calib == 'True':
	CE=1
if options.readout=='both':
	AR=1
	SR=1
	readmode = 0x1
if options.readout=='counters':
	AR=1
	SR=0
	readmode = 0x0
if options.readout=='memory':
	AR=0
	SR=1
	readmode = 0x1

shutters=0

cntsperspill = 0.
Startspill=True


if options.norm == 'False':
	thdac = [options.thresh,options.thresh,options.thresh,options.thresh,options.thresh,options.thresh]
else:
	thdac = [options.thresh,90,options.thresh,90,options.thresh,90]


n=6
m=5
c=0
u=1


Endloop = False
spillnumber = 0
#ModuleMode
#confdict = {'OM':[1,1,1,0,0,0],'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[1]*6,'ARL':[AR]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[1]*6,'ARR':[AR]*6,'CER':[CE]*6,'SP':[1]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
confdict = {'OM':[memmode]*6,'RT':[0]*6,'SCW':[0]*6,'SH2':[0]*6,'SH1':[0]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'PML':[1]*6,'ARL':[AR]*6,'CEL':[CE]*6,'CW':[0]*6,'PMR':[1]*6,'ARR':[AR]*6,'CER':[CE]*6,'SP':[1]*6,'SR':[SR]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
#confdict = {'OM':[memmode]*6,'THDAC':thdac,'CALDAC':[options.charge]*6,'ARL':[AR]*6,'CEL':[CE]*6,'ARR':[AR]*6,'CER':[CE]*6,'SR':[SR]*6}
#confdict = {'OM':[None]*6,'RT':[None]*6,'SCW':[None]*6,'SH2':[None]*6,'SH1':[None]*6,'THDAC':[None]*6,'CALDAC':[options.charge]*6,'PML':[None]*6,'ARL':[None]*6,'CEL':[None]*6,'CW':[None]*6,'PMR':[None]*6,'ARR':[None]*6,'CER':[None]*6,'SP':[None]*6,'SR':[None]*6,'TRIMDACL':[None]*6,'TRIMDACR':[None]*6}
vararr = []

if options.record=='True':

	timestr = datetime.datetime.now().time().isoformat().replace(":","").replace(".","")
	foldername = 'daqout_'+options.setting+'_'+options.format+'_'+timestr+dstr
	commands = []
	commands.append('mkdir daqlogs')

	commands.append('mkdir daqlogs/'+foldername)
	commands.append('cp -r data daqlogs/'+foldername)
	logfname = 'daqlogs/'+foldername+'/log_'+timestr+'.log'

	if options.monitor=='True':
		commands.append('python show.py '+logfname+' &')
	for s in commands :
		print 'executing ' + s
		subprocess.call( [s], shell=True )
	tree_vars = {}			
	tree_vars["SPILL"] = array('L',[0])
	#tree_vars["TIMESTAMP"] = array('L',[0])
	if options.setting == 'testbeam':

		tree_vars["TRIG_COUNTS_SHUTTER"] = array('L',[0])
		tree_vars["TRIG_COUNTS_TOTAL_SHUTTER"] = array('L',[0])
		tree_vars["TRIG_COUNTS_TOTAL"] = array('L',[0])
		tree_vars["TRIG_OFFSET_BEAM"] = array('L',[0]*2048)
		tree_vars["TRIG_OFFSET_MPA"] = array('L',[0]*2048)
	for i in range(0,6):
			tree_vars["AR_MPA_R"+str(i)] = array('L',[0]*48)
			tree_vars["AR_MPA_L"+str(i)] = array('L',[0]*48)
			if options.readout=='both':
				tree_vars["SR_BX_MPA_R"+str(i)] = array('L',[0]*96)
				tree_vars["SR_MPA_R"+str(i)] = array('L',[0]*96)

				tree_vars["SR_BX_MPA_L"+str(i)] = array('L',[0]*96)
				tree_vars["SR_MPA_L"+str(i)] = array('L',[0]*96)
	F = TFile('daqlogs/'+foldername+'/output.root','recreate')
	tree=TTree("Tree","Tree")


	for key in tree_vars.keys():
		if "SR" in key:
			tree.Branch(key,tree_vars[key],key+"[96]/l")
		if "AR" in key:
			tree.Branch(key,tree_vars[key],key+"[48]/l")
		if "TRIG_OFFSET" in key:
			tree.Branch(key,tree_vars[key],key+"[2048]/l")
		if "TRIG_COUNTS" in key:
			tree.Branch(key,tree_vars[key],key+"[1]/l")
	Outf1 = open(logfname, 'w')

	sys.stdout = Outf1
	print "Firmware Version " + str(firmver)
	print "DAQ Version " + str(daqver)
	print 
	print "Options summary"
	print "=================="
	for opt,value in options.__dict__.items():
		print str(opt) +': '+ str(value)
	print "=================="
	print 
	print "---------------------------------------------------------------------------"
	print "----------------------------Starting Datataking----------------------------"
	print "---------------------------------------------------------------------------"
	print 
else:	
	Outf1 = saveout

Kill=False

mapsa.daq().Strobe_settings(snum,sdel,slen,sdist,CE)
start1 = time.time()
if options.setting == 'testbeam' or options.setting == 'default':




		sys.stdout = saveout
		print "Starting DAQ loop.  Press Enter to quit"
		#raw_input("...")
		sys.stdout = Outf1




		configR = mapsa.config(Config=1,string="calibratedRight",njump=0)
		configL = mapsa.config(Config=1,string="calibratedLeft",njump=0)

		configR.modifyfull(confdict)  
		configL.modifyfull(confdict)  

		configR.upload(show = 1, UL = "Right")
		configL.upload(show = 1, UL = "Left")
		configR.write(UL = "Right",n=n,m=m,c=c,u=u)
	
		if options.setting == 'testbeam':
			polltime = 5000
			a._hw.getNode("Shutter").getNode("time").write(options.shutterdur)
			a._hw.dispatch()
			mapsa.daq().Testbeam_init(clock=options.testclock ,calib=0x0,phase=options.phase)
			mapsa.daq().header_init()
		if options.setting == 'default':
			polltime = 200
			mapsa.daq().Sequencer_init(0x1,sdur,mem=1)
			mapsa.daq().header_init()






		time.sleep(0.1)
		for cbuff in range(1,5):
			pixR,memR = mapsa.daq().read_data(buffer_num=cbuff,UL="Right",nmpa =6,Fast=True)
			pixL,memL = mapsa.daq().read_data(buffer_num=cbuff,UL="Left",nmpa =6,Fast=True)
			if options.setting == 'testbeam':
				ctotal_triggers,ctrigger_counter,ctrigger_total_counter,cOffset_BEAM,cOffset_MPA = mapsa.daq().read_trig(cbuff)
		time.sleep(0.1)


		ibuffer=1
		
		iread=0



	        Endrun = False

		zeroshutters = 0
		numloops=0

	  	poll =  0


		start = time.time()
		while Endrun == False:
		    Endspill = False
		    Startspill=True
		    cntsperspill = 0
		    spillnumber+=1
		    sys.stdout = saveout
		    print "Starting spill " + str(spillnumber)

		    sys.stdout = Outf1
		    print 
		    print
		    print "---------------------------------------------------------------------------"
		    print "-----------------------------Starting spill " + str(spillnumber)+"------------------------------"
		    print "---------------------------------------------------------------------------"
		    print
		    sys.stdout = saveout
		    while Endspill == False:




			buffers_num = a._hw.getNode("Control").getNode('Sequencer').getNode('buffers_num').read()
			spill = a._hw.getNode("Control").getNode('Sequencer').getNode('spill').read()
			buffers_index = a._hw.getNode("Control").getNode('Sequencer').getNode("buffers_index").read()
			a._hw.dispatch()
			sys.stdout = saveout
			#print buffers_num
			if options.loops!=-1:
				if numloops>=options.loops:
					Kill=True
     			if sys.stdin in select.select([sys.stdin], [], [], 0)[0] or Kill:
				 
				for ibuffer in range(1,5):
					pix,mem = mapsa.daq().read_data(ibuffer,wait=False)
				a._hw.getNode("Control").getNode('testbeam_mode').write(0x0)
        			line = raw_input()
				print "Ending loop"
				Endrun = True
				Endspill = True
        			break

	  		poll += 1


			if poll % polltime == 0:
		    		sys.stdout = saveout
				cur = time.time()
				if Startspill==True:
					print "Waiting for spill for " +str(cur-start)+ " seconds"
				#if Startspill==False:
				if Startspill==False:
					if cur-start>3.:
						print "Spill ended"
						Endspill == True
						if options.setting == 'testbeam':
							Endrun = True
						break
					else:
						print "Idle for " +str(cur-start)+ " seconds"
			#if True:
			end1 = time.time()

			#print end1-start1
			if buffers_num<4:

				if poll!=1 or buffers_num!=0:
					time.sleep(0.013)

				shutters+=1
				iread+=1
				sys.stdout = saveout
				#print 	"Buffer index pre trig " + str(buffers_index)

				#time.sleep(0.001)
				if options.setting == 'testbeam':
					total_triggers,trigger_counter,trigger_total_counter,Offset_BEAM,Offset_MPA = mapsa.daq().read_trig(ibuffer)

				
				pixR,memR = mapsa.daq().read_data(buffer_num=ibuffer,UL="Right",nmpa =6,Fast=True)
				pixL,memL = mapsa.daq().read_data(buffer_num=ibuffer,UL="Left",nmpa =6,Fast=True)

				#print buffers_num


				#print end1-start1
				sys.stdout = Outf1

				parrayR = []
				marrayR = []

				parrayL = []
				marrayL = []

				cntspershutter = 0

				for i in range(0,6):
					sys.stdout = saveout

					pixR[i].pop(0)
					pixR[i].pop(0)

					parrayR.append(pixR[i])
					marrayR.append(memR[i])
				


					pixL[i].pop(0)
					pixL[i].pop(0)

					parrayL.append(pixL[i])
					marrayL.append(memL[i])


					sys.stdout = Outf1

					cntspershutter+=sum(pixR[i])


				if cntspershutter != 0 or options.setting == 'testbeam':
					print "Available buffers: ",buffers_num
					print "Reading buffer: " + str(ibuffer)
					sys.stdout = saveout
					print "Reading buffer: " + str(ibuffer)
					sys.stdout = Outf1
				ibuffer+=1
				if ibuffer >4:
					ibuffer=1 


				if cntsperspill>60.:
					Startspill=False

				if cntspershutter == 0 and options.skip=='True' and options.setting != 'testbeam':
					continue



				if options.setting == 'testbeam':

					offdat = []
					#To fix
					offsetbeam = [0]*2048
					offsetmpa = [0]*2048
					sys.stdout = saveout

					for i in range(0,trigger_counter):
							
						offsetbeam[i] = Offset_BEAM[i]
						offdat.append(1000*(Offset_BEAM[i]-Offset_BEAM[0])/26.5)
						offsetmpa[i] = Offset_MPA[i]



					sys.stdout = Outf1
					print "Offset beam: " + str(offsetbeam)
					print "Offset mpa: " + str(offsetmpa)
					a._hw.dispatch()
					offset = []



				cntsperspill+=cntspershutter
				sys.stdout = saveout
				print "Number of Shutters: " + str(shutters)
				print "Counts Total: " + str(cntsperspill)
				print "Counts per Shutter: " + str(cntspershutter)

				if options.setting == 'testbeam':
					print "Triggers per Shutter: " + str(trigger_counter)	
					print "Triggers at Shutter Start: " + str(trigger_total_counter)
					print "Triggers Total: " + str(total_triggers)
					print "Triggers Total: " + str(hex(total_triggers))
				print 
				sys.stdout = Outf1
				print "Number of Shutters: " + str(shutters)
				print "Counts Total: " + str(cntsperspill)
				print "Counts per Shutter: " + str(cntspershutter)

				if options.setting == 'testbeam':
					print "Triggers per Shutter: " + str(trigger_counter)	
					print "Triggers at Shutter Start: " + str(trigger_total_counter)
					print "Triggers Total: " + str(total_triggers)
				print 





				if AR:

					print "Counter output"
					temp_vars = {}

					i=0
					for p in parrayR:
						sys.stdout = Outf1
						print p
						print ""
						sys.stdout = saveout

						temp_vars["AR_MPA_R"+str(i)]=p

						i+=1

					i=0
					for p in parrayL:
						sys.stdout = Outf1
						print p
						print ""
						sys.stdout = saveout

						temp_vars["AR_MPA_L"+str(i)]=p

						i+=1

					sys.stdout = Outf1

				if SR:
					print "Memory output"

					i=0
					for memo in marrayR:
						temp_vars["SR_UN_MPA_R"+str(i)]=memo				
						i+=1

				
					i=0
					for memo in marrayL:
						temp_vars["SR_UN_MPA_L"+str(i)]=memo	
						i+=1



				if options.setting == 'testbeam':
	
					temp_vars["TRIG_COUNTS_SHUTTER"] = [trigger_counter]
					temp_vars["TRIG_COUNTS_TOTAL_SHUTTER"] = [trigger_total_counter]
					temp_vars["TRIG_COUNTS_TOTAL"] = [total_triggers]
					temp_vars["TRIG_OFFSET_BEAM"] = offsetbeam
					temp_vars["TRIG_OFFSET_MPA"] = offsetmpa
				temp_vars["SPILL"] = [spillnumber]
				vararr.append(temp_vars)

				#for tv in tree_vars.keys():
				#	sys.stdout = saveout

				#	for i in range(0,len(temp_vars[tv])):
				#		tree_vars[tv][i] = temp_vars[tv][i]
	
				#	sys.stdout = Outf1

				#tree.Fill()
	
				print "---------------------------------------------------------------------------"
				numloops+=1
	  			poll = 0				
				#start1 = time.time()
				#start = time.time()
	    	print "Writing events to tree..."

	    	nev = 0
	    	for ev in vararr:
			nev+=1
			if nev%20==0:

				print nev
			for impa in range(0,len(mpa)):
				
				#print ev["SR_UN_MPA_"+str(impa)]
				#print len(ev["SR_UN_MPA_"+str(impa)])

				memR[impa] = mpa[impa].daq().formatmem(ev["SR_UN_MPA_R"+str(impa)])
				memoR = mpa[impa].daq().read_memory(memR[impa],memmode)



				for p in range(0,96):
					if p>len(memoR[0]):
						memoR[0].append(int(0))
						memoR[1].append('0')

				BXmemoR = np.array(memoR[0])	
				DATAmemoR = np.array(memoR[1])

				DATAmemoRint = []	
				for DATAmemR in DATAmemoR:
					DATAmemoRint.append(long(DATAmemR,2)) 
	
				ev["SR_BX_MPA_R"+str(impa)] = BXmemoR
				ev["SR_MPA_R"+str(impa)] = DATAmemoRint


				#print ev["SR_UN_MPA_"+str(impa)]
				#print len(ev["SR_UN_MPA_"+str(impa)])
				memL[impa] = mpa[impa].daq().formatmem(ev["SR_UN_MPA_L"+str(impa)])
				memoL = mpa[impa].daq().read_memory(memL[impa],memmode)



				for p in range(0,96):
					if p>len(memoL[0]):
						memoL[0].append(int(0))
						memoL[1].append('0')

				BXmemoL = np.array(memoL[0])	
				DATAmemoL = np.array(memoL[1])

				DATAmemoLint = []	
				for DATAmemL in DATAmemoL:
					DATAmemoLint.append(long(DATAmemL,2)) 
	
				ev["SR_BX_MPA_L"+str(impa)] = BXmemoL
				ev["SR_MPA_L"+str(impa)] = DATAmemoLint


			for tv in tree_vars.keys():
				if 'SR_UN_MPA' in tv:
					continue 
				for i in range(0,len(ev[tv])):
					tree_vars[tv][i] = ev[tv][i]
			tree.Fill()
		print "Writing beam off"
		a._hw.getNode("Control").getNode("beam_on").write(0x0)
		a._hw.dispatch()
		print "Final trigger count"
		final_triggers = a._hw.getNode("Control").getNode('total_triggers').read()
		a._hw.dispatch()
		print final_triggers
	        F.Write()
	        F.Close()

print ""
print "Done"
