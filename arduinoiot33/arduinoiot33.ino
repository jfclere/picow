#include <Adafruit_BusIO_Register.h>
#include <Adafruit_I2CDevice.h>
#include <Adafruit_I2CRegister.h>
#include <Adafruit_SPIDevice.h>

#include <Adafruit_BME280.h>

#include <Adafruit_BME280.h>

#include <Adafruit_BME280.h>

#include <Adafruit_BME280.h>

#include <Adafruit_BME280.h>

/*

 This example connects to an encrypted Wifi network.

 Then it prints the  MAC address of the Wifi module,

 the IP address obtained, and other network details and send a HTTP request and reads the server response.

 created 13 July 2010

 by dlf (Metodo2 srl)

 modified 31 May 2012

 by Tom Igoe

 modified Aug 2023

 by Jean-Frederic Clere

 */
#include <SPI.h>
#include <WiFiNINA.h>
#include <Arduino.h>
#include "Bme280.h"
#include "base64encode.h"

#include "arduino_secrets.h"
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = MY_SSID;        // your network SSID (name)
char pass[] = MY_PASS;    // your network password (use for WPA, or use as key for WEP)
char user_pass[] = USER_PASS; // httpd user/password
char BASE_URI[] = URL; // Where to put the file. 

/* For the other part of example  */
char SERVER[] = "jfclere.myddns.me";
int READ_TIMEOUT = 60;

#define RED 2
#define GREEN 3
#define BLUE 4

char base64[128];

int count;

Bme280TwoWire sensor;

void setup() {

  //Initialize serial and wait for port to open:
  pinMode(RED, OUTPUT);
  pinMode(GREEN, OUTPUT);
  pinMode(BLUE, OUTPUT);

  Serial.begin(9600);
  Wire.begin();
  base64_encode(user_pass, base64);

  // check for the WiFi module:

  if (WiFi.status() == WL_NO_MODULE) {

    Serial.println("Communication with WiFi module failed!");

    // don't continue

    while (true);

  }

  String fv = WiFi.firmwareVersion();

  if (fv < WIFI_FIRMWARE_LATEST_VERSION) {

    Serial.println("Please upgrade the firmware");

  }

  connecttowifi();

  // you're connected now, so print out the data:

  Serial.print("You're connected to the network");

  printCurrentNet();

  printWifiData();

  sensor.begin(Bme280TwoWireAddress::Primary);
  sensor.setSettings(Bme280Settings::indoor());

  count = 6;

}

void loop() {

  // check the network connection once every 10 seconds:
  if (WiFi.status() != WL_CONNECTED)
    digitalWrite(GREEN, LOW);
  delay(10000);
  
  Serial.println("Starting loop");



  printCurrentNet();
  if (count == 6) {
    auto temperature = String(sensor.getTemperature()) + "C";
    auto pressure = String(sensor.getPressure() / 100.0) + "hPa";
    auto humidity = String(sensor.getHumidity()) + "%";

    String measurements = "Temperature : " + temperature + "\nPressure : " + pressure + "\nHumidity : " + humidity +"\n";
    Serial.println(measurements);
    Serial.println("have BME280 info");
    if (!sendtojfc(measurements)) {
      Serial.print("Something is fishy...");
      digitalWrite(BLUE, LOW);
      WiFi.end();
      connecttowifi();
    } else {
      count = 0;
    }
  } else
    count++;
}

void connecttowifi() {
  // attempt to connect to Wifi network:
  int status;
  while (status != WL_CONNECTED) {

    Serial.print("Attempting to connect to WPA SSID: ");

    Serial.println(ssid);

    // Connect to WPA/WPA2 network:

    status = WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:

    delay(10000);

  }
  digitalWrite(GREEN, HIGH);

}

void printWifiData() {

  // print your board's IP address:

  IPAddress ip = WiFi.localIP();

  Serial.print("IP Address: ");

  Serial.println(ip);

  Serial.println(ip);

  // print your MAC address:

  byte mac[6];

  WiFi.macAddress(mac);

  Serial.print("MAC address: ");

  printMacAddress(mac);
}

void printCurrentNet() {

  // print the SSID of the network you're attached to:

  Serial.print("SSID: ");

  Serial.println(WiFi.SSID());

  // print the MAC address of the router you're attached to:

  byte bssid[6];

  WiFi.BSSID(bssid);

  Serial.print("BSSID: ");

  printMacAddress(bssid);

  // print the received signal strength:

  long rssi = WiFi.RSSI();

  Serial.print("signal strength (RSSI):");

  Serial.println(rssi);

  // print the encryption type:

  byte encryption = WiFi.encryptionType();

  Serial.print("Encryption Type:");

  Serial.println(encryption, HEX);

  Serial.println();
}

void printMacAddress(byte mac[]) {

  for (int i = 5; i >= 0; i--) {

    if (mac[i] < 16) {

      Serial.print("0");

    }

    Serial.print(mac[i], HEX);

    if (i > 0) {

      Serial.print(":");

    }

  }

  Serial.println();
}

bool sendtojfc(String data) {
  WiFiSSLClient client;
  Serial.println("\nStarting connection to server...");
  // if you get a connection, report back via serial:
  if (!client.connect(SERVER, 443)) {
    Serial.println("Connection failed!");
    client.stop();
    digitalWrite(BLUE, LOW);
    return false;
  } else {
    digitalWrite(BLUE, HIGH);
    Serial.println("Connected ...");
    Serial.print("PUT ");
    Serial.print(BASE_URI);
    Serial.print("/temp.txt");
    Serial.println(" HTTP/1.1");
    Serial.print("Host: ");
    Serial.println(SERVER);
    Serial.print("Authorization: Basic ");
    Serial.println(base64);
    Serial.println("User-Agent: LED Map Client");
    Serial.print("Content-Length: ");
    Serial.println(data.length());
    Serial.println("Expect: 100-continue");
    Serial.println();
    Serial.print(data);
    // Make a HTTP request, and print it to console:
    
    client.print("PUT ");
    client.print(BASE_URI);
    client.print("/temp.txt");
    client.println(" HTTP/1.1");
    client.print("Host: ");
    client.println(SERVER);
    client.print("Authorization: Basic ");
    client.println(base64);
    client.println("User-Agent: LED Map Client");
    client.print("Content-Length: ");
    client.println(data.length());
    client.println("Expect: 100-continue");
    client.println();
    client.print(data);
   
    client.flush();
    unsigned long t = millis(); // start time

    Serial.println("Getting data");

    while (!client.connected()) {
      if ((millis() - t) >= (READ_TIMEOUT * 1000)) {
        Serial.println("---Timeout---");
        client.stop();
        return false;
      }
      Serial.print(".");
      delay(1000);
    }

    // Read the response
    while (client.connected()) {
      digitalWrite(RED, HIGH);
      if (client.available()) {

          char c = client.read();

          Serial.write(c);
      }
  
    }
    client.stop();
    digitalWrite(RED, LOW);
  }
  Serial.println("");
  return true;
}
