global com, POST, maxsr, ld0, ld1, ld2, ld3, ld4, ld5, ld6, ld7, ld8, ld9, ld10, ld11, fVoff, R, G, B, iR, iG, iB, nwR, nwG, nwB, sR, sG, sB, mR, mG, mB, port, psyon
psyon=0
com='COM13'
POST=1 #1 do POST, 0 skip it
#LED flag values - never use 0 or 255 - must match arduino
#figure out where to steal the flag values from for now I just
#took an even distribution, but is most likely not the best
#because of curve of human light intensity sensativity
ld0=21   #R0  D3
ld1=41   #G0  D5
ld2=61   #B0  D6
ld3=81   #R1  D9  G
ld4=101  #G1  D10 B
ld5=121  #B1  D11 R
ld6=141  #R2
ld7=161  #G2
ld8=181  #B2
ld9=201  #R3
ld10=221 #G3
ld11=241 #B3
fVoff=1  #set 1 to increase brightness of incoming flag
         #values, -1 to decrease
datar=125 #incoming number of values per second per channel

import OSC, serial, time, threading, datetime
R=[0]*datar
G=[0]*datar
B=[0]*datar
iR=-1
iG=-1
iB=-1
wR=0
wG=0
wB=0
sR=1
sG=1
sB=1
mR=0
mG=0
mB=0
if psyon:
    try:
        import psyco
        psyco.full()
    except ImportError:
        psyon=0
        pass
port = serial.Serial('\\\\.\\'+com, 115200, timeout=0)

def initBP(): #Test if BP is already online, may get out of some modes TBR
    port.write('##') #test string
    time.sleep(.008)
    if port.read(2)=='##': #echoing test string indicates BP in term mode
        port.write('\n') #if nothing is entered this will reset
        time.sleep(.008)
        port.write('m\n') #mode
        time.sleep(.008)
        port.write('3\n') #UART
        time.sleep(.008)
        port.write('9\n') #115200
        time.sleep(.008)
        port.write('1\n') #8/N
        time.sleep(.008)
        port.write('1\n') #/1
        time.sleep(.008)
        port.write('1\n') #/1
        time.sleep(.008)
        port.write('2\n') #3.3V
        time.sleep(.008)
        port.write('W\n') #PSU on
        time.sleep(.008)
        port.write('(3)\n') #transparent bridge with flow control
        time.sleep(.008)
        port.write('y')   # confirm entry to bridge

def main():
#    initBP() #TBR
    time.sleep(1) #pause for 2560 bootloader
    osc=OSC.ThreadingOSCServer(('127.0.0.1', 10233))
    osct=threading.Thread(target=osc.serve_forever)
    try:
        osc.addMsgHandler('/R', setR)
        osc.addMsgHandler('/G', setG)
        osc.addMsgHandler('/B', setB)
        osc.addMsgHandler('/mR', setmR)
        osc.addMsgHandler('/mG', setmG)
        osc.addMsgHandler('/mB', setmB)
        osc.addMsgHandler('/sR', setsR)
        osc.addMsgHandler('/sG', setsG)
        osc.addMsgHandler('/sB', setsB)
        osct.start()
        if POST==1:
            testsR()
            testsG()
            testsB()
        while 1:
            avg()
            if mR==1:
                testR()
            elif mR==2:
                testsR()
            else:
                colorR()
            if mG==1:
                testG()
            elif mG==2:
                testsG()
            else:
                colorG()
            if mB==1:
                testB()
            elif mB==2:
                testsB()
            else:
                colorB()
            if psyon:
                time.sleep(0) #needed for psyco
    except KeyboardInterrupt: #this does not work if psyco is on
        osc.close()
        osct.join()
        send(ld5,0)
        send(ld3,0)
        send(ld4,0)
        print time.strftime('[%H:%M:%S]')+' Program exited.'
        
def colorR():
    global wR
    if nwR!=wR:
        wR=nwR
        send(ld5,wR)

def colorG():
    global wG
    if nwG!=wG:
        wG=nwG
        send(ld3,wG)

def colorB():
    global wB
    if nwB!=wB:
        wB=nwB
        send(ld4,wB)

def testR():
    global tiR
    if tiR>255:
        send(ld5,510-tiR)
    else:
        send(ld5,tiR)
    tiR=(tiR+1)%510

def testG():
    global tiG
    if tiG>255:
        send(ld3,510-tiG)
    else:
        send(ld3,tiG)
    tiG=(tiG+1)%510

def testB():
    global tiB
    if tiB>255:
        send(ld4,510-tiB)
    else:
        send(ld4,tiB)
    tiB=(tiB+1)%510
    
def testsR():
    for i in xrange(256):
        send(ld11,i)
    for i in xrange(256):
        send(ld11,255-i)

def testsG():
    for i in xrange(256):
        send(ld3,i)
    for i in xrange(256):
        send(ld3,255-i)

def testsB():
    for i in xrange(256):
        send(ld4,i)
    for i in xrange(256):
        send(ld4,255-i)

def avg():
    global nwR, nwG, nwB
    aR=R
    aG=G
    aB=B
    aiR=iR
    aiG=iG
    aiB=iB
    asR=sR
    asG=sG
    asB=sB
    nwR=0
    nwG=0
    nwB=0
    for i in xrange(asR):
        nwR=nwR+aR[(aiR-i+datar)%datar]
    nwR=int(round(nwR/asR))
    for i in xrange(asG):
        nwG=nwG+aG[(aiG-i+datar)%datar]
    nwG=int(round(nwG/asG))
    for i in xrange(asB):
        nwB=nwB+aB[(aiB-i+datar)%datar]
    nwB=int(round(nwB/asB))

def setR(NULL1,NULL2,nR,NULL3):
    global R, iR
    if nR[0]>255:
        nR[0]=255
    iR=(iR+1)%datar
    R[iR]=nR[0]

def setG(NULL1,NULL2,nG,NULL3):
    global G, iG
    if nG[0]>255:
        nG[0]=255
    iG=(iG+1)%datar
    G[iG]=nG[0]

def setB(NULL1,NULL2,nB,NULL3):
    global B, iB
    if nB[0]>255:
        nB[0]=255
    iB=(iB+1)%datar
    B[iB]=nB[0]

def setsR(NULL1,NULL2,nsR,NULL3):
    global sR
    sR=nsR[0]
    print time.strftime('[%H:%M:%S]')+' Red averaging time: '+str(1000*sR/datar)+'ms.'

def setsG(NULL1,NULL2,nsG,NULL3):
    global sG
    sG=nsG[0]
    print time.strftime('[%H:%M:%S]')+' Green averaging time: '+str(1000*sG/datar)+'ms.'

def setsB(NULL1,NULL2,nsB,NULL3):
    global sB
    sB=nsB[0]
    print time.strftime('[%H:%M:%S]')+' Blue averaging time: '+str(1000*sB/datar)+'ms.'

def setmR(NULL1,NULL2,nmR,NULL3):
    global mR
    mR=nmR[0]
    if mR==1:
        global tiR
        tiR=0
        print time.strftime('[%H:%M:%S]')+' Red in test mode.'
    elif mR==2:
        print time.strftime('[%H:%M:%S]')+' Red in sequential test mode.'
    else:
        print time.strftime('[%H:%M:%S]')+' Red in color mode.'

def setmG(NULL1,NULL2,nmG,NULL3):
    global mG
    mG=nmG[0]
    if mG==1:
        global tiG
        tiG=0
        print time.strftime('[%H:%M:%S]')+' Green in test mode.'
    elif mG==2:
        print time.strftime('[%H:%M:%S]')+' Green in sequential test mode.'
    else:
        print time.strftime('[%H:%M:%S]')+' Green in color mode.'

def setmB(NULL1,NULL2,nmB,NULL3):
    global mB
    mB=nmB[0]
    if mB==1:
        global tiB
        tiB=0
        print time.strftime('[%H:%M:%S]')+' Blue in test mode.'
    elif mB==2:
        print time.strftime('[%H:%M:%S]')+' Blue in sequential test mode.'
    else:
        print time.strftime('[%H:%M:%S]')+' Blue in color mode.'

def send(fV,dV):
    while dV==ld0 or dV==ld1 or dV==ld2 or dV==ld3 or dV==ld4 or dV==ld5 or dV==ld6 or dV==ld7 or dV==ld8 or dV==ld9 or dV==ld10 or dV==ld11:
        dV=dV+fVoff
    port.write(bytearray([chr(fV),chr(dV)]))

main()
