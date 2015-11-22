// Import the neccessary libraries, SPI is included with Arduino
#include <SPI.h>
// NeoHWSerial is optional (uncomment to use) and available from 
// https://github.com/SlashDevin/NeoHWSerial/tree/master/1.6.5r2
// without it you get 31i/s (instructions per sec) on Mega2560
//#include <NeoHWSerial.h>
// If you are using NeoHWSerial there are three modes, define one of them
//#define S_FAS // (200i/s on Mega2560) quickest but can drop instructions
//#define S_REL // (41i/s on Mega2560) carries out every instruction
//#define S_LOW // This version doesn't work and I'm not sure why

// Specify the pixel values used for various signals, must match python.
#define def_pA 255 //whole strip solid color
#define def_su 254 //set numLights, fps, protocol and maxBright, reserved
#define def_ns 250 //single pixel
//start wave on color origin
#define def_cwR 251
#define def_cwG 252
#define def_cwB 253
//return code to request next byre
#define def_ret 17
// DI (with the white line)  connects to pin 11 (or 51 if you have a Mega)
// CI connects to pin 13 (or 52 if you have a Mega)

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
uint8_t ledBright;
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
typedef uint16_t arr16c2[2];
typedef uint8_t arr8c3[3];
arr8c1 *arrRc1;
arr8c1 *arrRc2;
arr16c2 *arrRi1;
arr16c2 *arrRi2;
arr8c1 *arrGc1;
arr8c1 *arrGc2;
arr16c2 *arrGi1;
arr16c2 *arrGi2;
arr8c1 *arrBc1;
arr8c1 *arrBc2;
arr16c2 *arrBi1;
arr16c2 *arrBi2;
arr8c3 *arrP1;
arr8c3 *arrP2;
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

void setup() {
// Pick the serial library to use
#ifdef NeoHWSerial_h
#define ser_l NeoSerial
  // Register the interrupt function
  ser_l.attachInterrupt(procSer);
#else
#define ser_l Serial
#endif
  // Start the serial connection
  ser_l.begin(115200);
  // Turn the power supply on
  pinMode(def_pwr,OUTPUT);
  digitalWrite(def_pwr,LOW);
  // Start the SPI connection
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  lShow=millis();
  //Make some arrays so we can free them during setup
  arrRc1=(arr8c1 *)malloc(0);
  arrRc2=(arr8c1 *)malloc(0);
  arrRi1=(arr16c2 *)malloc(0);
  arrRi2=(arr16c2 *)malloc(0);
  arrGc1=(arr8c1 *)malloc(0);
  arrGc2=(arr8c1 *)malloc(0);
  arrGi1=(arr16c2 *)malloc(0);
  arrGi2=(arr16c2 *)malloc(0);
  arrBc1=(arr8c1 *)malloc(0);
  arrBc2=(arr8c1 *)malloc(0);
  arrBi1=(arr16c2 *)malloc(0);
  arrBi2=(arr16c2 *)malloc(0);
  arrP1=(arr8c3 *)malloc(0);
  arrP2=(arr8c3 *)malloc(0);
  ser_l.write(def_ret);
}

#ifdef NeoHWSerial_h
#ifdef S_REL
// This version carries out every instruction
uint8_t serialInd=0;
uint8_t serialInst[def_instlen];

void procSer(uint8_t i_b) {
  serialInst[serialInd]=i_b;
  if (serialInd==def_instlenm1){
    inst=serialInst[0];
    ip8[1]=serialInst[1];
    ip8[0]=serialInst[2];
    ip=*(uint16_t *)&ip8;
    ir=serialInst[3];
    ig=serialInst[4];
    ib=serialInst[5];
    procInst();
  }
  serialInd=(serialInd+1)%def_instlen;
  ser_l.write(def_ret);
}

void loop() {
}
#endif

#ifdef S_LOW
// This version doesn't work and I'm not sure why
uint8_t serialInd=0;

void procSer(uint8_t i_b) {
  switch(serialInd) {
    case 0:
      inst=i_b;
      break;
    case 1:
      ip8[1]=i_b;
      break;
    case 2:
      ip8[2]=i_b;
      ip=*(uint16_t *)&ip8;
      break;
    case 3:
      ir=i_b;
      break;
    case 4:
      ig=i_b;
      break;
    case 5:
      ib=i_b;
      break;
  }
  serialInd=(serialInd+1)%def_instlen;
  ser_l.write(def_ret);
}

void loop(){
  if (serialInd==def_instlenm1){
    procInst();
  }
}
#endif

// This version is the quickest but can drop instructions
#ifdef S_FAS
uint8_t serialInd=0;
uint8_t serialInst[def_instlen];

void procSer(uint8_t i_b) {
  serialInst[serialInd]=i_b;
  serialInd=(serialInd+1)%def_instlen;
  ser_l.write(def_ret);
}

void loop(){
  if (serialInd==def_instlenm1){
    inst=serialInst[0];
    ip8[1]=serialInst[1];
    ip8[0]=serialInst[2];
    ip=*(uint16_t *)&ip8;
    ir=serialInst[3];
    ig=serialInst[4];
    ib=serialInst[5];
    procInst();
  }
}
#endif
#else
uint8_t l_ava=0;
uint8_t c_ava;

void loop(){
  c_ava=ser_l.available();
  if (c_ava>l_ava){
    l_ava=c_ava;
    ser_l.write(def_ret);
  }
  while (l_ava>=def_instlen){
    inst=ser_l.read();
    ip8[1]=ser_l.read();
    ip8[0]=ser_l.read();
    ip=*(uint16_t *)&ip8;
    ir=ser_l.read();
    ig=ser_l.read();
    ib=ser_l.read();
    l_ava =l_ava-def_instlen;
    procInst();
  }
}
#endif

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
  } else if (inst==def_ns){
    setPixelColor(ip,ir,ig,ib);
    show();
  } else if (inst==def_su){
    setupvars(ig,ir,ip);
  } else {
    solidColor(ledBright,0,0);
    show();
    delay(333);
    solidColor(0,ledBright,0);
    show();
    delay(333);
    solidColor(0,0,ledBright);
    show();
    delay(333);
  }
}

void colorwaveR(uint8_t r, uint8_t g, uint16_t b, uint8_t p){
  lR=r;
  if (millis()-lwR>=g){
    lwR=millis();
    writearrCc(def_arrRc, rowR, lR);
    writearrCi(def_arrRi, rowR, 0, b);
    writearrCi(def_arrRi, rowR, 1, b);
    if (alen == 65535){
      rowR=(rowR+1);
    } else {
      rowR=(rowR+1)%(alen+1);
    }
    for (uint16_t i=0; i <= slen; i++){
      writearrP(i, 0, 0);
    }
    uint16_t i;
    uint8_t tmp1_8;
    uint8_t tmp2_8;
    for (uint16_t j=0; j < alen; j++){
      if (alen == 65535){
        i=(rowR+j);
      } else {
        i=(rowR+j)%(alen+1);
      }
      tmp1_8=readarrCc(def_arrRc, i);
      if (tmp1_8 > p){
        writearrCc(def_arrRc, i, tmp1_8-p);
      } else if (readarrCc(def_arrRc, i) != 0){
        writearrCc(def_arrRc, i, 0);
      }
      uint16_t tmp2_16=readarrCi(def_arrRi, i, 1);
      uint16_t tmp1_16=tmp2_16+1;
      if (tmp1_16 <= slen && tmp2_16 != 65535 ){
        writearrCi(def_arrRi, i, 1, tmp1_16);
        tmp2_8=readarrCc(def_arrRi, i);
        tmp1_8=readarrP(tmp1_16, 0)+tmp2_8;
        if (tmp1_8 > ledBright || tmp1_8 < tmp2_8){
          writearrP(tmp1_16, 0, ledBright);
        } else {
          writearrP(tmp1_16, 0, tmp1_8);
        }
      } 
      tmp2_16=readarrCi(def_arrRi, i, 0);
      tmp1_16=tmp2_16-1;
      if (tmp1_16 < tmp2_16){
        writearrCi(def_arrRi, i, 0, tmp1_16);
        tmp2_8=readarrCc(def_arrRi, i);
        tmp1_8=readarrP(tmp1_16, 0)+tmp2_8;
        if (tmp1_8 > ledBright || tmp1_8 < tmp2_8){
          writearrP(tmp1_16, 0, ledBright);
        } else {
          writearrP(tmp1_16, 0, tmp1_8);
        }
      } 
    }
    tmp2_8=readarrP(b, 0);
    tmp1_8=tmp2_8+lR;
    if (tmp1_8 > ledBright || tmp1_8 < tmp2_8){
      writearrP(b, 0, ledBright);
    } else {
      writearrP(b, 0, tmp1_8);
    }
  } else {
    if (chngBProp == 1){
      setPixelColor(b,lR,lG,lB);
    }
  } 
}

void colorwaveG(uint8_t r, uint8_t g, uint16_t b, uint8_t p){
  lG=r;
  if (millis()-lwG>=g){
    lwG=millis();
    writearrCc(def_arrGc, rowG, lG);
    writearrCi(def_arrGi, rowG, 0, b);
    writearrCi(def_arrGi, rowG, 1, b);
    if (alen == 65535){
      rowG=(rowG+1);
    } else {
      rowG=(rowG+1)%(alen+1);
    }
    for (uint16_t i=0; i <= slen; i++){
      writearrP(i, 1, 0);
    }
    uint16_t i;
    uint8_t tmp1_8;
    uint8_t tmp2_8;
    for (uint16_t j=0; j < alen; j++){
      if (alen == 65535){
        i=(rowG+j);
      } else {
        i=(rowG+j)%(alen+1);
      }
      tmp1_8=readarrCc(def_arrGc, i);
      if (tmp1_8 > p){
        writearrCc(def_arrGc, i, tmp1_8-p);
      } else if (readarrCc(def_arrGc, i) != 0){
        writearrCc(def_arrGc, i, 0); 
      }
      uint16_t tmp2_16=readarrCi(def_arrGi, i, 1);
      uint16_t tmp1_16=tmp2_16+1;
      if (tmp1_16 <= slen && tmp2_16 != 65535){
        writearrCi(def_arrGi, i, 1, tmp1_16);
        tmp2_8=readarrCc(def_arrGi, i);
        tmp1_8=readarrP(tmp1_16, 1)+tmp2_8;
        if (tmp1_8 > ledBright || tmp1_8 < tmp2_8){
          writearrP(tmp1_16, 1, ledBright);
        } else {
          writearrP(tmp1_16, 1, tmp1_8);
        }
      }
      tmp2_16=readarrCi(def_arrGi, i, 0);
      tmp1_16=tmp2_16-1;
      if (tmp1_16 < tmp2_16){
        writearrCi(def_arrGi, i, 0, tmp1_16);
        tmp2_8=readarrCc(def_arrGi, i);
        tmp1_8=readarrP(tmp1_16, 1)+tmp2_8;
        if (tmp1_8 > ledBright || tmp1_8 < tmp2_8){
          writearrP(tmp1_16, 1, ledBright);
        } else {
          writearrP(tmp1_16, 1, tmp1_8);
        }
      }
    }
    tmp2_8=readarrP(b, 1);
    tmp1_8=tmp2_8+lG;
    if (tmp1_8 > ledBright){
      writearrP(b, 1, ledBright || tmp1_8 < tmp2_8);
    } else {
      writearrP(b, 1, tmp1_8);
    }
  } else {
    if (chngBProp == 1){
      setPixelColor(b,lR,lG,lB);
    }
  } 
}

void colorwaveB(uint8_t r, uint8_t g, uint16_t b, uint8_t p){
  lB=r;
  if (millis()-lwB>=g){
    lwB=millis();
    writearrCc(def_arrBc, rowB, lB);
    writearrCi(def_arrBi, rowB, 0, b);
    writearrCi(def_arrBi, rowB, 1, b);
    if (alen == 65535){
      rowB=(rowB+1);
    } else {
      rowB=(rowB+1)%(alen+1);
    }
    for (uint16_t i=0; i <= slen; i++){
      writearrP(i, 2, 0);
    }
    uint16_t i;
    uint8_t tmp1_8;
    uint8_t tmp2_8;
    for (uint16_t j=0; j < alen; j++){
      if (alen == 65535){
        i=(rowB+j);
      } else {
        i=(rowB+j)%(alen+1);
      }
      tmp1_8=readarrCc(def_arrBc, i);
      if (tmp1_8 > p){
        writearrCc(def_arrBc, i, tmp1_8-p);
      } else if (readarrCc(def_arrBc, i) != 0){
        writearrCc(def_arrBc, i, 0);
      }
      uint16_t tmp2_16=readarrCi(def_arrBi, i, 1);
      uint16_t tmp1_16=tmp2_16+1;
      if (tmp1_16 <= slen && tmp2_16 != 65535){
        writearrCi(def_arrBi, i, 1, tmp1_16);
        tmp2_8=readarrCc(def_arrBi, i);
        tmp1_8=readarrP(tmp1_16, 2)+tmp2_8;
        if (tmp1_8 > ledBright || tmp1_8 < tmp2_8){
          writearrP(tmp1_16, 2, ledBright);
        } else {
          writearrP(tmp1_16, 2, tmp1_8);
        }
      } 
      tmp2_16=readarrCi(def_arrBi, i, 0);
      tmp1_16=tmp2_16-1;
      if (tmp1_16 < tmp2_16){
        writearrCi(def_arrBi, i, 0, tmp1_16);
        tmp2_8=readarrCc(def_arrBi, i);
        tmp1_8=readarrP(tmp1_16, 2)+tmp2_8;
        if (tmp1_8 > ledBright || tmp1_8 < tmp2_8){
          writearrP(tmp1_16, 2, ledBright);
        } else {
          writearrP(tmp1_16, 2, tmp1_8);
        }
      } 
    }
    tmp2_8=readarrP(b, 2);
    tmp1_8=tmp2_8+lB;
    if (tmp1_8 > ledBright || tmp1_8 < tmp2_8){
      writearrP(b, 2, ledBright);
    } else {
      writearrP(b, 2, tmp1_8);
    }
  } else {
    if (chngBProp == 1){
      setPixelColor(b,lR,lG,lB);
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
  fps=g;
  slen=b;
  // set how to handle signal coming in faster than wave speed
  // 1 display it on the imcoming pixel
  // 0 ignore it
  if (r==0 || r==2){
    chngBProp=0;
  } else {
    chngBProp=1;
  }
  // set the max pixel brightness
  if (r==2 || r==3){
    ledBright=255;
  } else {
    ledBright=127;
  }
  //Make new pixel array
  if (slen+1<=32768) {
    arrP1=(arr8c3 *)malloc((slen+1) * 3 * sizeof(uint8_t));
    arrP2=(arr8c3 *)malloc(0);
  } else {
    arrP1=(arr8c3 *)malloc(32768 * 3 * sizeof(uint8_t));
    arrP2=(arr8c3 *)malloc(((slen+1)-32768) * 3 * sizeof(uint8_t));
  }
  //Calculate memory left for color wave arrays
  alen=(freeRam()/15)-10;
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
    arrRc1=(arr8c1 *)malloc((alen+1) * sizeof(uint8_t));
    arrRi1=(arr16c2 *)malloc((alen+1) * 2 * sizeof(uint16_t));
    arrGc1=(arr8c1 *)malloc((alen+1) * sizeof(uint8_t));
    arrGi1=(arr16c2 *)malloc((alen+1) * 2 * sizeof(uint16_t));
    arrBc1=(arr8c1 *)malloc((alen+1) * sizeof(uint8_t));
    arrBi1=(arr16c2 *)malloc((alen+1) * 2 * sizeof(uint16_t));
    arrRc2=(arr8c1 *)malloc(0);
    arrRi2=(arr16c2 *)malloc(0);
    arrGc2=(arr8c1 *)malloc(0);
    arrGi2=(arr16c2 *)malloc(0);
    arrBc2=(arr8c1 *)malloc(0);
    arrBi2=(arr16c2 *)malloc(0);
  } else {
    arrRc1=(arr8c1 *)malloc(32768 * sizeof(uint8_t));
    arrRi1=(arr16c2 *)malloc(32768 * 2 * sizeof(uint16_t));
    arrGc1=(arr8c1 *)malloc(32768 * sizeof(uint8_t));
    arrGi1=(arr16c2 *)malloc(32768 * 2 * sizeof(uint16_t));
    arrBc1=(arr8c1 *)malloc(32768 * sizeof(uint8_t));
    arrBi1=(arr16c2 *)malloc(32768 * 2 * sizeof(uint16_t));
    arrRc2=(arr8c1 *)malloc(((alen+1)-32768) * sizeof(uint8_t));
    arrRi2=(arr16c2 *)malloc(((alen+1)-32768) * 2 * sizeof(uint16_t));
    arrGc2=(arr8c1 *)malloc(((alen+1)-32768) * sizeof(uint8_t));
    arrGi2=(arr16c2 *)malloc(((alen+1)-32768) * 2 * sizeof(uint16_t));
    arrBc2=(arr8c1 *)malloc(((alen+1)-32768) * sizeof(uint8_t));;
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
}

void setPixelColor(uint16_t p, uint8_t r, uint8_t g, uint8_t b){
  writearrP(p, 0, r);
  writearrP(p, 1, g);
  writearrP(p, 2, b);
}

void writearrCc(uint8_t a, uint16_t p, uint8_t v){
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

uint8_t readarrCc(uint8_t a, uint16_t p){
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
    arrP1[p1][p2]=v;
  } else {
    arrP2[p1-32768][p2]=v;
  }
}

uint8_t readarrP(uint16_t p1, uint8_t p2){
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
  //if ledBright is 127 we use the LPD8806 protocol
  if (ledBright==127) {
    for (uint16_t i=0; i <= slen; i++){
      SPDR = readarrP(i, 1) | 0x80;
      while(!(SPSR & (1<<SPIF)));
      SPDR = readarrP(i, 0) | 0x80;
      while(!(SPSR & (1<<SPIF)));
      SPDR = readarrP(i, 2) | 0x80;
      while(!(SPSR & (1<<SPIF)));
    }
    llen = ((slen + 64) / 64) *3;
    while(llen--) SPI.transfer(0);
//    delay(1);
  // if ledBright is anything else (can only be 255) we use WS2801 protocol
  } else {
      for (uint16_t i=0; i <= slen; i++){
      for (uint8_t j=0; j < 3; j++){
        SPDR = readarrP(i,j);
        while(!(SPSR & (1<<SPIF)));
      }
    }
//    delay(1);
  }
}

uint32_t freeRam () {
  extern uint32_t __heap_start, *__brkval; 
  uint32_t v; 
  return (uint32_t) &v - (__brkval == 0 ? (uint32_t) &__heap_start : (uint32_t) __brkval); 
}

