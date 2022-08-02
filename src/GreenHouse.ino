//Ben Lepsch and Adnane Ezouhri group 7A
#include <ArduinoBLE.h>
#include <Arduino_HTS221.h>
#include "TimeoutTimer.h"
#define BUFSIZE 20

/*  Create a Environmental Sensing Service (ESS) and a 
 *  characteristic for its temperature value.
 */
BLEService essService("181A");
BLEShortCharacteristic tempChar("2A6E", BLERead | BLENotify );
BLEShortCharacteristic humChar("2a6f", BLERead | BLENotify );
BLEDevice centrale;

void setup() 
{
  Serial.begin(9600);
  while(!Serial);

  if (!HTS.begin()) {
    Serial.println("Failed to initialize humidity-temperature sensor!");
    while (1);
  }
  
  if ( !BLE.begin() )
  {
    Serial.println("Starting BLE failed!");
    while(1);
  }

  // Get the Arduino's BT address
  String deviceAddress = BLE.address();

  // The device name we'll advertise with.
  BLE.setLocalName("ArduinoBLE Group 7");


  // Get ESS service ready.
  essService.addCharacteristic( tempChar );
  essService.addCharacteristic( humChar );
  BLE.addService( essService );

  // Start advertising our new service.
  BLE.advertise();
  Serial.println("Bluetooth device (" + deviceAddress + ") active, waiting for connections...");
  
  
}

void loop() 
{
  // Wait for a BLE central device.
     centrale = BLE.central();
     
  // If a central device is connected to the peripheral...
  if ( centrale )
  {
    // Print the central's BT address.
    Serial.print("Connected to central: ");
    Serial.println( centrale.address() );

    // While the central device is connected...
    while( centrale.connected())
    {


      //Get temperature from Arduino sensor
       float temp = HTS.readTemperature();
       float hum  = HTS.readHumidity();
       
      Serial.print("Humidity: ");
      Serial.println(hum);
      Serial.print("Temp: ");
      Serial.println(temp);
     

      // Cast to desired format; multiply by 100 to keep desired precision.
      short shortTemp = (short) (temp * 100);
      short shortHum = (short) (hum * 100);

      // Send data to centeral for temperature characteristic.
      tempChar.writeValue( shortTemp );
      delay(1000);
      humChar.writeValue( shortHum);
      delay(2000);
      
    }
    
    Serial.print("Disconnected from central: ");
    Serial.println( centrale.address() );
    
  }
}
