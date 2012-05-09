//LED flag values never use 0 or 255 must match arduino- figure out where to steal the data bits from
//for now I just took an even distribution but this is probablly bad 
//because of curve of the led responce to current
int ld0=21;   //R0
int ld1=41;   //G0
int ld2=61;   //B0
int ld3=81;   //R1
int ld4=101;  //G1
int ld5=121;  //B1
int ld6=141;  //R2
int ld7=161;  //G2
int ld8=181;  //B2
int ld9=201;  //R3
int ld10=221; //G3
int ld11=241; //B3

//int led0=3; // variables to store the pin numbers for atmega328
//int led1=5;
//int led2=6;
//int led3=9;
//int led4=10;
//int led5=11;
int led0=2; //variables to store the pin numbers for atmega2560
int led1=3;
int led2=4;
int led3=5;
int led4=6;
int led5=7;
int led6=8;
int led7=9;
int led8=10;
int led9=11;
int led10=12;
int led11=13;
int pwr=14;
int fV; //incoming flag value
int dV; //incoming data value

void setup() {
  Serial.begin(115200);
//  pinMode(led0,OUTPUT); // set up pins
//  pinMode(led1,OUTPUT);
//  pinMode(led2,OUTPUT);
//  pinMode(led3,OUTPUT);
//  pinMode(led4,OUTPUT);
//  pinMode(led5,OUTPUT);
////  pinMode(led6,OUTPUT); // set up pins
////  pinMode(led7,OUTPUT);
////  pinMode(led8,OUTPUT);
////  pinMode(led9,OUTPUT);
////  pinMode(led10,OUTPUT);
////  pinMode(led11,OUTPUT);
  analogWrite(led0,0); //use to control power supply and not let signal float
  analogWrite(led1,0);
  analogWrite(led2,0);
  analogWrite(led3,0);
  analogWrite(led4,0);
  analogWrite(led5,0);
  analogWrite(led6,0);
  analogWrite(led7,0);
  analogWrite(led8,0);
  analogWrite(led9,0);
  analogWrite(led10,0);
  analogWrite(led11,0);
  pinMode(pwr,OUTPUT);
  digitalWrite(pwr,LOW);
}

void loop(){
  while (Serial.available()>1){
    fV=Serial.read();
    dV=Serial.read();
    if (((fV==ld0) || (fV==ld1) || (fV==ld2) || (fV==ld3) || (fV==ld4) || (fV==ld5) || (fV==ld6) || (fV==ld7) || (fV==ld8) || (fV==ld9) || (fV==ld10) || (fV==ld11) && ((dV!=ld0) || (dV!=ld1) || (dV!=ld2) || (dV!=ld3) || (dV!=ld4) || (dV!=ld5) || (dV!=ld6) || (dV!=ld7) || (dV!=ld8) || (dV!=ld9) || (dV!=ld10) || (dV!=ld11)))){
      if (fV==ld0){
          analogWrite(led0,dV);
      }
      if (fV==ld1){
          analogWrite(led1,dV);
      }
      if (fV==ld2){
          analogWrite(led2,dV);
      }
      if (fV==ld3){
          analogWrite(led3,dV);
      }
      if (fV==ld4){
          analogWrite(led4,dV);
      }
      if (fV==ld5){
          analogWrite(led5,dV);
      }
      if (fV==ld6){
          analogWrite(led6,dV);
      }
      if (fV==ld7){
          analogWrite(led7,dV);
      }
      if (fV==ld8){
          analogWrite(led8,dV);
      }
      if (fV==ld9){
          analogWrite(led9,dV);
      }
      if (fV==ld10){
          analogWrite(led10,dV);
      }
      if (fV==ld11){
          analogWrite(led11,dV);
      }
    } else {
        Serial.read();
    }
  }
}

