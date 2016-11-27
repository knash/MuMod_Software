#Functions related to data aquisition at the MAPSA level - starting calibration and data taking 
#as well as loops of MPA_daq readout objects for ease of use 



from MPA import *
from MPA_daq import *
from MAPSA_functions import *


class MAPSA_config:
	
	def __init__(self, hw,Config=1,string='default',njump=0):
		self.njump 		=	njump
		self._hw     		= 	hw
		self._Config		=	Config
		self._String		=	string
		self._Shutter   	= 	self._hw.getNode("Shutter")
		self._Control		=	self._hw.getNode("Control")
		self._Configuration 	=  	self._hw.getNode("Configuration_Left")
		self._Readout 		=  	self._hw.getNode("Readout_Left")
		self._Sequencer		=	self._Control.getNode("Sequencer") 

		self._puls_num   = self._Shutter.getNode("Strobe").getNode("number")
		self._puls_len   = self._Shutter.getNode("Strobe").getNode("length")
		self._puls_dist  = self._Shutter.getNode("Strobe").getNode("distance")
		self._puls_del   = self._Shutter.getNode("Strobe").getNode("delay")
		self._shuttertime	= self._Shutter.getNode("time")

		self._sequencerbusy  = self._Sequencer.getNode("busy")
		self._calib  = self._Control.getNode("calibration")
		#self._read  = self._Control.getNode("readout")
		self._buffers  = self._Sequencer.getNode("buffers_index")
		self._data_continuous  = self._Sequencer.getNode("datataking_continuous")

		self._memory  = self._Readout.getNode("Memory")
		self._counter  = self._Readout.getNode("Counter")
		self._readmode  = self._Control.getNode("readout")
		#self._readbuff  = self._Readout.getNode("buffer_num")

    		self._clken = self._Control.getNode("MPA_clock_enable") 		  
    		self._testbeam = self._Control.getNode("testbeam_mode") 		  


		self._Utility =  self._hw.getNode("Utility")
		self._Conf_busy    = self._Configuration.getNode("busy")

		self._Memory_DataConf   = self._Configuration.getNode("Memory_DataConf")

		self._confs = []
		self._confsxmlroot= []
		self._confsxmltree= []
		mpa = []  
		for i in range(1,7):
			mpa.append(MPA( self._hw,i))
			self._confs.append(mpa[i-1].config(xmlfile="data/Conf_"+self._String+"_MPA"+str(i)+"_config"+str(self._Config)+".xml"))
			self._confsxmltree.append(self._confs[i-1].xmltree)
			self._confsxmlroot.append(self._confs[i-1].xmlroot)

	def _spi_wait(self):
		busy = self._Conf_busy.read()
		self._hw.dispatch()
		while busy:
			time.sleep(0.001)
			busy = self._Conf_busy.read()
			self._hw.dispatch()
			#print busy

	def upload(self,show = 0, UL = "Left"):
		curs = []
		i=0
		for conf in self._confs:
			i+=1
			curs.append(conf.upload(show=show,Config=self._Config,UL = UL))
		return curs



	def modifyperiphery(self,what, value):

		impa=0
		for conf in self._confs:

########FOR JUMPERS##########
			
			if impa==6-self.njump:
				break
			conf.modifyperiphery(what, value[impa+self.njump])
##################


#			conf.modifyperiphery(what, value[impa])
			impa+=1

	def modifypixel(self,which, what, value):

		impa=0
		for conf in self._confs:

########FOR JUMPERS##########
			if impa==6-self.njump:
				break
			conf.modifypixel(which, what, value[impa+self.njump])
##################
#			conf.modifypixel(which, what, value[impa])



			impa+=1





	def modifyfull(self, whichs,pixels=[1,25]):
	

		for key in whichs.keys():
			if whichs[key] == [None]*6:
				continue
			if any(['OM' in key,'RT' in key,'SCW' in key,'SH2' in key,'SH1' in key,'THDAC' in key,'CALDAC' in key]):
				self.modifyperiphery(key,whichs[key])
			elif any(['PML' in key,'ARL' in key,'CEL' in key,'CW' in key,'PMR' in key,'ARR' in key,'CER' in key,'SP' in key,'SR' in key,'TRIMDACL' in key,'TRIMDACR' in key]):
	
				for x in range(pixels[0],pixels[1]):
					#if x==6 and key=='PML':
					#	self.modifypixel(x,key,[0,1,0,0,0,0])
					#else:
						self.modifypixel(x,key,whichs[key])









	def write(self,UL,n,m,c,u):

		self._hw.getNode("Configuration_Left").getNode("num_MPA").write(n)
		self._hw.getNode("Configuration_Right").getNode("num_MPA").write(n)

		self._hw.dispatch()

		self._Control.getNode("confs").write(c)
		self._hw.dispatch()

		self._Control.getNode("conf_upload").write(u)
		self._hw.dispatch()


		self._spi_wait()
