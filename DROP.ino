#include <Wire.h> 
#include <SparkFun_u-blox_GNSS_Arduino_Library.h>
#include <u-blox_config_keys.h>
#include <u-blox_structs.h>
#include <Servo.h>
#include <Adafruit_BMP3XX.h>
#include <bmp3.h>
#include <bmp3_defs.h>

/*]======================================================================================
 *                                  D.R.O.P. Rev2.a 
 *                          Designated Release of Payload (Two-Month)
 *                             For use with Teensy 4.0
 *                                     (10/19/2022)
 * Description: Automatic release mechanism of balloon line for a given Target altitude
 *              Sea Level set as zero on start-up (AGL)
 *              Xbee override capable, command: DROP
 * 
 * 
 * - Jaiden Stark
 ======================================================================================*/

// Servo for controlling trigger
Servo trigger;
int pos = 90;

// Barometer
Adafruit_BMP3XX bmp;
float seaLevel = 1028; float altitude = 0;

String command;

unsigned long lastTime = 0;
bool cut = false, light = false;
//==============================================================
int target = 7000;                     // Target altitude (meters)
//==============================================================
int led = 4, buzzer = 9;

int sampleRate = 700;

String device = "Drop2";   // <---------DEVICE NAME

const byte numChars = 32;
char receivedChars[numChars];   // an array to store the received data

void setup() {
  // Start serial stream
 // Serial.begin(9600);
  Serial1.begin(9600);
  Serial2.begin(9600);

  pinMode(led, OUTPUT);
  pinMode(buzzer, OUTPUT);
  Serial1.println("FLIGHT CODE");
  // Start I2C
  Wire.begin();
 
  // Attach servo to pin
  trigger.attach(14);
  trigger.write(pos);
  
  // Initialize Barometer
  if (!bmp.begin_I2C()) {
    Serial1.println("Could not find a valid BMP3 sensor, check wiring!");
    while (1){
      delay(50);
      digitalWrite(buzzer, HIGH);
      delay(50);
      digitalWrite(buzzer, LOW);
    }
  }
  // Calibrate pressure readings
  for(int i = 0; i < 11; i++){
    bmp.readPressure();
    delay(10);
  }
  // Define sea level reference as ground level pressure
  seaLevel = bmp.readPressure()/100.0;
  altitude = bmp.readAltitude(seaLevel);

  trigger.write(0);
  delay(500);
  trigger.write(90);
  delay(500);
  trigger.write(0);
  delay(500);
  trigger.write(90);
  delay(500);
  trigger.write(0);
  delay(500);
  trigger.write(90);
  delay(500);


  digitalWrite(led, HIGH); digitalWrite(buzzer, HIGH);
  delay(500);
  digitalWrite(led, LOW); digitalWrite(buzzer, LOW);
  delay(250);
  digitalWrite(led, HIGH); digitalWrite(buzzer, HIGH);
  delay(500);
  digitalWrite(led, LOW); digitalWrite(buzzer, LOW);
  delay(250);
  digitalWrite(led, HIGH); digitalWrite(buzzer, HIGH);
  delay(500);
  digitalWrite(led, LOW); digitalWrite(buzzer, LOW);
  delay(250);

  Serial1.println("START"); 
}
// =============================================================================================================================//
void loop() {

  if(millis()-lastTime >= sampleRate){
    altitude = bmp.readAltitude(seaLevel);
    sendData();
    printData();
    digitalWrite(led, light);
    light = !light;
    lastTime = millis(); 
  }

//  command = recieve();

  if(!cut && altitude >= target){
    cutDown();
  }
  if(Serial2.available() > 0){
    cutDown();
    serial2Flush();  
  }
  delay(10);
}

void cutDown(){
  Serial1.println(F("================ CUTDOWN ================="));
  digitalWrite(led, HIGH); digitalWrite(buzzer, HIGH);
  delay(100);
  digitalWrite(led, LOW); digitalWrite(buzzer, LOW);
  delay(100);
  digitalWrite(led, HIGH); digitalWrite(buzzer, HIGH);
  delay(100);
  digitalWrite(led, LOW); digitalWrite(buzzer, LOW);
  delay(100);
  digitalWrite(led, HIGH); digitalWrite(buzzer, HIGH);
  delay(100);
  digitalWrite(led, LOW); digitalWrite(buzzer, LOW);
  delay(100);
  cut = true;
  
  for(int i=0;i<=5;i++){
    trigger.write(0);
    delay(500);
    trigger.write(90);
    delay(500);
  } 
}
void printData(){  // for OpenLOg
  //myGNSS.checkUblox();
  Serial1.println((String)(millis()/1000.0) + "," + device + "," + (String)altitude + "," + (String)bmp.readPressure() + ", " + (String)bmp.temperature + "," + (String)pos + "," + (String)cut + "," + command);
  };

void sendData(){  // For XBEE
  String str = (String)(millis()/1000.0) + "," + device + "," + (String)altitude + "," + (String)cut;
  int str_len = str.length() + 1; 
  char char_array[str_len];
  str.toCharArray(char_array, str_len);
  Serial2.println(str);
}


void serial2Flush(){
  while(Serial2.available() > 0) {
    char t = Serial2.read();
  }
}
/*
String recieve() {
    String rc
    if (Serial2.available() > 0) {
        String rc = Serial2.read();
        return rc;
    }

}
*/
