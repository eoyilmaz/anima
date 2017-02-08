"""import threading
import time

class Mythread(threading.Thread):
	def run(self):
		print("About to ss")
		time.sleep(5)
		print("finish")

m = Mythread()
m.start()

print(time.perf_counter())"""

import threading
import PeyeonScript,time
from multiprocessing import Pool , TimeoutError

def serverConnect(ip):
	basla2= time.clock()
	fusion = PeyeonScript.scriptapp("Fusion",ip)
	with basla2>1:
		print "ssss"
	if fusion != None:
		comp = fusion.GetCurrentComp()
		try:
			compName= comp.GetAttrs('COMPS_Name')
			username = fusion.GetEnv("USERNAME")
			print "Username: %s Composition Name: %s Ip Adress: %s" %(username,compName,ip)
		except AttributeError:
			print "AttributeError"
	basla3 = time.clock()
	print("Toplam Sure = {:10.8f}".format(basla3-basla2), ip)


if __name__ == "__main__":
	gorev = list()
	pool = Pool()

	for i in range(35):
		ip = "192.168.0.%s" %i
		mp = pool.apply_async(serverConnect, args=(ip,))

	pool.close()
	pool.join()
	print "Bitti"