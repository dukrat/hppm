// Import the neccessary libraries, SPI is included with Arduino and
#include <SPI.h>

// Specify the pixel values used for various signals, must match python.
uint8_t pA=255; //whole strip solid color
uint8_t su=254; //set numLights, fps, fade, reserved
uint8_t ns=250; //single pixel
//start wave on color origin
uint8_t cwR=251;
uint8_t cwG=252;
uint8_t cwB=253;
// DI (with the white line)  connects to pin 11 (or 51 if you have a Mega)
// CI connects to pin 13 (or 52 if you have a Mega)

uint8_t pwr=12; // pin for controlling the power supply
uint8_t i; //incoming instruction value
uint8_t p8[2]; //incoming pixel values
uint16_t p; //refactored pixel value
uint8_t r; //incoming data values
uint8_t g;
uint8_t b;
uint8_t fps;
uint16_t slen;
uint32_t lShow;
uint8_t fade=0;
uint32_t lwR=0;
uint32_t lwG=0;
uint32_t lwB=0;
uint8_t lR=0;
uint8_t lG=0;
uint8_t lB=0;
uint16_t rowR=0;
uint16_t rowG=0;
uint16_t rowB=0;
uint16_t arrR[313][3];
uint16_t arrG[313][3];
uint16_t arrB[313][3];
uint16_t arrP[313][3];

void setup() {
  // Start the serial connection
  Serial.begin(115200);
  // Turn the power supply on
  pinMode(pwr,OUTPUT);
  digitalWrite(pwr,LOW);
  // Start the SPI connection
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  lShow=millis();
}

void loop(){
  while (Serial.available()>=6){
    i=Serial.read();
    p8[1]=Serial.read();
    p8[0]=Serial.read();
    p=*(uint16_t *)&p8;
    r=Serial.read();
    g=Serial.read();
    b=Serial.read();
    if (i==pA){
      solidColor(r,g,b);
      show();
    } else if (i==su){
      setupvars(g,r,p);
    } else if (i==cwR){
      colorwaveR(g,r,p);
      show();
    } else if (i==cwG){
      colorwaveG(g,r,p);
      show();
    } else if (i==cwB){
      colorwaveB(g,r,p);
      show();
    } else{
      setPixelColor(p,r,g,b);
      show();
    }
  }
}

void colorwaveR(uint8_t r, uint8_t g, uint16_t b){
  lR=r;
  if (millis()-lwR>=g){
    lwR=millis();
    arrR[rowR][0]=lR;
    arrR[rowR][1]=b;
    arrR[rowR][2]=b;
    rowR=(rowR+1)%slen;
    for (int i=0; i < slen; i++){
      arrP[i][0]=0;
    }
    for (int j=0; j < slen-1; j++){
      int i=(rowR+j)%slen;
      if (arrR[i][0]-fade > -1){
        arrR[i][0]=arrR[i][0]-fade;
      } else if (arrR[i][0] != 0){
        arrR[i][0]=0;
      }
      if (arrR[i][2]+1 < slen){
        arrR[i][2]=arrR[i][2]+1;
        arrP[arrR[i][2]][0]=arrP[arrR[i][2]][0]+arrR[i][0];
      } 
      if (arrR[i][1]-1 > -1){
        arrR[i][1]=arrR[i][1]-1;
        arrP[arrR[i][1]][0]=arrP[arrR[i][1]][0]+arrR[i][0];
      }
    }
    arrP[b][0]=arrP[b][0]+lR;
  } else {
    setPixelColor(b,lR,lG,lB);
  } 
}

void colorwaveG(uint8_t r, uint8_t g, uint16_t b){
  lG=r;
  if (millis()-lwG>=g){
    lwG=millis();
    arrG[rowG][0]=lG;
    arrG[rowG][1]=b;
    arrG[rowG][2]=b;
    rowG=(rowG+1)%slen;
    for (int i=0; i < slen; i++){
      arrP[i][1]=0;
    }
    for (int j=0; j < slen-1; j++){
      int i=(rowG+j)%slen;
      if (arrG[i][0]-fade > -1){
        arrG[i][0]=arrG[i][0]-fade;
      } else if (arrG[i][0] != 0){
        arrG[i][0]=0;
      }
      if (arrG[i][2]+1 < slen){
        arrG[i][2]=arrG[i][2]+1;
        arrP[arrG[i][2]][1]=arrP[arrG[i][2]][1]+arrG[i][0];
      } 
      if (arrG[i][1]-1 > -1){
        arrG[i][1]=arrG[i][1]-1;
        arrP[arrG[i][1]][1]=arrP[arrG[i][1]][1]+arrG[i][0];
      }
    }
    arrP[b][1]=arrP[b][1]+lG;
  } else {
    setPixelColor(b,lR,lG,lB);
  } 
}

void colorwaveB(uint8_t r, uint8_t g, uint16_t b){
  lB=r;
  if (millis()-lwB>=g){
    lwB=millis();
    arrB[rowB][0]=lB;
    arrB[rowB][1]=b;
    arrB[rowB][2]=b;
    rowB=(rowB+1)%slen;
    for (int i=0; i < slen; i++){
      arrP[i][2]=0;
    }
    for (int j=0; j < slen-1; j++){
      int i=(rowB+j)%slen;
      if (arrB[i][0]-fade > -1){
        arrB[i][0]=arrB[i][0]-fade;
      } else if (arrB[i][0] != 0){
        arrB[i][0]=0;
      }
      if (arrB[i][2]+1 < slen){
        arrB[i][2]=arrB[i][2]+1;
        arrP[arrB[i][2]][2]=arrP[arrB[i][2]][2]+arrB[i][0];
      } 
      if (arrB[i][1]-1 > -1){
        arrB[i][1]=arrB[i][1]-1;
        arrP[arrB[i][1]][2]=arrP[arrB[i][1]][2]+arrB[i][0];
      }
    }
    arrP[b][2]=arrP[b][2]+lB;
  } else {
    setPixelColor(b,lR,lG,lB);
  } 
}

void solidColor(uint8_t r,uint8_t g,uint8_t b){
  for (int i=0; i < slen; i++) {
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
  fade=r;
  fps=g;
  slen=b;
  for (int i=0; i < slen; i++){
    for (int j=0; j < 3; j++){
      arrR[i][j]=0;
      arrG[i][j]=0;
      arrB[i][j]=0;
    }
  }
  solidColor(0,0,0);
  show();
}

void setPixelColor(uint16_t p, uint8_t r, uint8_t g, uint8_t b){
  arrP[p][0]=r;
  arrP[p][1]=g;
  arrP[p][2]=b;
}

void dis(){
  for (int i=0; i < slen; i++){
    for (int j=0; j < 3; j++){
      SPDR = arrP[i][j];
      while(!(SPSR & (1<<SPIF)));
    }
  }
  delay(1);
}
