#include <Servo.h>

Servo servoX;
String inputString = "";
bool stringComplete = false;

int currentX = 90;  // posisi awal servo
int targetX = 90;   // target posisi dari Python

void setup() {
  Serial.begin(9600);
  servoX.attach(9);
  servoX.write(currentX);  // set posisi awal
}

void loop() {
  // Update target dari Python
  serialEvent();
  if (stringComplete) {
    // Parse the string: assume format "x,area" – extract x
    int commaIndex = inputString.indexOf(',');
    if (commaIndex != -1) {
      targetX = currentX + inputString.substring(0, commaIndex).toInt();
      if (targetX > 180){
        targetX = 180;
      }
      if (targetX < 0) targetX= 0;
      // Serial.println(targetX);
    }
    inputString = "";
    stringComplete = false;
  }

  if (abs(currentX - targetX) > 10){
    if (targetX > currentX){
      currentX =currentX  +  1;
      if (currentX > 180 ) currentX = 180;
    }else{
      currentX = currentX  - 1;
      if (currentX <0) currentX = 0;
    }
  }
  // Serial.println(currentX);

  
  servoX.write(currentX);

  delay(20);  // Slightly increased delay for more smoothness (was 15)
}

void serialEvent() {
  while (Serial.available()) {
    char inChar = (char)Serial.read();
    inputString += inChar;
    if (inChar == '\n') {
      stringComplete = true;
    }
  }
}