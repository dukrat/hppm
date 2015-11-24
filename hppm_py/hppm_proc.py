

global psyon, com, dpR, dpG, dpB, ourt, fps, sType, numLights, woR, woG, woB
global mR, mG, mB, wsR, wsG, wsB, pA, su, cwR, cwG, cwB, R, G, B, iR, iG, iB
global tiR, tiG, tiB, wR, wG, wB, sR, sG, sB, lR, lG, lB, lW, nwR, nwG, nwB
global port, fadeR, fadeG, fadeB, lightOn, chngBProp, pR, pG, pB, exit_v

#the pixel values used for various signals, should match arduino
pA=255 #whole strip solid color
su=254 #set numLights, fps, protocol and maxBright, reserved
ns=250 #single pixel
#start wave on color origin
cwR=251
cwG=252
cwB=253
def_ret=17 #time to send a new byte
import OSC, serial, time, threading, datetime, struct, random, ConfigParser
import signal, sys
config=ConfigParser.RawConfigParser()
if len(sys.argv)==2:
    config.read(sys.argv[1])
else:
    config.read('hppm_proc_py.ini')
psyon=config.getint("hppm_proc.py", "psyon")
com=config.get("hppm_proc.py", "com")
fadeR=config.getint("hppm_proc.py", "fadeR")
fadeG=config.getint("hppm_proc.py", "fadeG")
fadeB=config.getint("hppm_proc.py", "fadeB")
lightOn=config.getint("hppm_proc.py", "lightOn")
chngBProp=config.getint("hppm_proc.py", "chngBProp")
minrwR=config.getint("hppm_proc.py", "minrwR")
maxrwR=config.getint("hppm_proc.py", "maxrwR")
minrwG=config.getint("hppm_proc.py", "minrwG")
maxrwG=config.getint("hppm_proc.py", "maxrwG")
minrwB=config.getint("hppm_proc.py", "minrwB")
maxrwB=config.getint("hppm_proc.py", "maxrwB")
datar=config.getint("hppm_proc.py", "datar")
dpR=config.getint("hppm_proc.py", "dpR")
dpG=config.getint("hppm_proc.py", "dpG")
dpB=config.getint("hppm_proc.py", "dpB")
rpR=config.getint("hppm_proc.py", "rpR")
rpG=config.getint("hppm_proc.py", "rpG")
rpB=config.getint("hppm_proc.py", "rpB")
srp=config.getint("hppm_proc.py", "srp")
outr=config.getint("hppm_proc.py", "outr")
fps=config.getint("hppm_proc.py", "fps")
sType=config.get("hppm_proc.py", "sType")
numLights=config.getint("hppm_proc.py", "numLights")
woR=config.getint("hppm_proc.py", "woR")
woG=config.getint("hppm_proc.py", "woG")
woB=config.getint("hppm_proc.py", "woB")
mR=config.getint("hppm_proc.py", "mR")
mG=config.getint("hppm_proc.py", "mG")
mB=config.getint("hppm_proc.py", "mB")
wsR=config.getint("hppm_proc.py", "wsR")
wsG=config.getint("hppm_proc.py", "wsG")
wsB=config.getint("hppm_proc.py", "wsB")

R=[0]*datar
G=[0]*datar
B=[0]*datar
iR=-1
iG=-1
iB=-1
tiR=0
tiG=0
tiB=0
wR=0
wG=0
wB=0
sR=1
sG=1
sB=1
lR=0
lG=0
lB=0
lW=0
pR=dpR
pG=dpG
pB=dpB
if psyon:
    try:
        import psyco
        psyco.full()
    except ImportError:
        psyon=0
        pass
port = serial.Serial('\\\\.\\'+com, 115200, timeout=1.1)
exit_v=0

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
    print time.strftime('[%H:%M:%S]')+' Program started.'
    time.sleep(1.5) #pause for bootloader
    #define OSC server
    osc=OSC.ThreadingOSCServer(('127.0.0.1', 10233))
    osct=threading.Thread(target=osc.serve_forever)
    #setup and start the OSC server
    osc.addMsgHandler('/R', setR)
    osc.addMsgHandler('/G', setG)
    osc.addMsgHandler('/B', setB)
    osc.addMsgHandler('/mR', setmR)
    osc.addMsgHandler('/mG', setmG)
    osc.addMsgHandler('/mB', setmB)
    osc.addMsgHandler('/sR', setsR)
    osc.addMsgHandler('/sG', setsG)
    osc.addMsgHandler('/sB', setsB)
    osc.addMsgHandler('/wsR', setwsR)
    osc.addMsgHandler('/wsG', setwsG)
    osc.addMsgHandler('/wsB', setwsB)
    osc.addMsgHandler('/woR', setwoR)
    osc.addMsgHandler('/woG', setwoG)
    osc.addMsgHandler('/woB', setwoB)
    osct.start()
    #setup the arduino program
    global maxBright
    if sType=="LPD8806":
	sNum=0
	maxBright=127
    elif sType=="WS2801":
	sNum=2
	maxBright=255
    else:
	print time.strftime('[%H:%M:%S]')+' Incorrect sType specified.'
	osc.close()
	osct.join()
	time.sleep(.100)
	if lightOn==0:
	    sendSCH(0,0,0)
	else:
	    sendSCH(maxBright,maxBright,maxBright)
	print time.strftime('[%H:%M:%S]')+' Program exited.'
    write(su,numLights-1,fps,chngBProp+sNum,0)
    while 1:
	avg()
	if mG==1:
	    testG()
	elif mG==2:
	    testsG()
	elif mG==3:
	    rwalkG()
	else:
	    colorG()
	if mR==1:
	    testR()
	elif mR==2:
	    testsR()
	elif mR==3:
	    rwalkR()
	else:
	    colorR()
	if mB==1:
	    testB()
	elif mB==2:
	    testsB()
	elif mB==3:
	    rwalkB()
	else:
	    colorB()
	if psyon:
	    time.sleep(0) #needed for psyco
	if exit_v:
	    osc.close()
	    osct.join()
                #we send these twice, as the first isn't always proc'd
	    if lightOn==0:
		sendSCH(0,0,0)
                sendSCH(0,0,0)
	    else:
		sendSCH(maxBright,maxBright,maxBright)
                sendSCH(maxBright,maxBright,maxBright)
	    print time.strftime('[%H:%M:%S]')+' Program exited.'
            exit()

def signal_handler(signal, frame):
    print time.strftime('[%H:%M:%S]')+' Exiting...'
    global exit_v
    exit_v=1

signal.signal(signal.SIGINT, signal_handler)

def colorR():
    global wR
    wR=nwR
    sendT("R",wR)

def colorG():
    global wG
    wG=nwG
    sendT("G",wG)

def colorB():
    global wB
    wB=nwB
    sendT("B",wB)

def testR():
    global tiR
    if tiR>maxBright:
        sendT("R",(maxBright*2)-tiR)
    else:
        sendT("R",tiR)
    tiR=(tiR+1)%(maxBright*2)

def testG():
    global tiG
    if tiG>maxBright:
        sendT("G",(maxBright*2)-tiG)
    else:
        sendT("G",tiG)
    tiG=(tiG+1)%(maxBright*2)

def testB():
    global tiB
    if tiB>maxBright:
        sendT("B",(maxBright*2)-tiB)
    else:
        sendT("B",tiB)
    tiB=(tiB+1)%(maxBright*2)

def testsR():
    for i in xrange(maxBright+1):
        sendT("R",i)
    for i in xrange(maxBright):
        sendT("R",maxBright-1-i)

def testsG():
    for i in xrange(maxBright+1):
        sendT("G",i)
    for i in xrange(maxBright):
        sendT("G",maxBright-1-i)

def testsB():
    for i in xrange(maxBright+1):
        sendT("B",i)
    for i in xrange(maxBright):
        sendT("B",maxBright-1-i)

def rwalkR():
    sendT("R",random.randint(minrwR, maxrwR))
    
def rwalkG():
    sendT("G",random.randint(minrwG, maxrwG))

def rwalkB():
    sendT("B",random.randint(minrwB, maxrwB))

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
    if nR[0]>maxBright:
        nR[0]=maxBright
    iR=(iR+1)%datar
    R[iR]=nR[0]

def setG(NULL1,NULL2,nG,NULL3):
    global G, iG
    if nG[0]>maxBright:
        nG[0]=maxBright
    iG=(iG+1)%datar
    G[iG]=nG[0]

def setB(NULL1,NULL2,nB,NULL3):
    global B, iB
    if nB[0]>maxBright:
        nB[0]=maxBright
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

def setwsR(NULL1,NULL2,nwsR,NULL3):
    global wsR
    wsR=nwsR[0]
    print time.strftime('[%H:%M:%S]')+' Red wave delay: '+str(1/wsR)+'ms between jumps.'

def setwsG(NULL1,NULL2,nwsG,NULL3):
    global wsG
    wsG=nwsG[0]
    print time.strftime('[%H:%M:%S]')+' Green wave delay: '+str(1/wsG)+'ms between jumps.'

def setwsB(NULL1,NULL2,nwsB,NULL3):
    global wsB
    wsB=nwsB[0]
    print time.strftime('[%H:%M:%S]')+' Blue wave delay: '+str(1/wsB)+'ms betweenjumps .'
    
def setwoR(NULL1,NULL2,nwoR,NULL3):
    global woR
    woR=nwoR[0]
    if woR==0:
        print time.strftime('[%H:%M:%S]')+' Red wavemode offlined.'
    if woR==1:
        print time.strftime('[%H:%M:%S]')+' Red wavemode onlined.'

def setwoG(NULL1,NULL2,nwoG,NULL3):
    global woG
    woG=nwoG[0]
    if woG==0:
        print time.strftime('[%H:%M:%S]')+' Green wavemode offlined.'
    if woG==1:
        print time.strftime('[%H:%M:%S]')+' Green wavemode onlined.'

def setwoB(NULL1,NULL2,nwoB,NULL3):
    global woB
    woB=nwoB[0]
    if woB==0:
        print time.strftime('[%H:%M:%S]')+' Blue wavemode offlined.'
    if woB==1:
        print time.strftime('[%H:%M:%S]')+' Blue wavemode onlined.'

def sendT(cV,dV):
    if cV=="R":
        if woR==0:
            sendSC(cV,dV)
        if woR==1:
            sendCW(cV,dV)
    elif cV=="G":
        if woG==0:
            sendSC(cV,dV)
        if woG==1:
            sendCW(cV,dV)
    elif cV=="B":
        if woB==0:
            sendSC(cV,dV)
        if woB==1:
            sendCW(cV,dV)

def sendSC(cV,dV):
    global lR, lG, lB
    if cV=="R":
        lR=dV
        write(pA,0,lR,lG,lB)
    elif cV=="G":
        lG=dV
        write(pA,0,lR,lG,lB)
    elif cV=="B":
        lB=dV
        write(pA,0,lR,lG,lB)

def sendCW(cV,dV):
    global lR, lG, lB, pR, pG, pB
    if cV=="R":
        lR=dV
        if srp==1:
            pR=pG
        elif rpR==1:
            pR=random.randint(0,numLights-1)
        else:
            pR=dpR
        write(cwR,pR,wsR,lR,fadeR)
    elif cV=="G":
        lG=dV
        if rpG==1:
            pG=random.randint(0,numLights-1)
        else:
            pG=dpG
        write(cwG,pG,wsG,lG,fadeG)
    elif cV=="B":
        lB=dV
        if srp==1:
            pB=pG
        elif rpB==1:
            pB=random.randint(0,numLights-1)
        else:
            pB=dpB
        write(cwB,pB,wsB,lB,fadeB)

def sendSCH(r,g,b):
    global lR, lG, lB
    lR=r
    lG=g
    lB=b
    write(pA,0,lR,lG,lB)

def write(i,p,r,g,b):
    s=0
    while s==0:
	global lW
	if outr==0 or time.clock()-lW>=(1./outr):
	    b_arr=[]
	    b_arr.append(bytearray(struct.pack("!B",i)))
	    b_arr.append(bytearray(struct.pack("!B",bytearray(struct.pack("!H",p))[0])))
	    b_arr.append(bytearray(struct.pack("!B",bytearray(struct.pack("!H",p))[1])))
	    b_arr.append(bytearray(struct.pack("!B",r)))
	    b_arr.append(bytearray(struct.pack("!B",g)))
	    b_arr.append(bytearray(struct.pack("!B",b)))
	    for k in b_arr:
		s1=0
		while s1==0:
		    incm_b=port.read(1)
		    if incm_b==struct.pack("!B",def_ret):
#DEBUG                        print "waiting:"+str(port.inWaiting())
			port.write(k)
			s1=1
#                    else:
#                        sys.stdout.write("DEBUG:"+incm_b)
#                        print 1./(time.clock()-lW)
#DEBUG                port.write(bytearray(struct.pack("!BHBBB",i,p,r,g,b)))
#           print 1./(time.clock()-lW)
	    lW=time.clock()
	    s=1


#this sends a solid color by addressing each light, it is slow
#I include it only for testing purposes
def sendSCslow(cV,dV):
    global lR, lG, lB
    if cV=="R":
        lR=dV
        for i in xrange(numLights):
            write(ns,i,lR,lG,lB)
    elif cV=="G":
        lG=dV
        for i in xrange(numLights):
            write(ns,i,lR,lG,lB)
    elif cV=="B":
        lB=dV
        for i in xrange(numLights):
            write(ns,i,lR,lG,lB)

main()
