#the pixel values used for various signals, should match arduino
pA=255 #whole strip solid color
su=254 #set numLights, fps, protocol and maxBright, reserved
ns=250 #single pixel
pAns=248 #whole strip solid color but no show
nsns=249 #single pixel but no show
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
datar=config.getint("hppm_proc.py", "datar")
sType=config.get("hppm_proc.py", "sType")
use_ard_int=config.getint("hppm_proc.py", "use_ard_int")
if use_ard_int:
    com=config.get("hppm_proc.py", "com")
    if "/" not in com:
        com='\\\\.\\'+com
use_tcp=config.getint("hppm_proc.py", "use_tcp")
if use_ard_int or use_tcp:
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
    dpR=config.getint("hppm_proc.py", "dpR")
    dpG=config.getint("hppm_proc.py", "dpG")
    dpB=config.getint("hppm_proc.py", "dpB")
    rpR=config.getint("hppm_proc.py", "rpR")
    rpG=config.getint("hppm_proc.py", "rpG")
    rpB=config.getint("hppm_proc.py", "rpB")
    srp=config.getint("hppm_proc.py", "srp")
    outr=config.getint("hppm_proc.py", "outr")
    fps=config.getint("hppm_proc.py", "fps")
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
    use_osc_server=config.getint("hppm_proc.py", "use_osc_server")
    if use_osc_server:
        import OSC
    bind_ip=config.get("hppm_proc.py", "bind_ip")
    if bind_ip==0:
        temp_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        temp_sock.connect(('8.8.8.8', 0))
        bind_ip=temp_sock.getsockname()[0]
        temp_sock.close()
    bind_port=config.getint("hppm_proc.py", "bind_port")
use_gstreamer=config.getint("hppm_proc.py", "use_gstreamer")
if use_gstreamer:
    remote_osc_server=config.get("hppm_proc.py", "remote_osc_server")
    remote_osc_port=config.getint("hppm_proc.py", "remote_osc_port")
    if (use_ard_int or use_tcp) and (bind_ip=='127.0.0.1' or bind_ip=="localhost")  and (remote_osc_server=='127.0.0.1' or remote_osc_server=='localhost') and bind_port==remote_osc_port:
        use_local=1
    else:
        use_local=0
        import OSC
    import gi, re
    gi.require_version('Gst', '1.0')
    from gi.repository import GObject, Gst
    Gst.init(None)
    aud_sample_rate=config.getint("hppm_proc.py", "aud_sample_rate")
    aud_chans=config.getint("hppm_proc.py", "aud_chans")
    aud_depth=config.getint("hppm_proc.py", "aud_depth")
    spectrum_bands=1024
    low_db_adj=config.getfloat("hppm_proc.py", "low_db_adj")
    mid_db_adj=config.getfloat("hppm_proc.py", "mid_db_adj")
    high_db_adj=config.getfloat("hppm_proc.py", "high_db_adj")
    low_led_curv=config.getfloat("hppm_proc.py", "low_led_curv")
    mid_led_curv=config.getfloat("hppm_proc.py", "mid_led_curv")
    high_led_curv=config.getfloat("hppm_proc.py", "high_led_curv")
    low_led_adj=config.getint("hppm_proc.py", "low_led_adj")
    mid_led_adj=config.getint("hppm_proc.py", "mid_led_adj")
    high_led_adj=config.getint("hppm_proc.py", "high_led_adj")
    min_low_freq=config.get("hppm_proc.py", "min_low_freq")
    max_low_freq=config.get("hppm_proc.py", "max_low_freq")
    min_mid_freq=config.get("hppm_proc.py", "min_mid_freq")
    max_mid_freq=config.get("hppm_proc.py", "max_mid_freq")
    min_high_freq=config.get("hppm_proc.py", "min_high_freq")
    max_high_freq=config.get("hppm_proc.py", "max_high_freq")
    sample_interval=int((1./datar)*1000000000.)
    aud_dev_name=config.get("hppm_proc.py", "aud_dev_name")
    if aud_dev_name==0:
        sound_framework='autosoundsrc'
    else:
        if sys.platform.startswith('win32'):
            sound_framework='directsoundsrc device-name="'+aud_dev_name[0:31]+'" latency-time=1000 buffer-time=1001'
        elif sys.platform.startswith('darwin'):
            sound_framework='osxaudiosrc device="'+aud_dev_name+'"'
        else:
            sound_framework='alsasrc device="'+aud_dev_name+'"'

if sType=="LPD8806":
    sNum=0
    maxBright=127
elif sType=="LPD8806v2":
    sNum=4
    maxBright=127
elif sType=="WS2801":
    sNum=2
    maxBright=255
else:
    print(time.strftime('[%H:%M:%S]')+' Incorrect sType specified.  Exiting...')
    print(time.strftime('[%H:%M:%S]')+' Program exited.')
    exit()

if psyon:
    try:
        import psyco
        psyco.full()
    except ImportError:
        psyon=0
        pass
tcp_sock='NULL'
quit_list=[]


class SignalExit:
    exit_v = False


    def __init__(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)


    def signal_handler(self, signum, frame):
       print(time.strftime('[%H:%M:%S]') + ' Requested exit.')
       self.exit_v = True


sigExit = SignalExit()


def initBP(port): #Test if BP is already online, may get out of some modes TBR
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
    port = serial.Serial(com, 115200, timeout=1.1)
    #  initBP(port) #TBR
    time.sleep(1.5) #pause for bootloader
    return port

def start_tcp(tcp_server, tcp_port):
    import socket
    s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
    try:
        s.connect((socket.gethostbyname(tcp_server), tcp_port))
        return s
    except:
        print(time.strftime('[%H:%M:%S]')+' Could not connect to TCP Server.')
        s.close()
        return 'NULL'
#        if use_gstreamer:
#            gi_thread.quit()
#        print time.strftime('[%H:%M:%S]')+' Program exited.'
#        exit()
    

def main():
    print(time.strftime('[%H:%M:%S]')+' Program started.')
    global tcp_sock,quit_list
    if use_tcp:
        tcp_sock=start_tcp(config.get("hppm_proc.py", "tcp_server"),config.getint("hppm_proc.py", "tcp_port"))
    quit_list.append(tcp_sock)
    if use_gstreamer:
        pipeline,bus=start_gst()
        quit_list.append(pipeline)
        quit_list.append(bus)
        if not use_local:
            global client
            client=setup_osc_client()
            quit_list.append(client)
        else:
            quit_list.append('NULL')
    else:
        quit_list.append('NULL')
        quit_list.append('NULL')
        quit_list.append('NULL')
    if use_ard_int:
        port=start_ard()
        quit_list.append(port)
    else:
        port='NULL'
        quit_list.append('NULL')
    if use_ard_int or use_tcp:
        write(su,numLights-1,fps,chngBProp+sNum,0,port,tcp_sock)
        if use_osc_server:
            osc,osct=start_osc_server()
            quit_list.append(osc)
            quit_list.append(osct)
        else:
            quit_list.append('NULL')
            quit_list.append('NULL')
        while True:
            avg()
            if mG==1:
                testG(port,tcp_sock)
            elif mG==2:
                testsG(port,tcp_sock)
            elif mG==3:
                rwalkG(port,tcp_sock)
            else:
                colorG(port,tcp_sock)
            if mR==1:
                testR(port,tcp_sock)
            elif mR==2:
                testsR(port,tcp_sock)
            elif mR==3:
                rwalkR(port,tcp_sock)
            else:
                colorR(port,tcp_sock)
            if mB==1:
                testB(port,tcp_sock)
            elif mB==2:
                testsB(port,tcp_sock)
            elif mB==3:
                rwalkB(port,tcp_sock)
            else:
                colorB(port,tcp_sock)
            if psyon:
                time.sleep(0) #needed for psyco
            if sigExit.exit_v:
                quit_program(quit_list)
    else:
        quit_list.append('NULL')
        quit_list.append('NULL')
        while True:
            if psyon:
                time.sleep(0) #needed for psyco
            if sigExit.exit_v:
                quit_program(quit_list)

def quit_program(quit_list):
    (tcp_sock,pipeline,bus,client,port,osc,osct) = quit_list
    print(time.strftime('[%H:%M:%S]')+' Exiting...')
    if use_gstreamer:
        pipeline.set_state(Gst.State.NULL)
        bus.remove_watch()
        if not use_local:
            client.close()
        gi_thread.quit()
    if use_ard_int or use_tcp:
        if use_osc_server:
            osc.close()
            osct.join()
#we send these twice, as the first isn't always proc'd
        if lightOn==0:
            sendSCH(0,0,0,port,tcp_sock)
            sendSCH(0,0,0,port,tcp_sock)
        else:
            sendSCH(maxBright,maxBright,maxBright,port,tcp_sock)
            sendSCH(maxBright,maxBright,maxBright,port,tcp_sock)
        if use_ard_int:
            port.close()
        if tcp_sock!='NULL':
            tcp_sock.close()
    print(time.strftime('[%H:%M:%S]')+' Program exited.')
    exit()


def colorR(port,tcp_sock):
    global wR
    wR=nwR
    sendT("R",wR,port,tcp_sock)

def colorG(port,tcp_sock):
    global wG
    wG=nwG
    sendT("G",wG,port,tcp_sock)

def colorB(port,tcp_sock):
    global wB
    wB=nwB
    sendT("B",wB,port,tcp_sock)

def testR(port,tcp_sock):
    global tiR
    if tiR>maxBright:
        sendT("R",(maxBright*2)-tiR,port,tcp_sock)
    else:
        sendT("R",tiR,port,tcp_sock)
    tiR=(tiR+1)%(maxBright*2)

def testG(port,tcp_sock):
    global tiG
    if tiG>maxBright:
        sendT("G",(maxBright*2)-tiG,port,tcp_sock)
    else:
        sendT("G",tiG,port,tcp_sock)
    tiG=(tiG+1)%(maxBright*2)

def testB(port,tcp_sock):
    global tiB
    if tiB>maxBright:
        sendT("B",(maxBright*2)-tiB,port,tcp_sock)
    else:
        sendT("B",tiB,port,tcp_sock)
    tiB=(tiB+1)%(maxBright*2)

def testsR(port,tcp_sock):
    for i in range(maxBright+1):
        sendT("R",i,port,tcp_sock)
    for i in range(maxBright):
        sendT("R",maxBright-1-i,port,tcp_sock)

def testsG(port,tcp_sock):
    for i in range(maxBright+1):
        sendT("G",i,port,tcp_sock)
    for i in range(maxBright):
        sendT("G",maxBright-1-i,port,tcp_sock)

def testsB(port,tcp_sock):
    for i in range(maxBright+1):
        sendT("B",i,port,tcp_sock)
    for i in range(maxBright):
        sendT("B",maxBright-1-i,port,tcp_sock)

def rwalkR(port,tcp_sock):
    sendT("R",random.randint(minrwR, maxrwR),port,tcp_sock)
    
def rwalkG(port,tcp_sock):
    sendT("G",random.randint(minrwG, maxrwG),port,tcp_sock)

def rwalkB(port,tcp_sock):
    sendT("B",random.randint(minrwB, maxrwB),port,tcp_sock)

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
    for i in range(asR):
        nwR=nwR+aR[(aiR-i+datar)%datar]
    nwR=int(round(nwR/asR))
    for i in range(asG):
        nwG=nwG+aG[(aiG-i+datar)%datar]
    nwG=int(round(nwG/asG))
    for i in range(asB):
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
    print(time.strftime('[%H:%M:%S]')+' Red averaging time: '+str(1000*sR/datar)+'ms.')

def setsG(NULL1,NULL2,nsG,NULL3):
    global sG
    sG=nsG[0]
    print(time.strftime('[%H:%M:%S]')+' Green averaging time: '+str(1000*sG/datar)+'ms.')

def setsB(NULL1,NULL2,nsB,NULL3):
    global sB
    sB=nsB[0]
    print(time.strftime('[%H:%M:%S]')+' Blue averaging time: '+str(1000*sB/datar)+'ms.')

def setmR(NULL1,NULL2,nmR,NULL3):
    global mR
    mR=nmR[0]
    if mR==1:
        global tiR
        tiR=0
        print(time.strftime('[%H:%M:%S]')+' Red in test mode.')
    elif mR==2:
        print(time.strftime('[%H:%M:%S]')+' Red in sequential test mode.')
    else:
        print(time.strftime('[%H:%M:%S]')+' Red in color mode.')

def setmG(NULL1,NULL2,nmG,NULL3):
    global mG
    mG=nmG[0]
    if mG==1:
        global tiG
        tiG=0
        print(time.strftime('[%H:%M:%S]')+' Green in test mode.')
    elif mG==2:
        print(time.strftime('[%H:%M:%S]')+' Green in sequential test mode.')
    else:
        print(time.strftime('[%H:%M:%S]')+' Green in color mode.')

def setmB(NULL1,NULL2,nmB,NULL3):
    global mB
    mB=nmB[0]
    if mB==1:
        global tiB
        tiB=0
        print(time.strftime('[%H:%M:%S]')+' Blue in test mode.')
    elif mB==2:
        print(time.strftime('[%H:%M:%S]')+' Blue in sequential test mode.')
    else:
        print(time.strftime('[%H:%M:%S]')+' Blue in color mode.')

def setwsR(NULL1,NULL2,nwsR,NULL3):
    global wsR
    wsR=nwsR[0]
    print(time.strftime('[%H:%M:%S]')+' Red wave delay: '+str(1/wsR)+'ms between jumps.')

def setwsG(NULL1,NULL2,nwsG,NULL3):
    global wsG
    wsG=nwsG[0]
    print(time.strftime('[%H:%M:%S]')+' Green wave delay: '+str(1/wsG)+'ms between jumps.')

def setwsB(NULL1,NULL2,nwsB,NULL3):
    global wsB
    wsB=nwsB[0]
    print(time.strftime('[%H:%M:%S]')+' Blue wave delay: '+str(1/wsB)+'ms betweenjumps .')
    
def setwoR(NULL1,NULL2,nwoR,NULL3):
    global woR
    woR=nwoR[0]
    if woR==0:
        print(time.strftime('[%H:%M:%S]')+' Red wavemode offlined.')
    if woR==1:
        print(time.strftime('[%H:%M:%S]')+' Red wavemode onlined.')

def setwoG(NULL1,NULL2,nwoG,NULL3):
    global woG
    woG=nwoG[0]
    if woG==0:
        print(time.strftime('[%H:%M:%S]')+' Green wavemode offlined.')
    if woG==1:
        print(time.strftime('[%H:%M:%S]')+' Green wavemode onlined.')

def setwoB(NULL1,NULL2,nwoB,NULL3):
    global woB
    woB=nwoB[0]
    if woB==0:
        print(time.strftime('[%H:%M:%S]')+' Blue wavemode offlined.')
    if woB==1:
        print(time.strftime('[%H:%M:%S]')+' Blue wavemode onlined.')

def sendT(cV,dV,port,tcp_sock):
    if cV=="R":
        if woR==0:
            sendSC(cV,dV,port,tcp_sock)
        if woR==1:
            sendCW(cV,dV,port,tcp_sock)
    elif cV=="G":
        if woG==0:
            sendSC(cV,dV,port,tcp_sock)
        if woG==1:
            sendCW(cV,dV,port,tcp_sock)
    elif cV=="B":
        if woB==0:
            sendSC(cV,dV,port,tcp_sock)
        if woB==1:
            sendCW(cV,dV,port,tcp_sock)

def sendSC(cV,dV,port,tcp_sock):
    global lR, lG, lB
    if cV=="R":
        lR=dV
        write(pA,0,lR,lG,lB,port,tcp_sock)
    elif cV=="G":
        lG=dV
        write(pA,0,lR,lG,lB,port,tcp_sock)
    elif cV=="B":
        lB=dV
        write(pA,0,lR,lG,lB,port,tcp_sock)

def sendCW(cV,dV,port,tcp_sock):
    global lR, lG, lB, pR, pG, pB
    if cV=="R":
        lR=dV
        if srp==1:
            pR=pG
        elif rpR==1:
            pR=random.randint(0,numLights-1)
        else:
            pR=dpR
        write(cwR,pR,wsR,lR,fadeR,port,tcp_sock)
    elif cV=="G":
        lG=dV
        if rpG==1:
            pG=random.randint(0,numLights-1)
        else:
            pG=dpG
        write(cwG,pG,wsG,lG,fadeG,port,tcp_sock)
    elif cV=="B":
        lB=dV
        if srp==1:
            pB=pG
        elif rpB==1:
            pB=random.randint(0,numLights-1)
        else:
            pB=dpB
        write(cwB,pB,wsB,lB,fadeB,port,tcp_sock)

def sendSCH(r,g,b,port,tcp_sock):
    global lR, lG, lB
    lR=r
    lG=g
    lB=b
    write(pA,0,lR,lG,lB,port,tcp_sock)

def write(i,p,r,g,b,port,tcp_sock_local):
    global lW
    time_waited=time.clock()-lW
    if outr and time_waited<(1./outr):
        time.sleep((1./outr)-time_waited)
    b_arr=struct.pack("!BHBBB",i,p,r,g,b)
    if use_tcp:
        try:
            tcp_sock_local.send(b_arr)
        except:
            print(time.strftime('[%H:%M:%S]')+' TCP send error, trying to reconnect...')
            global tcp_sock,quit_list
            if tcp_sock!='NULL':
                tcp_sock_local.close()
            tcp_sock=start_tcp(config.get("hppm_proc.py", "tcp_server"),config.getint("hppm_proc.py", "tcp_port"))
            if tcp_sock!='NULL':
                print(time.strftime('[%H:%M:%S]')+' TCP reconnected.')
            quit_list[0]=tcp_sock
    if use_ard_int:
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
def sendSCslow(cV,dV,port,tcp_sock):
    global lR, lG, lB
    if cV=="R":
        lR=dV
        for i in range(numLights):
            write(ns,i,lR,lG,lB,port,tcp_sock)
    elif cV=="G":
        lG=dV
        for i in range(numLights):
            write(ns,i,lR,lG,lB,port,tcp_sock)
    elif cV=="B":
        lB=dV
        for i in range(numLights):
            write(ns,i,lR,lG,lB,port,tcp_sock)

def setup_osc_client():
    ######from twisted.internet import reactor
    ######from txosc import osc, dispatch, async
    ######client=async.DatagramClientProtocol()
    ######reactor.listenUDP(0, client)
    ######def sendOSC(element):
    ######      client.send(element, ("hostip", 10233))

    ##import socket
    ##from txosc import osc, sync
    ##client=sync.UdpSender("hostip", 10233)
    import socket
    client = OSC.OSCClient()
    client.connect((socket.gethostbyname(remote_osc_server), remote_osc_port))
    return client

def freq_to_band(freq):
    if freq=='None':
        return None
    else:
        return int((2.*float(freq)*float(spectrum_bands)-(float(aud_sample_rate)/2.))/float(aud_sample_rate))
   #return int(float(freq)/(aud_sample_rate/spectrum_bands))+1

def playerbin_message(bus,message):
    if message.type == Gst.MessageType.ELEMENT:
        struct = message.get_structure()
        if struct.get_name() == 'spectrum':
            matches = re.search(r'magnitude=\(float\){([^}]+)}', struct.to_string())
            m = [float(x) for x in matches.group(1).split(',')]
            low  = max(m[freq_to_band(min_low_freq):freq_to_band(max_low_freq)])
            mid  = max(m[freq_to_band(min_mid_freq):freq_to_band(max_mid_freq)])
            high = max(m[freq_to_band(min_high_freq):freq_to_band(max_high_freq)])

            low_lin=10**((low+low_db_adj)/20.)
            mid_lin=10**((mid+mid_db_adj)/20.)
            high_lin=10**((high+high_db_adj)/20.)
            low_adj=((low_lin**float(low_led_curv))*float(maxBright))+float(low_led_adj)
            mid_adj=((mid_lin**float(mid_led_curv))*float(maxBright))+float(mid_led_adj)
            high_adj=((high_lin**float(high_led_curv))*float(maxBright))+float(high_led_adj)

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
            if use_local:
                setR('NULL','NULL',[low_adj],'NULL')
                setG('NULL','NULL',[mid_adj],'NULL')
                setB('NULL','NULL',[high_adj],'NULL')
            else:
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

#DEBUG    else:
#DEBUG        print message
    return True

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

    pipeline = Gst.parse_launch(sound_framework+' ! \
                                audio/x-raw,rate='+str(aud_sample_rate)+',channels='+str(aud_chans)+',depth='+str(aud_depth)+' ! \
                                spectrum interval='+str(sample_interval)+' bands='+str(spectrum_bands)+' ! fakesink')


#    pipeline = Gst.parse_launch(sound_framework+' device-name="'+device_name+'" latency-time=1000 buffer-time=1001 ! \
#                                spectrum interval='+str(sample_interval)+' ! fakesink')

    bus = pipeline.get_bus()
    #bus.add_signal_watch()
    #bus.connect('message', playerbin_message)
    bus.add_watch(0, playerbin_message)
    pipeline.set_state(Gst.State.PLAYING)
    print(time.strftime('[%H:%M:%S]')+' pipeline PLAYING')
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

#convert to not global:
#wR wG wB
#nwR nwG nwB
#lR lG lB
#pR pG pB
#lW
#
#globals:
#client
#R iR
#G iG
#B iB
#sR
#sG
#sB
#mG tiG
#mR tiR
#mB tiB
#wsR
#wsG
#wsB
#woR
#woB
#woG
