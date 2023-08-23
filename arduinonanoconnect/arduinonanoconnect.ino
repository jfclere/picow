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

#include "arduino_secrets.h"
///////please enter your sensitive data in the Secret tab/arduino_secrets.h
char ssid[] = MY_SSID;        // your network SSID (name)
char pass[] = MY_PASS;    // your network password (use for WPA, or use as key for WEP)
int status = WL_IDLE_STATUS;     // the Wifi radio's status
char SERVER[] = "jfclere.myddns.me";
char BASE_URI[] = "/webdav/temp.txt";
int READ_TIMEOUT = 60;

void setup() {

  //Initialize serial and wait for port to open:

  Serial.begin(9600);

  while (!Serial) {

    ; // wait for serial port to connect. Needed for native USB port only

  }

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

}

void loop() {

  // check the network connection once every 10 seconds:

  delay(10000);

  printCurrentNet();
  if (!sendtojfc()) {
    Serial.print("Something is fishy...");
    WiFi.end();
    connecttowifi();
  }
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

bool sendtojfc() {
  WiFiSSLClient client;
  Serial.println("\nStarting connection to server...");
  // if you get a connection, report back via serial:
  if (!client.connect(SERVER, 443)) {
    Serial.println("Connection failed!");
    client.stop();
    return false;
  } else {
    Serial.println("Connected ...");
    Serial.print("GET ");
    Serial.print(BASE_URI);
    Serial.println(" HTTP/1.1");
    Serial.print("Host: ");
    Serial.println(SERVER);
    Serial.println("User-Agent: LED Map Client");
    Serial.println("Connection: close");
    Serial.println();
    // Make a HTTP request, and print it to console:
    client.print("GET ");
    client.print(BASE_URI);
    client.println(" HTTP/1.1");
    client.print("Host: ");
    client.println(SERVER);
    client.println("User-Agent: LED Sectional Client");
    client.println("Connection: close");
    client.println();
    client.flush();
    unsigned long t = millis(); // start time

    Serial.print("Getting data");

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

       if (client.available()) {

          char c = client.read();

          Serial.write(c);
       }
  
    }
    client.stop();
  }
  return true;
}