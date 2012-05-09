// Import the neccessary libraries, SPI is included with Arduino and
// LPD8806 comes from Adafruit (https://github.com/adafruit/LPD8806).
#include <LPD8806.h>
#include <SPI.h>

// Specify the pixel values used for various signals, must match python.
int pA=255; //whole strip solid color
int su=254; //set fade, fps, numLights
//start wave on color origin
int cwR=251;
int cwG=252;
int cwB=253;
// DI (with the white line)  connects to pin 11 (or 51 if you have a Mega)
// CI connects to pin 13 (or 52 if you have a Mega)
LPD8806 strip = LPD8806();

int pwr=12; // pin for controlling the power supply
uint16_t p; //incoming pixel value
uint8_t r; //incoming data values
uint8_t g;
uint8_t b;
int fps;
int slen;
long lShow;
int fade=0;
long lwR=0;
long lwG=0;
long lwB=0;
int lR=0;
int lG=0;
int lB=0;
int rowR=0;
int rowG=0;
int rowB=0;
int arrR[64][3];
int arrG[64][3];
int arrB[64][3];
int arrP[64][3];

void setup() {
  // Start the serial connection
  Serial.begin(115200);
  // Turn the power supply on
  pinMode(pwr,OUTPUT);
  digitalWrite(pwr,LOW);
  // Start up the LED stripline
  strip.begin();
  lShow=millis();
}

void loop(){
  while (Serial.available()>=4){
    p=Serial.read();
    r=Serial.read();
    g=Serial.read();
    b=Serial.read();
    if (p==pA){
      solidColor(r,g,b);
      show();
    } else if (p==su){
      setupvars(r,g,b);
    } else if (p==cwR){
      colorwaveR(r,g,b);
      show();
    } else if (p==cwG){
      colorwaveG(r,g,b);
      show();
    } else if (p==cwB){
      colorwaveB(r,g,b);
      show();
    } else{
      strip.setPixelColor(p,r,g,b);
      show();
    }
  }
}

void colorwaveR(uint8_t r, uint8_t g, uint8_t b){
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
    for (int i=0; i < slen; i++){
      strip.setPixelColor(i,arrP[i][0],arrP[i][1],arrP[i][2]);
    }
  } else {
    strip.setPixelColor(b,lR,lG,lB);
  } 
}

void colorwaveG(uint8_t r, uint8_t g, uint8_t b){
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
    for (int i=0; i < slen; i++){
      strip.setPixelColor(i,arrP[i][0],arrP[i][1],arrP[i][2]);
    }
  } else {
    strip.setPixelColor(b,lR,lG,lB);
  } 
}

void colorwaveB(uint8_t r, uint8_t g, uint8_t b){
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
    for (int i=0; i < slen; i++){
      strip.setPixelColor(i,arrP[i][0],arrP[i][1],arrP[i][2]);
    }
  } else {
    strip.setPixelColor(b,lR,lG,lB);
  } 
}

void solidColor(uint8_t r,uint8_t g,uint8_t b){
  for (int i=0; i < slen; i++) {
      strip.setPixelColor(i,r,g,b);
  }
}

void show(){
  if (fps==0) {
    strip.show();
  } else if (millis()-lShow>=1/fps){
    lShow=millis();
    strip.show();
  } else {
    show();
  }
}

void setupvars(uint8_t r,uint8_t g,uint8_t b){
  fade=r;
  fps=g;
  slen=b;
  strip.updateLength(slen);
  for (int i=0; i < 66; i++){
    for (int j=0; j < 3; j++){
      arrR[i][j]=0;
      arrG[i][j]=0;
      arrB[i][j]=0;
      arrP[i][j]=0;
    }
  }
  solidColor(0,0,0);
  show();
}
