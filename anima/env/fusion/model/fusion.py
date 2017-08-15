try:
    # for Fusion 6 and 7
    import PeyeonScript as bmf
except ImportError:
    # for Fusion 8+
    import BlackmagicFusion as bmf


class fusion(object):
	def __init__(self):
		self.sumshot = 0.0
		self.offset = 0

		self.fusion = bmf.scriptapp("Fusion")
		self.comp = self.fusion.GetCurrentComp()

	def loader(self, name, clip, x, y):
		self.comp.Lock()
		self.clip = self.comp.Loader({"Clip": clip})
		self.setPos(self.clip, x, y)
		if self.offset == 0:
			bg = self.comp.Background()
			self.setPos(bg,-1, +2) #tek bi tane lazim oldugu icin burada
			self.Merge(bg,self.clip,x,y+2)
		else:
			self.Merge(self.merge,self.clip,x,y+2)

		self.clip.SetAttrs({"TOOLS_Name": name})
		self.end = self.clip.ClipTimeEnd[1]
		if self.offset > 0:
			self.offSet()
		self.offset += 1
		self.sumShot(self.end)
		self.comp.Unlock()

	def Merge(self,bg,fg,x,y):
		self.merge = self.comp.Merge()
		self.setPos(self.merge,x,y)
		self.merge.Foreground = fg.Output
		self.merge.Background = bg.Output

	def setPos(self, obj, x, y):
		flow = self.comp.CurrentFrame.FlowView
		flow.SetPos(obj, x, y)

	def sumShot(self, s):
		self.sumshot += s+1

	def offSet(self):
		self.clip.GlobalOut[1] = self.sumshot
		self.clip.GlobalIn[1] = self.sumshot
		self.clip.HoldLastFrame[1] = 0
		self.clip.HoldFirstFrame[1] = 0
		self.clip.ClipTimeStart[1] = 0
		self.clip.ClipTimeEnd[1] = self.end

	def compStartEnd(self):
		self.comp.SetAttrs({"COMPN_GlobalStart": 0})
		self.comp.SetAttrs({"COMPN_GlobalEnd": self.sumshot-1})
		self.comp.SetAttrs({"COMPN_RenderStartTime": 0})
		self.comp.SetAttrs({"COMPN_RenderEndTime": self.sumshot-1})
		self.comp.SetAttrs({"COMPN_RenderStart":0})
		self.comp.SetAttrs({"COMPN_RenderEnd": self.sumshot-1})
