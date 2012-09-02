// Import the neccessary libraries, SPI is included with Arduino and
#include <SPI.h>

// Set one minus the number of wavemode instructions kept in memory at a
// time and one minus the maximum number of lights that can be controlled
// you can play with these numbers as needed, if you set them equal
// the highest useable value for Mega (Atmega2560) is 312 and the
// highest useable value for Uno (Atmega328) is unknown but close to 64
#define const_wave_states_minus_one 312
#define const_num_lights_minus_one 312

// Specify the pixel values used for various signals, must match python.
#define const_pA 255 //whole strip solid color
#define const_su 254 //set numLights, fps, fade, reserved
#define const_ns 250 //single pixel
//start wave on color origin
#define const_cwR 251
#define const_cwG 252
#define const_cwB 253
// DI (with the white line)  connects to pin 11 (or 51 if you have a Mega)
// CI connects to pin 13 (or 52 if you have a Mega)

#define const_pwr 12 // pin for controlling the power supply
uint8_t inst; //incoming instruction value
uint8_t p8[2]; //incoming pixel values
uint16_t p; //refactored pixel value
uint8_t r; //incoming data values
uint8_t g;
uint8_t b;
uint8_t fps;
uint16_t slen;
uint16_t n;
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
uint16_t arrR[const_wave_states_minus_one+1][3];
uint16_t arrG[const_wave_states_minus_one+1][3];
uint16_t arrB[const_wave_states_minus_one+1][3];
uint16_t arrP[const_num_lights_minus_one+1][3];

void setup() {
  // Start the serial connection
  Serial.begin(115200);
  // Turn the power supply on
  pinMode(const_pwr,OUTPUT);
  digitalWrite(const_pwr,LOW);
  // Start the SPI connection
  SPI.begin();
  SPI.setBitOrder(MSBFIRST);
  SPI.setDataMode(SPI_MODE0);
  SPI.setClockDivider(SPI_CLOCK_DIV8);
  lShow=millis();
}

void loop(){
  while (Serial.available()>=6){
    inst=Serial.read();
    p8[1]=Serial.read();
    p8[0]=Serial.read();
    p=*(uint16_t *)&p8;
    r=Serial.read();
    g=Serial.read();
    b=Serial.read();
    if (inst==const_pA){
      solidColor(r,g,b);
      show();
    } else if (inst==const_su){
      setupvars(g,r,p);
    } else if (inst==const_cwR){
      colorwaveR(g,r,p);
      show();
    } else if (inst==const_cwG){
      colorwaveG(g,r,p);
      show();
    } else if (inst==const_cwB){
      colorwaveB(g,r,p);
      show();
    } else if (inst==const_ns){
      setPixelColor(p,r,g,b);
      show();
    } else {
      solidColor(255,0,0);
      delay(333);
      solidColor(0,255,0);
      delay(333);
      solidColor(0,0,255);
      delay(333);
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
    if (const_wave_states_minus_one == 65535){
      rowR=(rowR+1);
    } else {
      rowR=(rowR+1)%(const_wave_states_minus_one+1);
    }
    for (uint16_t i=0; i <= slen; i++){
      arrP[i][0]=0;
    }
    uint16_t i;
    for (uint16_t j=0; j < const_wave_states_minus_one; j++){
      if (const_wave_states_minus_one == 65535){
        i=(rowR+j);
      } else {
        i=(rowR+j)%(const_wave_states_minus_one+1);
      }
      if (arrR[i][0]-fade <= arrR[i][0]){
        arrR[i][0]=arrR[i][0]-fade;
      } else if (arrR[i][0] != 0){
        arrR[i][0]=0;
      }
      if (arrR[i][2]+1 <= slen && arrR[i][2]+1 > arrR[i][2]){
        arrR[i][2]=arrR[i][2]+1;
        arrP[arrR[i][2]][0]=arrP[arrR[i][2]][0]+arrR[i][0];
      } 
      if (arrR[i][1]-1 < arrR[i][1]){
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
    if (const_wave_states_minus_one == 65535){
      rowG=(rowG+1);
    } else {
      rowG=(rowG+1)%(const_wave_states_minus_one+1);
    }
    for (uint16_t i=0; i <= slen; i++){
      arrP[i][1]=0;
    }
    uint16_t i;
    for (uint16_t j=0; j < const_wave_states_minus_one; j++){
      if (const_wave_states_minus_one == 65535){
        i=(rowG+j);
      } else {
        i=(rowG+j)%(const_wave_states_minus_one+1);
      }
      if (arrG[i][0]-fade <= arrG[i][0]){
        arrG[i][0]=arrG[i][0]-fade;
      } else if (arrG[i][0] != 0){
        arrG[i][0]=0;
      }
      if (arrG[i][2]+1 <= slen && arrG[i][2]+1 > arrG[i][2]){
        arrG[i][2]=arrG[i][2]+1;
        arrP[arrG[i][2]][1]=arrP[arrG[i][2]][1]+arrG[i][0];
      } 
      if (arrG[i][1]-1 < arrG[i][1]){
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
    if (const_wave_states_minus_one == 65535){
      rowB=(rowB+1);
    } else {
      rowB=(rowB+1)%(const_wave_states_minus_one+1);
    }
    for (uint16_t i=0; i <= slen; i++){
      arrP[i][2]=0;
    }
    uint16_t i;
    for (uint16_t j=0; j < const_wave_states_minus_one; j++){
      if (const_wave_states_minus_one == 65535){
        i=(rowB+j);
      } else {
        i=(rowB+j)%(const_wave_states_minus_one+1);
      }
      if (arrB[i][0]-fade <= arrB[i][0]){
        arrB[i][0]=arrB[i][0]-fade;
      } else if (arrB[i][0] != 0){
        arrB[i][0]=0;
      }
      if (arrB[i][2]+1 <= slen && arrB[i][2]+1 > arrB[i][2]){
        arrB[i][2]=arrB[i][2]+1;
        arrP[arrB[i][2]][2]=arrP[arrB[i][2]][2]+arrB[i][0];
      } 
      if (arrB[i][1]-1 < arrB[i][1]){
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
  fade=r;
  fps=g;
  slen=b;
  for (uint16_t i=0; i <= const_wave_states_minus_one; i++){
    for (uint8_t j=0; j < 3; j++){
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
  for (uint16_t i=0; i <= slen; i++){
    SPDR = arrP[i][1] | 0x80;
    while(!(SPSR & (1<<SPIF)));
    SPDR = arrP[i][0] | 0x80;
    while(!(SPSR & (1<<SPIF)));
    SPDR = arrP[i][2] | 0x80;
    while(!(SPSR & (1<<SPIF)));
  }
  n = ((slen + 64) / 64) *3;
  while(n--) SPI.transfer(0);
  delay(1);
}
