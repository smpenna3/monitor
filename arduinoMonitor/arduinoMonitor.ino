#include <Wire.h>
#include "Adafruit_MCP9808.h"

// Serial test script
String readString;

// Create the MCP9808 temperature sensor object
Adafruit_MCP9808 tempsensor = Adafruit_MCP9808();

// Pin declarations
int P12 = A2; // Positive 12V Rail
int N12 = A1; // Negative 12V Rail
int depth = A0; // Depth sensor

// Conversion factor from ADC to voltage
float convertFactor = 5.0/1023.0;

// Amplify from the voltage division of 12->4
// This is the OPOSITE of the voltage division
float voltageDivisionScale = (10.3+4.686)/4.686;

// Depth sensor is 60 meters per volt
float depthConvertFactor = 60;

void setup()
{
  Serial.begin(9600);  // initialize serial communications at 9600 bps

  // Setup the pins as output
  pinMode(P12, INPUT);
  pinMode(N12, INPUT);
  pinMode(depth, INPUT);

  tempsensor.wake(); // Wake the sensor
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
  //Serial.println(readString);
  if (readString.length() >0)
  {
    // Check if the "data" command was received, if so send the data
    if(readString == "data"){
      // Get the temperature reading
      float c = tempsensor.readTempC();
      float f = c * 9.0 / 5.0 + 32;

      // Get the positive 12V reading
      float p12Reading = analogRead(P12) * convertFactor * voltageDivisionScale;
      
      // Get the negative 12V reading
      float n12Reading = analogRead(N12) * convertFactor * voltageDivisionScale * -1.0;

      // Get the depth sensor
      float depthReading = analogRead(depth) * convertFactor * depthConvertFactor;


      // Create the JSON string to send out
      String p12Str = String(p12Reading);
      String n12Str = String(n12Reading);
      String depthStr = String(depthReading);
      String tempStr = String(f);

      // " is replaced with $ for string formatting, changed later in python
      String outData = String("temp, " + tempStr + ", depth, " + depthStr + ", n12, " + n12Str + ", p12, " + p12Str + "\n");
      //String outData = String("'{$temp$:$" + tempStr + "$, $depth$:$" + depthStr + "$, $n12$:$" + n12Str + "$, $p12$:$" + p12Str + "$}" + "/n");

      Serial.print(outData);

      readString = "";
    }
  }

  if(readString.length() > 4){
    readString = "";
  }
}
