#include <Wire.h>
#include "Adafruit_MCP9808.h"

// Serial test script
String readString;

// Create the MCP9808 temperature sensor object
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();

// Pin declarations
P12 = A2 // Positive 12V Rail
N12 = A1 // Negative 12V Rail
depth = A0 // Depth sensor

void setup()
{
  Serial.begin(9600);  // initialize serial communications at 9600 bps

  // Setup the pins as output
  pinMode(P12, OUTPUT);
  pinMode(N12, OUTPUT);
  pinMode(depth, OUTPUT);

}

void loop()
{
  while(!Serial.available()) {}
  // serial read section
  while (Serial.available())
  {
    if (Serial.available() >0)
    {
      char c = Serial.read();  //gets one byte from serial buffer
      readString += c; //makes the string readString
    }
  }

  if (readString.length() >0)
  {
    // Check if the "data" command was received, if so send the data
    if(readString == "data"){
      
    }
  }
}
