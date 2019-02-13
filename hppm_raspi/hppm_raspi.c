// Import the neccessary libraries
// lpd8806led is from https://github.com/fishkingsin/elinux-lpd8806
#include <fcntl.h>
#include <stdlib.h>
#include <stdbool.h>
#include <sys/ioctl.h>
#include <netdb.h>
#include <linux/spi/spidev.h>
#include <string.h>
#include <unistd.h>
#include <time.h>
#include <sys/time.h>
#include <stdio.h>
#include <poll.h>
#include "cie1931.h"
void procInst();
void colorwaveR(uint8_t r, uint8_t g, uint16_t b, uint8_t p);
void colorwaveG(uint8_t r, uint8_t g, uint16_t b, uint8_t p);
void colorwaveB(uint8_t r, uint8_t g, uint16_t b, uint8_t p);
void solidColor(uint8_t r,uint8_t g,uint8_t b);
void show();
void setupvars(uint8_t r,uint8_t g,uint16_t b);
void setPixelColor(uint16_t p, uint8_t r, uint8_t g, uint8_t b);
void writearrCc(uint8_t a, uint16_t p, uint16_t v);
uint16_t readarrCc(uint8_t a, uint16_t p);
void writearrCi(uint8_t a, uint16_t p1, bool p2, uint16_t v);
uint16_t readarrCi(uint8_t a, uint16_t p1, bool p2);
void writearrP(uint16_t p1, uint8_t p2, uint8_t v);
void writearrP16(uint16_t p1, uint8_t p2, uint16_t v);
uint16_t readarrP(uint16_t p1, uint8_t p2);
void dis();
unsigned int millis (void);
static uint64_t epochMilli;
struct timespec thirdsec_time={0}, zero_time={0};

// Specify the pixel values used for various signals, must match python.
#define def_pA 255 //whole strip solid color
#define def_pAns 248 //whole strip solid color but no show
#define def_su 254 //set numLights, fps, protocol and maxBright, reserved
#define def_ns 250 //single pixel
#define def_nsns 249 //single pixel but no show
//start wave on color or
#define def_cwR 251
#define def_cwG 252
#define def_cwB 253
//return code to request next byre
#define def_ret 17
// DI (with the white line)  connects to pin 11 (or 51 if you have a Mega)
// CI connects to pin 13 (or 52 if you have a Mega)
#define def_spispd 8000000

#define def_pwr 12 // pin for controlling the power supply
uint8_t inst; //incoming instruction value
uint8_t ip8[2]; //incoming pixel values
uint16_t ip; //refactored pixel value
uint8_t ir; //incoming data values
uint8_t ig;
uint8_t ib;
uint8_t fps;
uint16_t slen;
uint16_t llen;
uint16_t alen;
uint32_t lShow;
bool chngBProp;
#define def_ledBright 255
#define def_ledBright16 2550
uint8_t sNum;
uint32_t lwR=0;
uint32_t lwG=0;
uint32_t lwB=0;
uint8_t lR=0;
uint8_t lG=0;
uint8_t lB=0;
uint16_t rowR=0;
uint16_t rowG=0;
uint16_t rowB=0;
typedef uint8_t arr8c1;
typedef uint16_t arr16c1;
typedef uint16_t arr16c2[2];
typedef uint16_t arr16c3[3];
arr16c1 *arrRc1;
arr16c1 *arrRc2;
arr16c2 *arrRi1;
arr16c2 *arrRi2;
arr16c1 *arrGc1;
arr16c1 *arrGc2;
arr16c2 *arrGi1;
arr16c2 *arrGi2;
arr16c1 *arrBc1;
arr16c1 *arrBc2;
arr16c2 *arrBi1;
arr16c2 *arrBi2;
arr16c3 *arrP1;
arr16c3 *arrP2;
arr8c1 *spi_buf;

void spi_send(arr8c1 *spi_msg, size_t *spi_msg_len);

// Defines to use names for choosing the arr to write/read to
#define def_arrRc 0
#define def_arrGc 1
#define def_arrBc 2
#define def_arrRi 0
#define def_arrGi 1
#define def_arrBi 2
// Set the number of bytes in an instruction
#define def_instlen 6
// Set to one less than def_instlen
#define def_instlenm1 5

int spifd;

void usage(char *progname) {
  printf("Usage: %s [-s]\n       -s keep lights on when there is no TCP client (otherwise lights turn off)\n",progname);
  fflush(stdout);
}

int main(int argc, char *argv[]) {
  // See if lights should stay on or go off
  // when there is no TCP incoming
  bool lights_off=1;
  arr8c1 *reset_buf;
  size_t reset_buf_len=198657;
  if(argc == 2){
    if(strcmp(argv[1],"-s") == 0 ){
      lights_off=0;
    } else {
      usage(argv[0]);
      exit(1);
    }
  } else if(argc > 2){
    usage(argv[0]);
    exit(1);
  } else {
    reset_buf=(arr8c1 *)malloc(reset_buf_len*sizeof(uint8_t));
    memset(reset_buf,128,198657);
    for (uint32_t i=0;i<2048;i++){
      reset_buf[i]=0;
    }
  }
  // Start the TCP/IP server
  struct sockaddr_in serv_addr, cli_addr;
  int srvTcpFd=socket(AF_INET, SOCK_STREAM, 0);
  const int reuse = 1;
  setsockopt(srvTcpFd,SOL_SOCKET,SO_REUSEADDR,(const char*)&reuse, sizeof(reuse));
  setsockopt(srvTcpFd,SOL_SOCKET,SO_REUSEPORT,(const char*)&reuse, sizeof(reuse));
  memset((char *) &serv_addr, 0,sizeof(serv_addr));
  serv_addr.sin_family=AF_INET;
  serv_addr.sin_addr.s_addr=INADDR_ANY;
  //set port
  serv_addr.sin_port=htons(10489);
  while(1) {
    int bind_status=bind(srvTcpFd, (struct sockaddr *) &serv_addr, sizeof(serv_addr));
    if (bind_status<0) {
      printf("Cannot bind server error %d, retrying...\n",bind_status);
      fflush(stdout);
    } else {
      break;
    }
  }
  listen(srvTcpFd,5);
  int clilen=sizeof(cli_addr);
  // Start the SPI connection
  spifd=open("/dev/spidev0.0",O_RDWR);
  ioctl(spifd,SPI_IOC_WR_MODE,SPI_MODE_0);
  ioctl(spifd,SPI_IOC_WR_BITS_PER_WORD,8);
  ioctl(spifd,SPI_IOC_WR_MAX_SPEED_HZ,def_spispd);
  lShow=millis();
  //Make some arrays so we can free them during setup
  arrRc1=(arr16c1 *)malloc(0);
  arrRc2=(arr16c1 *)malloc(0);
  arrRi1=(arr16c2 *)malloc(0);
  arrRi2=(arr16c2 *)malloc(0);
  arrGc1=(arr16c1 *)malloc(0);
  arrGc2=(arr16c1 *)malloc(0);
  arrGi1=(arr16c2 *)malloc(0);
  arrGi2=(arr16c2 *)malloc(0);
  arrBc1=(arr16c1 *)malloc(0);
  arrBc2=(arr16c1 *)malloc(0);
  arrBi1=(arr16c2 *)malloc(0);
  arrBi2=(arr16c2 *)malloc(0);
  arrP1=(arr16c3 *)malloc(0);
  arrP2=(arr16c3 *)malloc(0);
  spi_buf=(arr8c1 *)malloc(0);
  //set time
  struct timeval tv ;
  gettimeofday (&tv, NULL) ;
  epochMilli = (uint64_t)tv.tv_sec * (uint64_t)1000    + (uint64_t)(tv.tv_usec / 1000) ;
  thirdsec_time.tv_sec=0;
  thirdsec_time.tv_nsec=333000000;
  uint8_t tcp_buf[def_instlen];
  printf("Waiting for TCP Client...\n");
  fflush(stdout);
  //poll() setup
  struct pollfd watch_fd[1];
  watch_fd[0].fd=srvTcpFd;
  watch_fd[0].events=POLLIN;
  while(1){
    int sock_ready=poll(watch_fd,1,10000);
    if(sock_ready > 0){
      int tcpConFd=accept(srvTcpFd, (struct sockaddr *) &cli_addr, (socklen_t*) &clilen);
      printf("TCP Client Connected.\n");
      fflush(stdout);
      while(1){
        memset(tcp_buf,0,def_instlen);
        uint16_t bytes_read=read(tcpConFd,tcp_buf,def_instlen);
        inst=(uint8_t)tcp_buf[0];
        ip8[1]=(uint8_t)tcp_buf[1];
        ip8[0]=(uint8_t)tcp_buf[2];
        ip=*(uint16_t *)&ip8;
        ir=(uint8_t)tcp_buf[3];
        ig=(uint8_t)tcp_buf[4];
        ib=(uint8_t)tcp_buf[5];
        if (inst==0 || bytes_read!=def_instlen){
          break;
        }
        procInst();
      }
      printf("Closing TCP socket.\n");
      fflush(stdout);
      close(tcpConFd);
    } else {
      if(lights_off){
        //turn off lights
        spi_send(reset_buf,&reset_buf_len);
      }
    }
  }
}

void procInst(){
  if (inst==def_cwR){
    colorwaveR(ig,ir,ip,ib);
    show();
  } else if (inst==def_cwG){
    colorwaveG(ig,ir,ip,ib);
    show();
  } else if (inst==def_cwB){
    colorwaveB(ig,ir,ip,ib);
    show();
  } else if (inst==def_pA){
    solidColor(ir,ig,ib);
    show();
  } else if (inst==def_pAns){
    solidColor(ir,ig,ib);
  } else if (inst==def_ns){
    setPixelColor(ip,ir,ig,ib);
    show();
  } else if (inst==def_nsns){
    setPixelColor(ip,ir,ig,ib);
  } else if (inst==def_su){
    setupvars(ig,ir,ip);
  } else {
    solidColor(def_ledBright,0,0);
    show();
    nanosleep(&thirdsec_time,&zero_time);
    solidColor(0,def_ledBright,0);
    show();
    nanosleep(&thirdsec_time,&zero_time);
    solidColor(0,0,def_ledBright);
    show();
    nanosleep(&thirdsec_time,&zero_time);
  }
}

void colorwaveR(uint8_t light_level, uint8_t wave_speed, uint16_t pixel_position, uint8_t fade){
  lR=light_level;
  if (millis()-lwR>=wave_speed){
    lwR=millis();
    writearrCc(def_arrRc, rowR, lR*10);
    writearrCi(def_arrRi, rowR, 0, pixel_position);
    writearrCi(def_arrRi, rowR, 1, pixel_position);
    if (alen == 65535){
      rowR=(rowR+1);
    } else {
      rowR=(rowR+1)%(alen+1);
    }
    for (uint16_t i=0; i <= slen; i++){
      writearrP16(i, 0, 0);
    }
    uint16_t i;
    uint16_t cur_light_lev;
    uint16_t nex_light_lev;
    uint16_t cur_pixel_pos;
    uint16_t nex_pixel_pos;
    for (uint16_t j=0; j < alen; j++){
      if (alen == 65535){
        i=(rowR+j);
      } else {
        i=(rowR+j)%(alen+1);
      }
      cur_light_lev=readarrCc(def_arrRc, i);
      if (fade < cur_light_lev){
        writearrCc(def_arrRc, i, cur_light_lev-fade);
      } else if (cur_light_lev != 0){
        writearrCc(def_arrRc, i, 0);
      }
      cur_pixel_pos=readarrCi(def_arrRi, i, 1);
      nex_pixel_pos=cur_pixel_pos+1;
      if (nex_pixel_pos <= slen && cur_pixel_pos != 65535 ){
        writearrCi(def_arrRi, i, 1, nex_pixel_pos);
        cur_light_lev=readarrCc(def_arrRi, i);
        nex_light_lev=readarrP(nex_pixel_pos, 0)+cur_light_lev;
        if (nex_light_lev > def_ledBright16 || nex_light_lev < cur_light_lev){
          writearrP16(nex_pixel_pos, 0, def_ledBright16);
        } else {
          writearrP16(nex_pixel_pos, 0, nex_light_lev);
        }
      } 
      cur_pixel_pos=readarrCi(def_arrRi, i, 0);
      nex_pixel_pos=cur_pixel_pos-1;
      if (nex_pixel_pos < cur_pixel_pos){
        writearrCi(def_arrRi, i, 0, nex_pixel_pos);
        cur_light_lev=readarrCc(def_arrRi, i);
        nex_light_lev=readarrP(nex_pixel_pos, 0)+cur_light_lev;
        if (nex_light_lev > def_ledBright16 || nex_light_lev < cur_light_lev){
          writearrP16(nex_pixel_pos, 0, def_ledBright16);
        } else {
          writearrP16(nex_pixel_pos, 0, nex_light_lev);
        }
      } 
    }
    cur_light_lev=readarrP(pixel_position, 0);
    nex_light_lev=cur_light_lev+lR*10;
    if (nex_light_lev > def_ledBright16 || nex_light_lev < cur_light_lev){
      writearrP16(pixel_position, 0, def_ledBright16);
    } else {
      writearrP16(pixel_position, 0, nex_light_lev);
    }
  } else {
    if (chngBProp == 1){
      setPixelColor(pixel_position,lR,lG,lB);
    }
  } 
}

void colorwaveG(uint8_t light_level, uint8_t wave_speed, uint16_t pixel_position, uint8_t fade){
  lG=light_level;
  if (millis()-lwG>=wave_speed){
    lwG=millis();
    writearrCc(def_arrGc, rowG, lG*10);
    writearrCi(def_arrGi, rowG, 0, pixel_position);
    writearrCi(def_arrGi, rowG, 1, pixel_position);
    if (alen == 65535){
      rowG=(rowG+1);
    } else {
      rowG=(rowG+1)%(alen+1);
    }
    for (uint16_t i=0; i <= slen; i++){
      writearrP16(i, 1, 0);
    }
    uint16_t i;
    uint16_t cur_light_lev;
    uint16_t nex_light_lev;
    uint16_t cur_pixel_pos;
    uint16_t nex_pixel_pos;
    for (uint16_t j=0; j < alen; j++){
      if (alen == 65535){
        i=(rowG+j);
      } else {
        i=(rowG+j)%(alen+1);
      }
      cur_light_lev=readarrCc(def_arrGc, i);
      if (fade < cur_light_lev){
        writearrCc(def_arrGc, i, cur_light_lev-fade);
      } else if (cur_light_lev != 0){
        writearrCc(def_arrGc, i, 0); 
      }
      cur_pixel_pos=readarrCi(def_arrGi, i, 1);
      nex_pixel_pos=cur_pixel_pos+1;
      if (nex_pixel_pos <= slen && cur_pixel_pos != 65535){
        writearrCi(def_arrGi, i, 1, nex_pixel_pos);
        cur_light_lev=readarrCc(def_arrGi, i);
        nex_light_lev=readarrP(nex_pixel_pos, 1)+cur_light_lev;
        if (nex_light_lev > def_ledBright16 || nex_light_lev < cur_light_lev){
          writearrP16(nex_pixel_pos, 1, def_ledBright16);
        } else {
          writearrP16(nex_pixel_pos, 1, nex_light_lev);
        }
      }
      cur_pixel_pos=readarrCi(def_arrGi, i, 0);
      nex_pixel_pos=cur_pixel_pos-1;
      if (nex_pixel_pos < cur_pixel_pos){
        writearrCi(def_arrGi, i, 0, nex_pixel_pos);
        cur_light_lev=readarrCc(def_arrGi, i);
        nex_light_lev=readarrP(nex_pixel_pos, 1)+cur_light_lev;
        if (nex_light_lev > def_ledBright16 || nex_light_lev < cur_light_lev){
          writearrP16(nex_pixel_pos, 1, def_ledBright16);
        } else {
          writearrP16(nex_pixel_pos, 1, nex_light_lev);
        }
      }
    }
    cur_light_lev=readarrP(pixel_position, 1);
    nex_light_lev=cur_light_lev+lG*10;
    if (nex_light_lev > def_ledBright16 || nex_light_lev < cur_light_lev){
      writearrP16(pixel_position, 1, def_ledBright16);
    } else {
      writearrP16(pixel_position, 1, nex_light_lev);
    }
  } else {
    if (chngBProp == 1){
      setPixelColor(pixel_position,lR,lG,lB);
    }
  } 
}

void colorwaveB(uint8_t light_level, uint8_t wave_speed, uint16_t pixel_position, uint8_t fade){
  lB=light_level;
  if (millis()-lwB>=wave_speed){
    lwB=millis();
    writearrCc(def_arrBc, rowB, lB*10);
    writearrCi(def_arrBi, rowB, 0, pixel_position);
    writearrCi(def_arrBi, rowB, 1, pixel_position);
    if (alen == 65535){
      rowB=(rowB+1);
    } else {
      rowB=(rowB+1)%(alen+1);
    }
    for (uint16_t i=0; i <= slen; i++){
      writearrP16(i, 2, 0);
    }
    uint16_t i;
    uint16_t cur_light_lev;
    uint16_t nex_light_lev;
    uint16_t cur_pixel_pos;
    uint16_t nex_pixel_pos;
    for (uint16_t j=0; j < alen; j++){
      if (alen == 65535){
        i=(rowB+j);
      } else {
        i=(rowB+j)%(alen+1);
      }
      cur_light_lev=readarrCc(def_arrBc, i);
      if (fade < cur_light_lev){
        writearrCc(def_arrBc, i, cur_light_lev-fade);
      } else if (cur_light_lev != 0){
        writearrCc(def_arrBc, i, 0);
      }
      cur_pixel_pos=readarrCi(def_arrBi, i, 1);
      nex_pixel_pos=cur_pixel_pos+1;
      if (nex_pixel_pos <= slen && cur_pixel_pos != 65535){
        writearrCi(def_arrBi, i, 1, nex_pixel_pos);
        cur_light_lev=readarrCc(def_arrBi, i);
        nex_light_lev=readarrP(nex_pixel_pos, 2)+cur_light_lev;
        if (nex_light_lev > def_ledBright16 || nex_light_lev < cur_light_lev){
          writearrP16(nex_pixel_pos, 2, def_ledBright16);
        } else {
          writearrP16(nex_pixel_pos, 2, nex_light_lev);
        }
      } 
      cur_pixel_pos=readarrCi(def_arrBi, i, 0);
      nex_pixel_pos=cur_pixel_pos-1;
      if (nex_pixel_pos < cur_pixel_pos){
        writearrCi(def_arrBi, i, 0, nex_pixel_pos);
        cur_light_lev=readarrCc(def_arrBi, i);
        nex_light_lev=readarrP(nex_pixel_pos, 2)+cur_light_lev;
        if (nex_light_lev > def_ledBright16 || nex_light_lev < cur_light_lev){
          writearrP16(nex_pixel_pos, 2, def_ledBright16);
        } else {
          writearrP16(nex_pixel_pos, 2, nex_light_lev);
        }
      } 
    }
    cur_light_lev=readarrP(pixel_position, 2);
    nex_light_lev=cur_light_lev+lB*10;
    if (nex_light_lev > def_ledBright16 || nex_light_lev < cur_light_lev){
      writearrP16(pixel_position, 2, def_ledBright16);
    } else {
      writearrP16(pixel_position, 2, nex_light_lev);
    }
  } else {
    if (chngBProp == 1){
      setPixelColor(pixel_position,lR,lG,lB);
    }
  } 
}

void solidColor(uint8_t r,uint8_t g,uint8_t b){
  for (uint16_t i=0; i <= slen; i++) {
      setPixelColor(i,r,g,b);
  }
}

void show(){
  if (fps==0) {
    dis();
  } else if (millis()-lShow>=1/fps){
    lShow=millis();
    dis();
  } else {
    show();
  }
}

void setupvars(uint8_t r,uint8_t g,uint16_t b){
  printf("Setting up.\n");
  fflush(stdout);
  //Free old arrays
  free(arrRc1);
  free(arrRc2);
  free(arrRi1);
  free(arrRi2);
  free(arrGc1);
  free(arrGc2);
  free(arrGi1);
  free(arrGi2);
  free(arrBc1);
  free(arrBc2);
  free(arrBi1);
  free(arrBi2);
  free(arrP1);
  free(arrP2);
  free(spi_buf);
  fps=g;
  slen=b;
  sNum=r;
  // set how to handle signal coming in faster than wave speed
  // 1 display it on the imcoming pixel
  // 0 ignore it
  if (r==0 || r==2 || r==4){
    chngBProp=0;
  } else {
    chngBProp=1;
  }
  //Make new pixel array
  if (slen+1<=32768) {
    arrP1=(arr16c3 *)malloc((slen+1) * 3 * sizeof(uint16_t));
    arrP2=(arr16c3 *)malloc(0);
  } else {
    arrP1=(arr16c3 *)malloc(32768 * 3 * sizeof(uint16_t));
    arrP2=(arr16c3 *)malloc(((slen+1)-32768) * 3 * sizeof(uint16_t));
  }
  size_t num_reset_bytes=slen/32+2;
  spi_buf=(arr8c1 *)malloc(((slen+1)*3+num_reset_bytes) * sizeof(uint8_t));
  //Calculate memory left for color wave arrays
    alen=(slen+1)*3;
//  alen=(freeRam()/15)-10;
//These are useful for debugging
//  ser_l.print("slen:");
//  ser_l.println(slen);
//  ser_l.print("alen:");
//  ser_l.println(alen);
//  ser_l.print("freemem:");
//  ser_l.println(freeRam());
//  alen=20;
  //Create arrays
  if (alen+1<=32768) {
    arrRc1=(arr16c1 *)malloc((alen+1) * sizeof(uint16_t));
    arrRi1=(arr16c2 *)malloc((alen+1) * 2 * sizeof(uint16_t));
    arrGc1=(arr16c1 *)malloc((alen+1) * sizeof(uint16_t));
    arrGi1=(arr16c2 *)malloc((alen+1) * 2 * sizeof(uint16_t));
    arrBc1=(arr16c1 *)malloc((alen+1) * sizeof(uint16_t));
    arrBi1=(arr16c2 *)malloc((alen+1) * 2 * sizeof(uint16_t));
    arrRc2=(arr16c1 *)malloc(0);
    arrRi2=(arr16c2 *)malloc(0);
    arrGc2=(arr16c1 *)malloc(0);
    arrGi2=(arr16c2 *)malloc(0);
    arrBc2=(arr16c1 *)malloc(0);
    arrBi2=(arr16c2 *)malloc(0);
  } else {
    arrRc1=(arr16c1 *)malloc(32768 * sizeof(uint16_t));
    arrRi1=(arr16c2 *)malloc(32768 * 2 * sizeof(uint16_t));
    arrGc1=(arr16c1 *)malloc(32768 * sizeof(uint16_t));
    arrGi1=(arr16c2 *)malloc(32768 * 2 * sizeof(uint16_t));
    arrBc1=(arr16c1 *)malloc(32768 * sizeof(uint16_t));
    arrBi1=(arr16c2 *)malloc(32768 * 2 * sizeof(uint16_t));
    arrRc2=(arr16c1 *)malloc(((alen+1)-32768) * sizeof(uint16_t));
    arrRi2=(arr16c2 *)malloc(((alen+1)-32768) * 2 * sizeof(uint16_t));
    arrGc2=(arr16c1 *)malloc(((alen+1)-32768) * sizeof(uint16_t));
    arrGi2=(arr16c2 *)malloc(((alen+1)-32768) * 2 * sizeof(uint16_t));
    arrBc2=(arr16c1 *)malloc(((alen+1)-32768) * sizeof(uint16_t));;
    arrBi2=(arr16c2 *)malloc(((alen+1)-32768) * 2 * sizeof(uint16_t));
  }
  //Zero the arrays
  for (uint16_t i=0; i <= alen; i++){
    writearrCc(def_arrRc, i, 0);
    writearrCc(def_arrGc, i, 0);
    writearrCc(def_arrBc, i, 0);
    for (uint8_t j=0; j < 2; j++){
      writearrCi(def_arrRi, i, j, 0);
      writearrCi(def_arrGi, i, j, 0);
      writearrCi(def_arrBi, i, j, 0);
    }
  }
  solidColor(0,0,0);
  show();
  printf("Running.\n");
  fflush(stdout);
}

void setPixelColor(uint16_t p, uint8_t r, uint8_t g, uint8_t b){
  writearrP(p, 0, r);
  writearrP(p, 1, g);
  writearrP(p, 2, b);
}

void writearrCc(uint8_t a, uint16_t p, uint16_t v){
  if (p<32768) {
    switch (a) {
      case 0:
        arrRc1[p]=v;
        break;
      case 1:
        arrGc1[p]=v;
        break;
      case 2:
        arrBc1[p]=v;
        break;
    }
  } else {
    switch (a) {
      case 0:
        arrRc2[p-32768]=v;
        break;
      case 1:
        arrGc2[p-32768]=v;
        break;
      case 2:
        arrBc2[p-32768]=v;
        break;
    }
  }
}

uint16_t readarrCc(uint8_t a, uint16_t p){
  if (p<32768) {
    switch (a) {
      case 0:
        return arrRc1[p];
        break;
      case 1:
        return arrGc1[p];
        break;
      case 2:
        return arrBc1[p];
        break;
    }
  } else {
    switch (a) {
      case 0:
        return arrRc2[p-32768];
        break;
      case 1:
        return arrGc2[p-32768];
        break;
      case 2:
        return arrBc2[p-32768];
        break;
    }
  }
}

void writearrCi(uint8_t a, uint16_t p1, bool p2, uint16_t v){
  if (p1<32768) {
    switch (a) {
      case 0:
        arrRi1[p1][p2]=v;
        break;
      case 1:
        arrGi1[p1][p2]=v;
        break;
      case 2:
        arrBi1[p1][p2]=v;
        break;
    }
  } else {
    switch (a) {
      case 0:
        arrRi2[p1-32768][p2]=v;
        break;
      case 1:
        arrGi2[p1-32768][p2]=v;
        break;
      case 2:
        arrBi2[p1-32768][p2]=v;
        break;
    }
  }
}

uint16_t readarrCi(uint8_t a, uint16_t p1, bool p2){
  if (p1<32768) {
    switch (a) {
      case 0:
        return arrRi1[p1][p2];
        break;
      case 1:
        return arrGi1[p1][p2];
        break;
      case 2:
        return arrBi1[p1][p2];
        break;
    }
  } else {
    switch (a) {
      case 0:
        return arrRi2[p1-32768][p2];
        break;
      case 1:
        return arrGi2[p1-32768][p2];
        break;
      case 2:
        return arrBi2[p1-32768][p2];
        break;
    }
  }
}

void writearrP(uint16_t p1, uint8_t p2, uint8_t v){
  if (p1<32768) {
    arrP1[p1][p2]=v*10;
  } else {
    arrP2[p1-32768][p2]=v*10;
  }
}

void writearrP16(uint16_t p1, uint8_t p2, uint16_t v){
  if (p1<32768) {
    arrP1[p1][p2]=v;
  } else {
    arrP2[p1-32768][p2]=v;
  }
}

uint16_t readarrP(uint16_t p1, uint8_t p2){
  if (p1<32768) {
    return arrP1[p1][p2];
  } else {
    return arrP2[p1-32768][p2];
  }
}

////You can use this to debug just comment out the real dis
//void dis(){
//  for (uint16_t i=0; i <= slen; i++){
//    ser_l.print(readarrP(i, 0),DEC);
//    ser_l.print("-");
//    ser_l.print(readarrP(i, 1),DEC);
//    ser_l.print("-");
//    ser_l.print(readarrP(i, 2),DEC);
//    ser_l.print("-");
//  }
//  ser_l.println(slen);
//}

void dis(){
  size_t spi_buf_len=(slen+1)*3+(slen/32+2);
  memset(spi_buf,0,spi_buf_len);
  if (sNum==0 || sNum==1){
    for (uint16_t i=0; i <= slen; i++){
      spi_buf[(slen/32+2)+i*3]=cie_127[readarrP(i, 1)] | 0x80;
      spi_buf[(slen/32+2)+i*3+1]=cie_127[readarrP(i, 0)] | 0x80;
      spi_buf[(slen/32+2)+i*3+2]=cie_127[readarrP(i, 2)] | 0x80;
//      printf("\n%u %u %u\n",readarrP(i, 1),readarrP(i, 0),readarrP(i, 2));
//      printf("%u %u %u\n\n",spi_buf[i*3],spi_buf[i*3+1],spi_buf[i*3+2]);
    }
  } else if (sNum==4 || sNum==5){
    for (uint16_t i=0; i <= slen; i++){
      spi_buf[(slen/32+2)+i*3]=cie_127[readarrP(i, 2)] | 0x80;
      spi_buf[(slen/32+2)+i*3+1]=cie_127[readarrP(i, 0)] | 0x80;
      spi_buf[(slen/32+2)+i*3+2]=cie_127[readarrP(i, 1)] | 0x80;
//      printf("\n%u %u %u\n",readarrP(i, 1),readarrP(i, 0),readarrP(i, 2));
//      printf("%u %u %u\n\n",spi_buf[i*3],spi_buf[i*3+1],spi_buf[i*3+2]);
    }
  }
//  for (uint16_t i=0; i <=num_reset_bits; i++){
//    spi_buf[(slen+1)*3+slen/32+i]=0x00;
//  }
//
//  size_t size,attempt = (size_t)((slen+1)*3);
//  ssize_t result;
//  void *buf=const void *spi_buf;
//  while(size>0) {
//    result=write(spifd,buf,attempt);
//    buf+=result;
//    size-=result;
//    if(attempt>size) attempt=size;
//    printf("left:%o sent:%o ",size,result);
//  }
//  printf("all sent\n");
//  ssize_t num_written=write(spifd,spi_buf,(slen+1)*3);
//  printf("%u ",num_written);
//  fflush(stdout);
//printf("%u %u %u\n",spi_buf[13],spi_buf[14],spi_buf[15]);
  spi_send(spi_buf, &spi_buf_len);
//  printf("wrote:%u",ret);
//  fflush(stdout);
}

void spi_send(arr8c1 *spi_msg, size_t *spi_msg_len)
{
  const uint16_t bytes_at_once = 4096;
  uint16_t full_buffers = *spi_msg_len / bytes_at_once;
  uint16_t last_buffer_len = *spi_msg_len % bytes_at_once;
  for(size_t i=0;i<full_buffers;i++) {
    struct spi_ioc_transfer tr={
      .tx_buf=(unsigned long)(spi_msg+i*bytes_at_once),
      .len=bytes_at_once,
      .speed_hz=def_spispd,
    };
    ioctl(spifd,SPI_IOC_MESSAGE(1),&tr);
  }
  struct spi_ioc_transfer tr={
    .tx_buf=(unsigned long)(spi_msg+full_buffers*bytes_at_once),
    .len=last_buffer_len,
    .speed_hz=def_spispd,
  };
  ioctl(spifd,SPI_IOC_MESSAGE(1),&tr);
}

unsigned int millis (void)
{
  struct timeval tv ;
  uint64_t now ;

  gettimeofday (&tv, NULL) ;
  now  = (uint64_t)tv.tv_sec * (uint64_t)1000 + (uint64_t)(tv.tv_usec / 1000) ;

  return (uint32_t)(now - epochMilli) ;
}

void error(char *msg) {
  perror(msg);
}
