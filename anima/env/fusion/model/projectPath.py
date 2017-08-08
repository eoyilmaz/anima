# -*- coding: utf-8 -*-
import os
import re

class project():
	def __init__(self):
		self.window = r'T:'+os.sep+'PROJECTS'
		self.seq = 'Sequences'
		self.shots = "Shots"
		self.plate = "Plate"
		self.comp = "Comp"

	def checkPath(self,path):
		if path == False:
			return False
		if os.path.isdir(path):
			return True
		else:
			return False

	def fileCheck(self,file):
		if file == False:
			return False
		if os.path.isfile(file):
			return True
		else:
			return False

	def fileFinder(self, list, file): #val liste
		for i in range(0,len(list), 1):
			nesne = re.match(file, list[i])
			if nesne:
				return True

	def trash(self,list):
		if self.fileFinder(list,".DS_Store") == True:
			list.remove(".DS_Store")

		if self.fileFinder(list,".gallery") == True:
			list.remove(".gallery")

		if self.fileFinder(list,".Thumbs.db") == True:
			list.remove("Thumbs.db")

		if self.fileFinder(list,"SHeditedit") == True:
			list.remove("SHeditedit")

		if self.fileFinder(list,"SHedit") == True:
			list.remove("SHedit")


# PROJECT-------------------------------

	def project(self, choose):
		self.projectList()
		self.projectChoose(choose)

	def projectLength(self):
		self.projectlength = len(self.projectlist)

	def projectDict(self):
		self.projectdict = {i: self.projectlist[i] for i in range(0, self.projectlength, 1)}

	def projectList(self):
		if self.checkPath(self.window)== True :
			self.projectlist = os.listdir(self.window)
			self.trash(self.projectlist)
			self.projectLength()
			self.projectDict()
		else:
			self.projectList = -1

	def projectChoose(self, choose):   #projeleri listeliyor.
		if self.projectlist != -1:
			if 0 <= choose < self.projectlength:
				self.projectChoose = self.projectlist[choose]
				return self.projectChoose
		else:
			self.projectlist = -1


# PROJECT-------------------------------
# Sequences-------------------------------

	def sequence(self, seq):
		if self.projectlist != False:
			self.sequenceChoose(seq)

	def sequencePath(self):
		self.sequencepath = os.path.join(self.window,
										self.projectChoose,
										self.seq)

	def sequenceDict(self):
		self.sequencedict = {i: self.sequenceslist[i] for i in range(0, self.sequencelength, 1)}

	def sequenceLength(self):
		self.sequencelength = len(self.sequenceslist)

	def sequenceSelect(self, seq):
		self.sequencesList()
		if 0 <= seq < self.sequenceLength:
			self.sequence = self.sequenceslist[int(seq)]
		else:
			self.sequence = False

	def sequencesList(self):  #sekans icindeki klasorleri listeliyor
		self.sequencePath()
		if self.checkPath(self.sequencepath) == True:
			self.sequenceslist = os.listdir(self.sequencepath)
			self.trash(self.sequenceslist)
			self.sequenceLength()
		else:
			self.sequencepath = False


# Sequences-------------------------------
# SHOT-------------------------------
	def shotPath(self):
		if self.sequence != False:
			self.shotpath = os.path.join(self.sequencepath, self.sequence, self.shots)
		else:
			self.shotPath = False

	def shotLength(self):
		self.shotlength = len(self.shotlist)

	def selectShot(self, s):
		self.shot =  self.shotlist[s]
		return self.shot

	def shotList(self):
		self.shotPath()
		if self.checkPath(self.shotpath) == True:
			self.shotlist = os.listdir(self.shotpath)
			self.trash(self.shotlist)
			self.shotLength()
		else:
			self.shotpath = False

# SHOT-------------------------------
# PLATE-------------------------------

	def Plate(self):
		if self.shotpath != False :
			self.plateList()

	def platePath(self,shot):
		return os.path.join(self.shotpath, self.selectShot(shot), self.plate)

	def plateList(self):
		self.platePath()
		if self.checkPath(self.platePath):
			self.plateList = os.listdir(self.plateShot)
			self.trash(self.plateList)

	def plateLoop(self):
		self.platePathlist = []
		self.shotList()
		for i in range(0, self.shotlength, 1):
			self.platePathlist.append(self.platePath(i))
		if self.shotlength == 0:
			print "Shot have nothing"
		else:
			return self.platePathlist

	def show(self,s):
		print "Project: " + self.projectChoose
		print "ProjectList: " + str(self.projectlist)
		print "Sequence: " + self.sequence
		print "SequenceList: " + str(self.sequenceslist)
		print "SequencePath: " + self.sequencepath
		print "Shot: " + self.selectShot(s)
		print "ShotList: " + str(self.shotList)
		print "ShotList: " + self.shotpath


# PLATE-------------------------------




