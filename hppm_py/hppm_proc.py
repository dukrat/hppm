#global psyon, com, dpR, dpG, dpB, ourt, fps, sType, numLights, woR, woG, woB
#global mR, mG, mB, wsR, wsG, wsB, pA, su, cwR, cwG, cwB, R, G, B, iR, iG, iB
#global tiR, tiG, tiB, wR, wG, wB, sR, sG, sB, lR, lG, lB, lW, nwR, nwG, nwB
#global port, fadeR, fadeG, fadeB, lightOn, chngBProp, pR, pG, pB, exit_v

#the pixel values used for various signals, should match arduino
pA=255 #whole strip solid color
su=254 #set numLights, fps, protocol and maxBright, reserved
ns=250 #single pixel
#start wave on color origin
cwR=251
cwG=252
cwB=253
def_ret=17 #time to send a new byte
import serial, time, threading, datetime, struct, random, ConfigParser
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
bind_ip=config.get("hppm_proc.py", "bind_ip")
if bind_ip==0:
    temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    temp_sock.connect(('8.8.8.8', 0))
    bind_ip=temp_sock.getsockname()[0]
    temp_sock.close()
bind_port=config.getint("hppm_proc.py", "bind_port")
use_gstreamer=config.getint("hppm_proc.py", "use_gstreamer")
if use_gstreamer:
    remote_osc_server='127.0.0.1'
    remote_osc_port=10233
    import gi, re
    gi.require_version('Gst', '1.0')
    from gi.repository import GObject, Gst
    Gst.init(None)
    Fs = 44100
    N = 128
    db_boost=30
    sample_interval=int((1./datar)*1000000000.)
    specify_sound_dev=1
    if specify_sound_dev:
        device_name="Line In (Realtek High Definition Audio)"
        if sys.platform.startswith('win32'):
            sound_framework='directsoundsrc'
        elif sys.platform.startswith('darwin'):
            sound_framework='iHateOSX'
        else:
            sound_framework='alsasrc'

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
        port.write('y')     # confirm entry to bridge

def start_osc_server():
    import OSC
    #define OSC server
    osc=OSC.ThreadingOSCServer((bind_ip, bind_port))
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
    return osc,osct

def start_ard():
    #setup the arduino program
    global maxBright
    if sType=="LPD8806":
        sNum=0
        maxBright=127
    elif sType=="WS2801":
        sNum=2
        maxBright=255
    else:
        print time.strftime('[%H:%M:%S]')+' Incorrect sType specified.  Exiting...'
        port.close()
        print time.strftime('[%H:%M:%S]')+' Program exited.'
        exit()
    write(su,numLights-1,fps,chngBProp+sNum,0)

port = serial.Serial('\\\\.\\'+com, 115200, timeout=1.1)

def main():
    #  initBP() #TBR
    print time.strftime('[%H:%M:%S]')+' Program started.'
    time.sleep(1.5) #pause for bootloader
    start_ard()
    osc,osct=start_osc_server()
    if use_gstreamer:
        global client
        client=setup_osc_client()
        pipeline,bus=start_gst()
    while True:
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
            if use_gstreamer:
                quit_program(osc,osct,pipeline,bus,client)
            else:
                quit_program(osc,osct,'NULL','NULL','NULL')

def quit_program(osc,osct,pipeline,bus,client):
    if use_gstreamer:
        pipeline.set_state(Gst.State.NULL)
        bus.remove_watch()
        client.close()
        gi_thread.quit()
    osc.close()
    osct.join()
#we send these twice, as the first isn't always proc'd
    if lightOn==0:
        sendSCH(0,0,0)
        sendSCH(0,0,0)
    else:
        sendSCH(maxBright,maxBright,maxBright)
        sendSCH(maxBright,maxBright,maxBright)
    port.close()
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
    global lW
    time_waited=time.clock()-lW
    if outr and time_waited<(1./outr):
        time.sleep((1./outr)-time_waited)
    b_arr=struct.pack("!BHBBB",i,p,r,g,b)
    for k in b_arr:
        while True:
            incm_b=port.read(1)
            if incm_b==struct.pack("!B",def_ret):
#DEBUG                          print "waiting:"+str(port.inWaiting())
                port.write(bytearray(k))
                break
#                    else:
#                        sys.stdout.write("DEBUG:"+incm_b)
#                        print 1./(time.clock()-lW)
#DEBUG                  port.write(bytearray(struct.pack("!BHBBB",i,p,r,g,b)))
#           print 1./(time.clock()-lW)
    lW=time.clock()

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

def setup_osc_client():
    ######from twisted.internet import reactor
    ######from txosc import osc, dispatch, async
    ######client=async.DatagramClientProtocol()
    ######reactor.listenUDP(0, client)
    ######def sendOSC(element):
    ######      client.send(element, ("18.83.7.199", 10233))

    ##import socket
    ##from txosc import osc, sync
    ##client=sync.UdpSender("18.83.7.199", 10233)

    import OSC
    client = OSC.OSCClient()
    client.connect((remote_osc_server, remote_osc_port))
    return client

def n(F):
    return int(float(F)/(Fs/N))+1

def playerbin_message(bus,message):
    if message.type == Gst.MessageType.ELEMENT:
        struct = message.get_structure()
        if struct.get_name() == 'spectrum':
            matches = re.search(r'magnitude=\(float\){([^}]+)}', struct.to_string())
            m = [float(x) for x in matches.group(1).split(',')]
            #print n(125)
            #print n(350)
            #print n(1500)
            #print n(6000)
            low  = max(m[:n(125)])
            mid  = max(m[n(350):n(1500)])
            high = max(m[n(6000):])

            low_lin=10**((low+db_boost)/20.)
            mid_lin=10**((mid+db_boost)/20.)
            high_lin=10**((high+db_boost)/20.)
            low_adj=((low_lin**1.5)*255.)-1.
            mid_adj=((mid_lin**1.5)*255.)-1.
            high_adj=((high_lin**1.5)*255.)-1.

#            print "%03.1f %03.1f %03.1f %-30s %-30s %30s" % (low_adj, mid_adj, high_adj,
#                                                            "x"*int(low_adj/10),
#                                                            " "*int((30-(mid_adj/10))/2)+"x"*int(mid_adj/10),
#                                                            "x"*int(high_adj/10),
#                                                            )

######              sendOSC(osc.Message("/R", int(low_adj)))
######              sendOSC(osc.Message("/G", int(mid_adj)))
######              sendOSC(osc.Message("/B", int(high_adj)))

##              client.send(osc.Message("/R", int(low_adj)))
##              client.send(osc.Message("/G", int(mid_adj)))
##              client.send(osc.Message("/B", int(high_adj)))
            import OSC
            b = OSC.OSCBundle()
            osc_message=OSC.OSCMessage()
            osc_message.setAddress("/R")
            osc_message.append(int(low_adj))
            #client.send(osc_message)
            b.append(osc_message)
            osc_message=OSC.OSCMessage()
            osc_message.setAddress("/G")
            osc_message.append(int(mid_adj))
            #client.send(osc_message)
            b.append(osc_message)
            osc_message=OSC.OSCMessage()
            osc_message.setAddress("/B")
            osc_message.append(int(high_adj))
            #client.send(osc_message)
            b.append(osc_message)
            client.send(b)
#            client.send(OSC.OSCMessage("/R"+[int(low_adj)]))
#            client.send(OSC.OSCMessage("/G"+[int(mid_adj)]))
#            client.send(OSC.OSCMessage("/B"+[int(high_adj)]))

    else:
        print message
    return True

def test_message(bus, message):
    print 'pang'

def start_gst():
    #pipeline = Gst.parse_launch(
    #  'pulsesrc device="alsa_output.pci-0000_00_1b.0.analog-surround-50.monitor" ! spectrum interval=16666667 ! fakesink')
    ##pipeline = Gst.parse_launch('directsoundsrc device-name="Line In (Realtek High Definition Audio)" latency-time=1000 buffer-time=8000 ! \
    ##                              spectrum interval=16666667 ! tee name=t \
    ##                              t. ! queue ! udpsink blocksize=512 host= \
    ##                              t. ! queue ! udpsink blocksize=512 host=')
    #pipeline = Gst.parse_launch('directsoundsrc device-name="Line In (Realtek High Definition Audio)" latency-time=1000 buffer-time=2000 ! \
    #                            spectrum interval=33333333 ! tee name=t \
    #                            t. ! queue ! udpsink blocksize=512 host= \
    #                            t. ! queue ! udpsink blocksize=512 host=')
    #pipeline = Gst.parse_launch('directsoundsrc device-name="Microphone (GN 9350)" ! spectrum interval=16666667 ! directsoundsink')

    pipeline = Gst.parse_launch(sound_framework+' device-name="'+device_name+'" latency-time=1000 buffer-time=1001 ! \
                                spectrum interval='+str(sample_interval)+' ! fakesink')
    bus = pipeline.get_bus()
    #bus.add_signal_watch()
    #bus.connect('message', playerbin_message)
    bus.add_watch(0, playerbin_message)
    pipeline.set_state(Gst.State.PLAYING)
    print time.strftime('[%H:%M:%S]')+' pipeline PLAYING'
    return pipeline,bus

if use_gstreamer:
    main_thread=threading.Thread(target=main)
    main_thread.start()
    gi_thread=GObject.MainLoop()
    gi_thread.run()
else:
    main()
## Wait until error or EOS.
#msg = bus.timed_pop_filtered(Gst.CLOCK_TIME_NONE,
#Gst.MessageType.ERROR | Gst.MessageType.EOS)
#print msg
# To find devices
# sink=Gst.ElementFactory.make("directsoundsrc")
# 
#caps audio/x-raw, format=(string)S16LE, layout=(string)interleaved, rate=(int)44100, channels=(int)2
#
