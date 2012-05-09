import hppm_colorkinetics_network as Network
from numpy import zeros
import random
import time
import subprocess
global pA, su, cwR, cwG, cwB, fps, slen, lShow, fade, lwR, lwG, lwB
global lR, lG, lB, rowR, rowG, rowB, arrR, arrG, arrB, arrP
global SOCK_PORT, dest, sockets, packets
subprocess.call(['route', 'add', '10.32.0.43', '10.32.0.43'])
subprocess.call(['route', 'add', '10.32.0.60', '10.32.0.60'])
SOCK_PORT=6038
dest = [('10.32.0.43', 1), ('10.32.0.43', 2), ('10.32.0.60', 1), ('10.32.0.60', 2)]
#override the sent pixel values send for wave mode set -1 to use sent values
pR=11
pG=25
pB=40
#override the sent fade value for wave mode set -1 to use sent value
ofade=2
pA=255
su=254
cwR=251
cwG=252
cwB=253
slen=50
fade=0
lwR=0
lwG=0
lwB=0
lR=0
lG=0
lB=0
rowR=0
rowG=0
rowB=0
arrR=zeros((slen,3),'ubyte')
arrG=zeros((slen,3),'ubyte')
arrB=zeros((slen,3),'ubyte')
arrP=zeros((slen,3),'ubyte')

def loop(p, r, g, b):
    if p==pA:
        solidColor(r,g,b)
        show()
    elif p==su:
        setupvars(r,g,b)
    elif p==cwR:
        colorwaveR(r,g,b)
        show()
    elif p==cwG:
        colorwaveG(r,g,b)
        show()
    elif p==cwB:
        colorwaveB(r,g,b)
        show()
    else:
        global arrP
        arrP[p][0]=r
        arrP[p][1]=g
        arrP[p][2]=b
        show()

def colorwaveR(r,g,b):
    global lR, lwR, arrR, arrP, rowR, pR
    if pR!=-1:
        b=pR
    lR=r
    if time.clock()-lwR>=g:
        lwR=time.clock()
        arrR[rowR][0]=lR
        arrR[rowR][1]=b
        arrR[rowR][2]=b
        rowR=(rowR+1)%slen
        for i in xrange(slen):
            arrP[i][0]=0
        for j in xrange(slen-1):
            i=(rowR+j)%slen
            if arrR[i][0]-fade > -1:
                arrR[i][0]=arrR[i][0]-fade
            elif arrR[i][0] != 0:
                arrR[i][0]=0
            if arrR[i][2]+1 < slen:
                arrR[i][2]=arrR[i][2]+1
                arrP[arrR[i][2]][0]=arrP[arrR[i][2]][0]+arrR[i][0]
            if arrR[i][1]-1 > -1:
                arrR[i][1]=arrR[i][1]-1
                arrP[arrR[i][1]][0]=arrP[arrR[i][1]][0]+arrR[i][0]
        arrP[b][0]=arrP[b][0]+lR
        show()            
    else:
        arrP[b][0]=lR
        arrP[b][1]=lG
        arrP[b][2]=lB
        show()

def colorwaveG(r,g,b):
    global lG, lwG, arrG, arrP, rowG, pG
    if pG!=-1:
        b=pG
    lG=r
    if time.clock()-lwG>=g:
        lwG=time.clock()
        arrG[rowG][0]=lG
        arrG[rowG][1]=b
        arrG[rowG][2]=b
        rowG=(rowG+1)%slen
        for i in xrange(slen):
            arrP[i][1]=0
        for j in xrange(slen-1):
            i=(rowG+j)%slen
            if arrG[i][0]-fade > -1:
                arrG[i][0]=arrG[i][0]-fade
            elif arrG[i][0] != 0:
                arrG[i][0]=0
            if arrG[i][2]+1 < slen:
                arrG[i][2]=arrG[i][2]+1
                arrP[arrG[i][2]][1]=arrP[arrG[i][2]][1]+arrG[i][0]
            if arrG[i][1]-1 > -1:
                arrG[i][1]=arrG[i][1]-1
                arrP[arrG[i][1]][1]=arrP[arrG[i][1]][1]+arrG[i][0]
        arrP[b][1]=arrP[b][1]+lG
        show()            
    else:
        arrP[b][0]=lR
        arrP[b][1]=lG
        arrP[b][2]=lB
        show()

def colorwaveB(r,g,b):
    global lB, lwB, arrB, arrP, rowB, pB
    if pB!=-1:
        b=pB
    lB=r
    if time.clock()-lwB>=g:
        lwB=time.clock()
        arrB[rowB][0]=lB
        arrB[rowB][1]=b
        arrB[rowB][2]=b
        rowB=(rowB+1)%slen
        for i in xrange(slen):
            arrP[i][2]=0
        for j in xrange(slen-1):
            i=(rowB+j)%slen
            if arrB[i][0]-fade > -1:
                arrB[i][0]=arrB[i][0]-fade
            elif arrB[i][0] != 0:
                arrB[i][0]=0
            if arrB[i][2]+1 < slen:
                arrB[i][2]=arrB[i][2]+1
                arrP[arrB[i][2]][2]=arrP[arrB[i][2]][2]+arrB[i][0]
            if arrB[i][1]-1 > -1:
                arrB[i][1]=arrB[i][1]-1
                arrP[arrB[i][1]][2]=arrP[arrB[i][1]][2]+arrB[i][0]
        arrP[b][2]=arrP[b][2]+lB
        show()            

    else:
        arrP[b][0]=lR
        arrP[b][1]=lG
        arrP[b][2]=lB
        show()

def solidColor(r,g,b):
    for i in xrange(slen):
        arrP[i][0]=r
        arrP[i][1]=g
        arrP[i][2]=b
            
def send():
    sockets={}
    packets={}
    for (ip, port) in dest:
        packets[(ip, port)]=arrP
        packet=packets[(ip, port)]
        sockets[ip]=Network.getConnectedSocket(ip, SOCK_PORT)
        sendPacket=Network.composePixelStripPacket(packet, port)
        try:
            sockets[ip].send(sendPacket, 0x00)
        except:
            print time.strftime('[%H:%M:%S]')+' ColorKinetcs pack send failed.'

def show():
    global lShow
    if fps==0:
        send()
    elif time.clock()-lShow>=1/fps:
        lShow=time.clock()
        send()
    else:
        show()

def setupvars(r,g,b):
    global fade, fps, ofade
    if ofade!=-1:
        fade=ofade
    else:
        fade=r
    fps=g
    solidColor(0,0,0)
    show()

def exit():
    subprocess.call(['route', 'delete', '10.32.0.43'])
    subprocess.call(['route', 'delete', '10.32.0.60'])
