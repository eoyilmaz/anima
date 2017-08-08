from anima.env.fusion.model.projectPath import *
from anima.env.fusion.model.fusion import *
from anima.env.fusion.view.view import form



class controller(object):
	def __init__(self):
		#path
		self.path = project()
		self.path.projectList()

		#view
		self.projectForm = form()
		self.shotForm = form()
		self.sequenceForm= form()
		self.fusion = fusion()

	def projectSelect(self):
		form1 = self.projectForm.AskUser("Select Project", self.path.projectdict, 1)
		if form1 == None:
			print "Canceled by User"
			return None
		else:
			self.project = self.path.projectChoose(int(form1["project"]))
			self.sequence()

	def sequence(self):
		self.path.sequencesList()
		self.path.sequenceDict()
		form2 = self.sequenceForm.AskUser(self.project, self.path.sequencedict, 2)
		if form2 == None:
			print "Canceled by User"
			return None
		else:
			self.path.sequenceSelect(form2["sequence"])
			self.shotLoop()
			#path.sequence(0)

	def shotLoop(self):
		self.plateloop = self.path.plateLoop()
		#Loader Loop sokuluyor
		for i in range(0,len(self.plateloop), 1):
			shot = self.path.selectShot(i)
			f = self.shotForm.AskUser(shot, self.plateloop[i], 0)
			if f == None:
				print "Canceled by User"
				break
			if self.path.fileCheck(f["Path"])== True:
				self.fusion.loader(self.path.shot, f["Path"], i, 0)
				print str(i+1)+" / "+str(len(self.plateloop)) + " Shots Completed " + f["Path"]
			else:
				print "Wrong yol: " + f["Path"]
				break

	def cStartEnd(self):
		self.fusion.compStartEnd()
