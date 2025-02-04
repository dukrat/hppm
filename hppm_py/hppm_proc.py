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
import serial, time, threading, datetime, struct, random, configparser
import signal, sys
config=configparser.RawConfigParser()
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
        import pythonosc.udp_client, pythonosc.osc_bundle_builder, pythonosc.osc_message_builder, pythonosc.dispatcher, pythonosc.osc_server
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
        import pythonosc.udp_client, pythonosc.osc_bundle_builder, pythonosc.osc_message_builder, pythonosc.dispatcher, pythonosc.osc_server
    import gi, re
    gi.require_version('Gst', '1.0')
    from gi.repository import Gst, GLib
    Gst.init(None)
    aud_sample_rate=44000
    aud_chans=2
    aud_depth=8
    spectrum_bands=1024
    low_db_adj=config.getfloat("hppm_proc.py", "low_db_adj")
    mid_db_adj=config.getfloat("hppm_proc.py", "mid_db_adj")
    high_db_adj=config.getfloat("hppm_proc.py", "high_db_adj")
    low_led_log_shift=config.getfloat("hppm_proc.py", "low_led_log_shift")
    mid_led_log_shift=config.getfloat("hppm_proc.py", "mid_led_log_shift")
    high_led_log_shift=config.getfloat("hppm_proc.py", "high_led_log_shift")
    low_led_log_stretch=config.getfloat("hppm_proc.py", "low_led_log_stretch")
    mid_led_log_stretch=config.getfloat("hppm_proc.py", "mid_led_log_stretch")
    high_led_log_stretch=config.getfloat("hppm_proc.py", "high_led_log_stretch")
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
            sound_framework='wasapisrc device="'+aud_dev_name+'" low-latency=true use-audioclient3=true'
        elif sys.platform.startswith('darwin'):
            sound_framework='osxaudiosrc device="'+aud_dev_name+'"'
        else:
            sound_framework='alsasrc device="'+aud_dev_name+'"'

if sType=="LPD8806":
    sNum=0
    maxBright=255
elif sType=="LPD8806v2":
    sNum=4
    maxBright=255
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
use_nagios=config.getint("hppm_proc.py", "use_nagios")
if use_nagios:
    import requests
    from requests.packages import urllib3
    requests.packages.urllib3.disable_warnings(category=urllib3.exceptions.InsecureRequestWarning)
    from copy import copy
    # get ready to make the request to nagios
    status_url = config.get("hppm_proc.py", "nagios_status_uri")
    auth_obj=requests.auth.HTTPBasicAuth(config.get("hppm_proc.py","nagios_user"),
                            config.get("hppm_proc.py","nagios_pass"))
    timeout = 10.0
    hl_params = {'query': 'hostlist', 'details': 'true', 'hoststatus': 'up' +
                 ' down unreachable pending'}
    sl_params = {'query': 'servicelist', 'details': 'true', 'hoststatus':
                 'up down unreachable pending', 'servicestatus': 'ok warning' +
                 ' critical unknown pending'}
    rBrightR = config.getint("hppm_proc.py", "rBrightR")
    rBrightG = config.getint("hppm_proc.py", "rBrightG")
    rBrightB = config.getint("hppm_proc.py", "rBrightB")
    bBrightR = config.getint("hppm_proc.py", "bBrightR")
    bBrightG = config.getint("hppm_proc.py", "bBrightG")
    bBrightB = config.getint("hppm_proc.py", "bBrightB")
    gBrightR = config.getint("hppm_proc.py", "gBrightR")
    gBrightG = config.getint("hppm_proc.py", "gBrightG")
    gBrightB = config.getint("hppm_proc.py", "gBrightB")

tcp_sock='NULL'
quit_list={}

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
    #setup and start the OSC server
    oscd = pythonosc.dispatcher.Dispatcher()
    oscd.map('/R', setR)
    oscd.map('/G', setG)
    oscd.map('/B', setB)
    oscd.map('/mR', setmR)
    oscd.map('/mG', setmG)
    oscd.map('/mB', setmB)
    oscd.map('/sR', setsR)
    oscd.map('/sG', setsG)
    oscd.map('/sB', setsB)
    oscd.map('/wsR', setwsR)
    oscd.map('/wsG', setwsG)
    oscd.map('/wsB', setwsB)
    oscd.map('/woR', setwoR)
    oscd.map('/woG', setwoG)
    oscd.map('/woB', setwoB)
    osca=(bind_ip, bind_port)
    osc=pythonosc.osc_server.ThreadingOSCUDPServer(osca, oscd)
    osct=threading.Thread(target=osc.serve_forever)
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

def main():
    print(time.strftime('[%H:%M:%S]')+' Program started.')
    global tcp_sock,quit_list
    if use_tcp:
        tcp_sock=start_tcp(config.get("hppm_proc.py", "tcp_server"),config.getint("hppm_proc.py", "tcp_port"))
        quit_list['tcp_sock']=tcp_sock
    if use_gstreamer:
        pipeline,bus=start_gst()
        quit_list['pipeline']=pipeline
        quit_list['bus']=bus
        if not use_local:
            global client
            client=setup_osc_client()
            quit_list['client']=client
    port='NULL'
    if use_ard_int:
        port=start_ard()
    quit_list['port']=port
    if use_ard_int or use_tcp:
        write(su,numLights-1,fps,chngBProp+sNum,0,port,tcp_sock)
        if use_osc_server:
            osc,osct=start_osc_server()
            quit_list['osc']=osc
            quit_list['osct']=osct
        if use_nagios:
            # make some mutables for pass by ref
            data_lst = []
            rCount = [0]
            bCount = [0]
            gCount = [0]
            offset = [0]
            lastdata_lst = []
            lastrCount = [0]
            lastbCount = [0]
            lastgCount = [0]
            lastFrame = [None] * numLights
            quiet_sets=0
            nagQuietThreshR=config.getint("hppm_proc.py", "nagQuietThreshR")
            nagQuietThreshG=config.getint("hppm_proc.py", "nagQuietThreshG")
            nagQuietThreshB=config.getint("hppm_proc.py", "nagQuietThreshB")
            nagQuietFrames=config.getint("hppm_proc.py", "nagQuietFrames")
            data_t=nagios_setup(data_lst, rCount, bCount, gCount, port,
                                lastdata_lst, lastrCount, lastbCount, lastgCount)
            quit_list['nagios']=data_t
        while True:
            avg()
            if use_nagios:
                if nwR <= nagQuietThreshR and nwG <= nagQuietThreshG and nwB < nagQuietThreshB:
                    quiet_srts=quiet_sets+1
                else:
                    quiet_sets=0
                if quiet_sets > nagQuietFrames:
                    data_t=nagios_sends(data_t,data_lst, rCount, bCount, gCount, port, offset,
                         lastdata_lst, lastrCount, lastbCount, lastgCount, lastFrame)
                    quit_list['nagios']=data_t
                    time.sleep(.2)
                else:
                    main_sends(port)
            else:
                main_sends(port)
            if psyon:
                time.sleep(0) #needed for psyco
            if sigExit.exit_v:
                quit_program(quit_list)
    else:
        while True:
            if psyon:
                time.sleep(0) #needed for psyco
            if sigExit.exit_v:
                quit_program(quit_list)

def main_sends(port):
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

def nagios_sends(data_t,rCount,bCount,gCount,data_lst,port,offset,
                 lastdata_t,lastrCount,lastbCount,lastgCount,lastFrame):
    data_t.join(0)
    if data_t.is_alive() is not True:
    # the timer joined
    # let us know if there are new issues or resolutions
        if bCount[0] > lastbCount[0]:
            flash(2,port)
        elif gCount[0] > lastgCount[0]:
            flash(3,port)
        elif rCount[0] > lastrCount[0]:
            flash(1,port)
        # copy the data to be thread safe
        lastdata_lst = copy(data_lst)
        lastrCount = copy(rCount)
        lastbCount = copy(bCount)
        lastgCount = copy(gCount)
        # clean up
        data_lst = []
        rCount = [0]
        bCount = [0]
        gCount = [0]
        # and set the timer to run again
        data_t = threading.Timer(60.0, getNagData,
                    args=(hl_params, auth_obj,
                    sl_params, status_url, timeout, ccache_file,
                    data_lst, rCount, bCount, gCount, port))
        data_t.start()
    # display the data
    pushNagFrame(offset, tcp_sock, lastFrame, lastdata_lst, lastrCount,
                lastbCount, lastgCount,port)
    return data_t

def nagios_setup(data_lst, rCount, bCount, gCount, port,
                 lastdata_list, lastrCount, lastbCount, lastgCount):
    data_i = threading.Thread(target=getNagData, args=(hl_params,
        auth_obj, sl_params, status_url, timeout, data_lst,
        rCount, bCount, gCount, port))
    print(time.strftime('[%H:%M:%S]') + ' Getting initial nagios data...')
    data_i.start()
    data_i.join()
    print(time.strftime('[%H:%M:%S]') + ' Got initial nagios data.')
    # copy the first set of data to be thread safe
    lastdata_lst = copy(data_lst)
    lastrCount = copy(rCount)
    lastbCount = copy(bCount)
    lastgCount = copy(gCount)
    data_lst = []
    rCount = [0]
    bCount = [0]
    gCount = [0]
    data_t = threading.Timer(60.0, getNagData, args=(hl_params,
        auth_obj, sl_params, status_url, timeout,
        data_lst, rCount, bCount, gCount, port))
    data_t.start()
    return data_t

def quit_program(quit_list):
    print(time.strftime('[%H:%M:%S]')+' Exiting...')
    if 'pipeline' in quit_list:
        quit_list['pipeline'].set_state(Gst.State.NULL)
        quit_list['bus'].remove_watch()
        if 'client' in quit_list:
            quit_list['client'].close()
        gi_thread.quit()
    if 'nagios' in quit_list:
        quit_list['nagios'].cancel()
        if quit_list['nagios'].is_alive():
            quit_list['nagios'].join()
    if 'osc' in quit_list:
        quit_list['osc'].close()
        quit_list['osct'].join()
    if use_ard_int or use_tcp:
#we send these twice, as the first isn't always proc'd
        if lightOn==0:
            sendSCH(0,0,0,quit_list['port'],quit_list['tcp_sock'])
            sendSCH(0,0,0,quit_list['port'],quit_list['tcp_sock'])
        else:
            sendSCH(maxBright,maxBright,maxBright,quit_list['port'],quit_list['tcp_sock'])
            sendSCH(maxBright,maxBright,maxBright,quit_list['port'],quit_list['tcp_sock'])
    if  quit_list['port'] != 'NULL':
        quit_list['port'].close()
    if 'tcp_sock' in quit_list:
            quit_list['tcp_sock'].close()
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

def setR(unused_addr, nR):
    global R, iR
    if nR>maxBright:
        nR=maxBright
    iR=(iR+1)%datar
    R[iR]=nR

def setG(unused_addr, nG):
    global G, iG
    if nG>maxBright:
        nG=maxBright
    iG=(iG+1)%datar
    G[iG]=nG

def setB(unused_addr, nB):
    global B, iB
    if nB>maxBright:
        nB=maxBright
    iB=(iB+1)%datar
    B[iB]=nB

def setsR(unused_addr, nsR):
    global sR
    sR=nsR
    print(time.strftime('[%H:%M:%S]')+' Red averaging time: '+str(1000*sR/datar)+'ms.')

def setsG(unused_addr, nsG):
    global sG
    sG=nsG
    print(time.strftime('[%H:%M:%S]')+' Green averaging time: '+str(1000*sG/datar)+'ms.')

def setsB(unused_addr, nsB):
    global sB
    sB=nsB
    print(time.strftime('[%H:%M:%S]')+' Blue averaging time: '+str(1000*sB/datar)+'ms.')

def setmR(unused_addr, nmR):
    global mR
    mR=nmR
    if mR==1:
        global tiR
        tiR=0
        print(time.strftime('[%H:%M:%S]')+' Red in test mode.')
    elif mR==2:
        print(time.strftime('[%H:%M:%S]')+' Red in sequential test mode.')
    else:
        print(time.strftime('[%H:%M:%S]')+' Red in color mode.')

def setmG(unused_addr, nmG):
    global mG
    mG=nmG
    if mG==1:
        global tiG
        tiG=0
        print(time.strftime('[%H:%M:%S]')+' Green in test mode.')
    elif mG==2:
        print(time.strftime('[%H:%M:%S]')+' Green in sequential test mode.')
    else:
        print(time.strftime('[%H:%M:%S]')+' Green in color mode.')

def setmB(unused_addr, nmB):
    global mB
    mB=nmB
    if mB==1:
        global tiB
        tiB=0
        print(time.strftime('[%H:%M:%S]')+' Blue in test mode.')
    elif mB==2:
        print(time.strftime('[%H:%M:%S]')+' Blue in sequential test mode.')
    else:
        print(time.strftime('[%H:%M:%S]')+' Blue in color mode.')

def setwsR(unused_addr, nwsR):
    global wsR
    wsR=nwsR
    print(time.strftime('[%H:%M:%S]')+' Red wave delay: '+str(1/wsR)+'ms between jumps.')

def setwsG(unused_addr, nwsG):
    global wsG
    wsG=nwsG
    print(time.strftime('[%H:%M:%S]')+' Green wave delay: '+str(1/wsG)+'ms between jumps.')

def setwsB(unused_addr, nwsB):
    global wsB
    wsB=nwsB
    print(time.strftime('[%H:%M:%S]')+' Blue wave delay: '+str(1/wsB)+'ms betweenjumps .')

def setwoR(unused_addr, nwoR):
    global woR
    woR=nwoR
    if woR==0:
        print(time.strftime('[%H:%M:%S]')+' Red wavemode offlined.')
    if woR==1:
        print(time.strftime('[%H:%M:%S]')+' Red wavemode onlined.')

def setwoG(unused_addr, nwoG):
    global woG
    woG=nwoG
    if woG==0:
        print(time.strftime('[%H:%M:%S]')+' Green wavemode offlined.')
    if woG==1:
        print(time.strftime('[%H:%M:%S]')+' Green wavemode onlined.')

def setwoB(unused_addr, nwoB):
    global woB
    woB=nwoB
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
    time_waited=time.monotonic()-lW
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
            quit_list['tcp_sock']=tcp_sock
    if use_ard_int:
        for k in b_arr:
            while True:
                incm_b=port.read(1)
                if incm_b==struct.pack("!B",def_ret):
    #DEBUG                          print("waiting:"+str(port.inWaiting()))
                    port.write(bytearray(k))
                    break
    #                    else:
    #                        sys.stdout.write("DEBUG:"+incm_b)
    #                        print 1./(time.clock()-lW)
    #DEBUG                  port.write(bytearray(struct.pack("!BHBBB",i,p,r,g,b)))
    #           print 1./(time.clock()-lW)
    lW=time.monotonic()

def flash(color, port, e=None):
    for i in range(0, 3):
        if color == 1:
            write(pA, 0, rBrightR, rBrightG, rBrightB, port, tcp_sock)
        elif color == 2:
            write(pA, 0, bBrightR, bBrightG, bBrightB, port, tcp_sock)
        elif color == 3:
            write(pA, 0, gBrightR, gBrightG, gBrightB, port, tcp_sock)
        time.sleep(.5)
        write(pA, 0, 0, 0, 0, port, tcp_sock)
        time.sleep(.2)
    if e is not None:
        print(e)
        #exit(1)

def initccache(ccache, princ, keytab):
    ccache.init(princ)
    ccache.init_creds_keytab(keytab=keytab, principal=princ)

def getNagData(hl_params, auth_obj, sl_params, status_url, timeout, data_lst,
             rCount, bCount, gCount, port):
    try:
        # pull the hoststatus json
        hl = requests.get(status_url, params=hl_params, verify=False,
                          auth=auth_obj, timeout=timeout).json()
        # pull the servicestatus json
        sl = requests.get(status_url, params=sl_params, verify=False,
                          auth=auth_obj, timeout=timeout).json()
        for h in sorted(hl['data']['hostlist']):
            if (hl['data']['hostlist'][h]['status'] == 2 or
                hl['data']['hostlist'][h]['problem_has_been_acknowledged']
                is True):
                data_lst.append(1)
                rCount[0] = rCount[0] + 1
            else:
                data_lst.append(2)
                bCount[0] = bCount[0] + 1
            if h in sl['data']['servicelist']:
                for s in sorted(sl['data']['servicelist'][h]):
                    if (sl['data']['servicelist'][h][s]['status'] == 2 or
                            sl['data']['servicelist'][h][s]
                            ['problem_has_been_acknowledged'] is True):
                        data_lst.append(1)
                        rCount[0] = rCount[0] + 1
                    elif sl['data']['servicelist'][h][s]['status'] == 4:
                        data_lst.append(3)
                        gCount[0] = gCount[0] + 1
                    else:
                        data_lst.append(2)
                        bCount[0] = bCount[0] + 1
        data_lst.extend([0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
    except Exception as e:
        flash(3, port, e)

def getNagDataWithKrb(ccache, princ, keytab, hl_params, auth_obj, sl_params,
                   status_url, timeout, ccache_file, data_lst, rCount,
                   bCount, gCount):
    # init ticket
    initccache(ccache, princ, keytab)
    getNagData(hl_params, auth_obj, sl_params, status_url, timeout, data_lst,
             rCount, bCount, gCount)
    # remove the ccache
    os.remove(ccache_file)

def pushNagFrame(offset, tcp_sock, lastFrame, data_lst, rCount, bCount, gCount, port):
    if rCount[0] > numLights / 2:
        write(pAns, 0, rBrightR, rBrightG, rBrightB, port, tcp_sock)
        newFrame = [r] * numLights
    elif bCount[0] > numLights / 2:
        write(pAns, 0, bBrightR, bBrightG, bBrightB, port, tcp_sock)
        newFrame = [b] * numLights
    elif gCount[0] > numLights / 2:
        write(pAns, 0, gBrightR, gBrightG, gBrightB, port, tcp_sock)
        newFrame = [g] * numLights
    elif rCount[0] == 0 and bCount[0] == 0 and gCount[0] == 0:
        flash(3, port, time.strftime('[%H:%M:%S]') + ' No data available.')
        time.sleep(120.0)
        return
    else:
        newFrame = lastFrame
    data_lst_local = copy(data_lst)
    while len(data_lst_local) < numLights:
        data_lst_local = data_lst_local+data_lst_local
    lenData_lst = len(data_lst_local)
    data_lst_local = data_lst_local+data_lst_local
    for ledIndex, d in enumerate(data_lst_local[offset[0]:
                                 offset[0]+numLights - 2]):
        if d != newFrame[ledIndex]:
            if d == 1:
                write(nsns, ledIndex, rBrightR, rBrightG, rBrightB, port, tcp_sock)
                newFrame[ledIndex] = 1
            elif d == 2:
                write(nsns, ledIndex, bBrightR, bBrightG, bBrightB, port, tcp_sock)
                newFrame[ledIndex] = 2
            elif d == 3:
                write(nsns, ledIndex, gBrightR, gBrightG, gBrightB, port, tcp_sock)
                newFrame[ledIndex] = 3
            elif d == 0:
                write(nsns, ledIndex, 0, 0, 0, port, tcp_sock)
                newFrame[ledIndex] = 0
    d = data_lst_local[numLights - 1]
    if d == 1:
        write(ns, numLights - 1, rBrightR, rBrightG, rBrightB, port, tcp_sock)
        newFrame[numLights - 1] = 1
    elif d == 2:
        write(ns, numLights -1, bBrightR, bBrightG, bBrightB, port, tcp_sock)
        newFrame[numLights -1] = 2
    elif d == 3:
        write(ns, numLights - 1, gBrightR, gBrightG, gBrightB, port, tcp_sock)
        newFrame[numLights - 1] = 3
    elif d == 0:
        write(ns, numLights - 1, 0, 0, 0, port, tcp_sock)
        newFrame[numLights - 1] = 0
    offset[0] = (offset[0] + 1) % lenData_lst
    lastFrame = newFrame

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
    client = pythonosc.udp_client.UDPClient(socket.gethostbyname(remote_osc_server), remote_osc_port)
    return client

def freq_to_band(freq):
    if freq=='None':
        return None
    else:
        return int((2.*float(freq)*float(spectrum_bands)-(float(aud_sample_rate)/2.))/float(aud_sample_rate))
   #return int(float(freq)/(aud_sample_rate/spectrum_bands))+1

def playerbin_message(bus,message):
#    print(message.type)
#    if message.type == Gst.MessageType.STATE_CHANGED:
#        print(message.parse_state_changed())
#    if message.type == Gst.MessageType.STREAM_STATUS:
#        print(message.parse_stream_status())
    if message.type == Gst.MessageType.ELEMENT:
        struct = message.get_structure()
        if struct.get_name() == 'spectrum':
            matches = re.search(r'magnitude=\(float\){([^}]+)}', struct.to_string())
            m = [float(x) for x in matches.group(1).split(',')]
            for mute_freq in range(31,32):
                m[freq_to_band(mute_freq)] = -60.
            low  = max(m[freq_to_band(min_low_freq):freq_to_band(max_low_freq)])
            mid  = max(m[freq_to_band(min_mid_freq):freq_to_band(max_mid_freq)])
            high = max(m[freq_to_band(min_high_freq):freq_to_band(max_high_freq)])

            low_lin=10**((low+low_db_adj)/20.)
            mid_lin=10**((mid+mid_db_adj)/20.)
            high_lin=10**((high+high_db_adj)/20.)
            low_adj=(1./(1.+2.71828**((-low_lin+float(low_led_log_shift))*float(low_led_log_stretch))))*float(maxBright)+float(low_led_adj)
            mid_adj=(1./(1.+2.71828**((-mid_lin+float(mid_led_log_shift))*float(mid_led_log_stretch))))*float(maxBright)+float(mid_led_adj)
            high_adj=(1./(1.+2.71828**((-high_lin+float(high_led_log_shift))*float(high_led_log_stretch))))*float(maxBright)+float(high_led_adj)
#            low_adj=((low_lin**float(low_led_curv))*float(maxBright))+float(low_led_adj)
#            mid_adj=((mid_lin**float(mid_led_curv))*float(maxBright))+float(mid_led_adj)
#            high_adj=((high_lin**float(high_led_curv))*float(maxBright))+float(high_led_adj)

#            print("raw: %03.1f %03.1f %03.1f lin: %03.3f %03.3f %03.3f adj: %03.1f %03.1f %03.1f" % (low, mid, high, low_lin, mid_lin, high_lin, low_adj, mid_adj, high_adj))

#            print("%03.1f %03.1f %03.1f %-30s %-30s %30s" % (low_adj, mid_adj, high_adj,
#                                                            "x"*int(low_adj/10),
#                                                            " "*int((30-(mid_adj/10))/2)+"x"*int(mid_adj/10),
#                                                            "x"*int(high_adj/10),
#                                                            ))

######              sendOSC(osc.Message("/R", int(low_adj)))
######              sendOSC(osc.Message("/G", int(mid_adj)))
######              sendOSC(osc.Message("/B", int(high_adj)))

##              client.send(osc.Message("/R", int(low_adj)))
##              client.send(osc.Message("/G", int(mid_adj)))
##              client.send(osc.Message("/B", int(high_adj)))
            if use_local:
                setR('/R',max(0,low_adj))
                setG('/G',max(0,mid_adj))
                setB('/B',max(0,high_adj))
            else:
                bb = pythonosc.osc_bundle_builder.OscBundleBuilder(pythonosc.osc_bundle_builder.IMMEDIATELY)
                mb = pythonosc.osc_message_builder.OscMessageBuilder(address="/R")
                mb.add_arg(int(low_adj))
                bb.add_content(mb.build())
                mb = pythonosc.osc_message_builder.OscMessageBuilder(address="/G")
                mb.add_arg(int(mid_adj))
                bb.add_content(mb.build())
                mb = pythonosc.osc_message_builder.OscMessageBuilder(address="/B")
                mb.add_arg(int(high_adj))
                bb.add_content(mb.build())
                client.send(bb.build())
    #            client.send(OSC.OSCMessage("/R"+[int(low_adj)]))
    #            client.send(OSC.OSCMessage("/G"+[int(mid_adj)]))
    #            client.send(OSC.OSCMessage("/B"+[int(high_adj)]))

#DEBUG    else:
#DEBUG        print message
    return True

def start_gst():
    pipelinetxt = (sound_framework+' ! audioconvert ! audioresample ! '+
                   'audio/x-raw,rate='+str(aud_sample_rate)+',channels='+str(aud_chans)+',depth='+str(aud_depth)+' ! '+
                   'spectrum interval='+str(sample_interval)+' bands='+str(spectrum_bands)+' ! '+
                   'fakesink')

    pipeline = Gst.parse_launch(pipelinetxt)
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
    gi_thread=GLib.MainLoop()
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
