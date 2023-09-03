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
///////please enter your sensitive data in the Secret arduino_secrets.h
char ssid[] = MY_SSID;    // your network SSID (name)
char pass[] = MY_PASS;    // your network password (use for WPA, or use as key for WEP)
char token[] = TOKEN;
char insee[] = LOC_INSEE; // insee is not the postal code... google for it! */
int status = WL_IDLE_STATUS;     // the Wifi radio's status

char server[] = SERVER;
char base_uri[] = BASE_URI;

int READ_TIMEOUT = 60;

/*************************************************************

  This is a simple demo of sending and receiving some data.
  Be sure to check out other examples!
 *************************************************************/






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
  if (!sendtoserver()) {
    Serial.print("Something is fishy...");
    WiFi.end();
    connecttowifi();
  } else {
    delay(600000);
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

typedef enum Level {
  NONE,
  HEADER,
  CHUNK,
  DATA,
  DONE
} Level;


Level processmessdata(char *mess, int ret, Level initialstate);

bool ischunked = 0;
int remainingdata = 0;

char jsonbuff[2048]; // big enough or play with realloc!

Level processmessdata(char *mess, int ret, Level initialstate)
{
  int i = 0;
  int l = 0;
  Level state = initialstate;
  int size = 0;
  
  while (mess[i]) {
    if (mess[i] == '\r') {
      mess[i]= '\0';
      Serial.println(&mess[l]);
      switch(state) {
        case NONE:
          Serial.println("state: NONE");
          if (strstr(&mess[l], "OK"))
            state = HEADER;
          break;
        case HEADER:
          Serial.print("state: HEADER *");
          Serial.print(&mess[l]);
          Serial.println("*");
          if (!mess[l]) {
            if (ischunked)
              state = CHUNK;
            else
              state = DATA;
          }
          // Check for chunked
          if (strstr(&mess[l],"Transfer-Encoding: chunked"))
            ischunked = 1;
          break;
        case CHUNK:
          Serial.println("state: CHUNK");
          // The chunk tell us the size of the data in the next bloc
          sscanf (&mess[l],"%x",&size);
          remainingdata =  size;
          Serial.print("state: CHUNK: ");
          Serial.println(size);
          if (ischunked && size>0)
            state = DATA;
          else
            state = DONE;
          break;
        case DATA:
          Serial.println("state: DATA");
          if (ischunked) {
            remainingdata = remainingdata - strlen(&mess[l]);
            if (remainingdata<=0)
              state = CHUNK;
          }
          Serial.println("DATA:");
          Serial.println(&mess[l]);
          strcat(jsonbuff,&mess[l]);
          break;
      }
      l = i + 2;
      if (!mess[l])
        break; // Done
    }
    i++;
  }
  if (mess[l]) {
    Serial.println("Done remaining data:");
    Serial.println(&mess[l]);
    strcat(jsonbuff,&mess[l]);
    remainingdata = remainingdata - strlen(&mess[l]);
  } else 
    Serial.println("Done!");
  return state;
}

bool sendtoserver() {
  WiFiSSLClient client;
  char url[256];
  strcpy(url, "GET ");
  strcat(url, base_uri);
  strcat(url, "?token=");
  strcat(url, token);
  strcat(url, "&insee=");
  strcat(url, insee);

  Serial.println("\nStarting connection to server...");
  // if you get a connection, report back via serial:
  if (!client.connect(SERVER, 443)) {
    Serial.println("Connection failed!");
    client.stop();
    return false;
  } else {
    Serial.println("Connected ...");
    Serial.print(url);
    Serial.println(" HTTP/1.1");
    Serial.print("Host: ");
    Serial.println(server);
    Serial.println("User-Agent: LED Map Client");
    Serial.println("Connection: close");
    Serial.println();
    // Make a HTTP request, and print it to console:
    client.print(url);
    client.println(" HTTP/1.1");
    client.print("Host: ");
    client.println(server);
    client.println("User-Agent: LED Sectional Client");
    client.println("Connection: close");
    client.println();
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

    // Read the response: it is chunked
    Level state = NONE;
    jsonbuff[0] = '\0';
    while (client.connected()) {
      int ret =  client.available(); 
      if (ret>0) {
        char *mess = (char *) malloc(ret+1);
        for (int i=0; i<ret; i++)  
          mess[i] = client.read();
        Serial.println("received:");
        mess[ret] = '\0';
        Serial.println(mess);
        state = processmessdata(mess, ret, state);
        free(mess);
      }
  
    }
    Serial.println("JSON");
    int sizebuff = strlen(jsonbuff);
    for (int i = 0; i<sizebuff; i=i+80) {
      char buffet[81];
      memcpy(buffet, &jsonbuff[i], 80);
      buffet[80] = '\0';
      Serial.println(buffet);
    }
    Serial.println("JSON");
    client.stop();
  }
  return true;
}

