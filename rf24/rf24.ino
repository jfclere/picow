// SimpleRx - the slave or the receiver

#include <SPI.h>
#include <nRF24L01.h>
#include <RF24.h>

#define CE_PIN   9
#define CSN_PIN 10

const byte thisSlaveAddress[5] = {'2','N','o','d','e'};

RF24 radio(CE_PIN, CSN_PIN);

char dataReceived[11]; // this must match dataToSend in the TX
bool newData = false;

//===========

void setup() {

    Serial.begin(9600);
    while (!Serial) {
      ; // wait for serial port to connect. Needed for native USB port only
    }
    Serial.println("SimpleRx Starting");
    if (!radio.begin())
      Serial.println("Failed!");
    radio.setDataRate(RF24_250KBPS);
    radio.setPALevel(RF24_PA_MAX, 0);
    radio.setChannel(52);
    radio.openReadingPipe(1, thisSlaveAddress);
    radio.setPayloadSize(11);
    radio.startListening();
}

//=============

void loop() {
    getData();
    showData();
}

//==============

void getData() {
    if ( radio.available() ) {
        radio.read( &dataReceived, sizeof(dataReceived) );
        newData = true;
    }
}

void showData() {
    if (newData == true) {
        Serial.print("Data received ");
        Serial.println(dataReceived);
        newData = false;
    }
}