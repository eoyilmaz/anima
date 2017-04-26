# -*- coding: utf-8 -*-
import threading
import time
import PeyeonScript
from multiprocessing import Pool, TimeoutError


def server_connect(ip):
    """connects to server

    :param str ip: The IP of the
    :return:
    """
    basla2 = time.clock()
    fusion = PeyeonScript.scriptapp("Fusion", ip)
    if fusion is not None:
        comp = fusion.GetCurrentComp()
        try:
            comp_name = comp.GetAttrs('COMPS_Name')
            username = fusion.GetEnv("USERNAME")
            fusion_version = float(fusion.GetAttrs("FUSIONS_Version"))
            print {"Username": username, "Composition Name": comp_name,
                   "Ip Adress": ip, "Fusion Version": fusion_version}
        except AttributeError:
            print "AttributeError"
        # basla3 = time.clock()
        # print("Toplam Sure = {:10.8f}".format(basla3-basla2), ip)


if __name__ == "__main__":
    gorev = list()
    pool = Pool()
    
    for i in range(200):
        ip = "192.168.0.%s" % i
        mp = pool.apply_async(server_connect, args=(ip,))
    print "Sorry for waiting..."
    pool.close()
    pool.join()
    print "Bitti"
