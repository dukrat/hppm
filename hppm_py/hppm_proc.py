global psyon, com, pR, pG, pB, ourt, fps, sType, numLights, woR, woG, woB
global mR, mG, mB, wsR, wsG, wsB, pA, su, cwR, cwG, cwB, R, G, B, iR, iG, iB
global tiR, tiG, tiB, wR, wG, wB, sR, sG, sB, lR, lG, lB, lW, nwR, nwG, nwB
global port, fadeR, fadeG, fadeB, lightOn, chngBProp

psyon=0
com='COM4'
#set the fade speed of wave mode, 0 is off, 2 works best for 64 lights
fadeR=2
fadeG=2
fadeB=2
lightOn=1 #0, lights off on shutdown 1, lights on on shutdown
chngBProp=1 #if you send data in wave mode faster than the wave speed
#you can either display that data right away on the wave start pixel, 1
#or discard that data, 0

datar=30 #incoming number of values per second per channel, should match max
#these are the pixel values where waves will start
pR=11
pG=25
pB=40
outr=80 #framerate to output to arduino, over 80 is generally too fast
fps=0 #arduino framerate limit, may overload buffer, 0-255, 0 is no limiting
sType="LPD8806" #set to "LPD8806" or "WS2801", the strand type you have
numLights=52 #number lights you have
#a single strand of 32 lights strips is capable of addressing 65536 lights
#however the atmega238 only has memory for just over 64? lights in wave mode
#using the normal sketch and ? lights using the extended sketch
#the atmega2560 has memory for 313 lights in wave mode using the normal
#sketch and ? lights in wave mode using the extended sketch
#if you get an something with more memory you need to update the arduino code
#DI connects to pin 11 (or 51 if you have a Mega)
#CI connects to pin 13 (or 52 if you have a Mega)

#if for some reason you are running without the max part you can set the initial mode here
#this sets wavemode 0 off 1 on
woR=1
woG=1
woB=1
#these set the main mode
mR=0            #0 listen for audio
mG=0            #1 test colors interlaced
mB=0            #2 test colors sequentially
#this is the wave speed delays max 255ms
wsR=0
wsG=0
wsB=0
#the pixel values used for various signals, should match arduino
pA=255 #whole strip solid color
su=254 #set numLights, fps, protocol and maxBright, reserved
ns=250 #single pixel
#start wave on color origin
cwR=251
cwG=252
cwB=253
import OSC, serial, time, threading, datetime, struct
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
    print time.strftime('[%H:%M:%S]')+' Program started.'
    time.sleep(1.5) #pause for bootloader
    #define OSC server
    osc=OSC.ThreadingOSCServer(('127.0.0.1', 10233))
    osct=threading.Thread(target=osc.serve_forever)
    try:
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
        time.sleep(.100)
        if lightOn==0:
            sendSCH(0,0,0)
        else:
            sendSCH(maxBright,maxBright,maxBright)  
        print time.strftime('[%H:%M:%S]')+' Program exited.'
        
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
    global lR, lG, lB
    if cV=="R":
        lR=dV
        write(cwR,pR,wsR,lR,fadeR)
    elif cV=="G":
        lG=dV
        write(cwG,pG,wsG,lG,fadeG)
    elif cV=="B":
        lB=dV
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
        if time.clock()-lW>=(1./outr):
            lW=time.clock()
            port.write(bytearray(struct.pack("!BHBBB",i,p,r,g,b)))
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
