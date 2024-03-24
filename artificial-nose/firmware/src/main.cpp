#include <Arduino.h>

#include <CircularBuffer.hpp>


#include <artificial_nose_inferencing.h>

#include <Multichannel_Gas_GMXXX.h>
#include <Wire.h>
#include <queue>

#include <WiFi.h>

#include "arduino_secrets.h"

/**
* @brief      Printf function uses vsnprintf and output using Arduino Serial
*
* @param[in]  format     Variable argument list
*/
void ei_printf(const char *format, ...)
{
  static char print_buf[512] = { 0 };

  va_list args;
  va_start(args, format);
  int r = vsnprintf(print_buf, sizeof(print_buf), format, args);
  va_end(args);

  if (r > 0)
  {
    Serial.write(print_buf);
  }
}

GAS_GMXXX<TwoWire>* gas = new GAS_GMXXX<TwoWire>();

typedef uint32_t (GAS_GMXXX<TwoWire>::*sensorGetFn)();

typedef struct SENSOR_INFO
{
  char* name;
  char* unit;
  std::function<uint32_t()> readFn;
  uint32_t last_val;
} SENSOR_INFO;

SENSOR_INFO sensors[4] = {
  { "NO2", "ppm", std::bind(&GAS_GMXXX<TwoWire>::measure_NO2, gas), 0 },
  { "CO", "ppm", std::bind(&GAS_GMXXX<TwoWire>::measure_CO, gas), 0 },
  { "C2H5OH", "ppm", std::bind(&GAS_GMXXX<TwoWire>::measure_C2H5OH, gas), 0 },
  { "VOC", "ppm", std::bind(&GAS_GMXXX<TwoWire>::measure_VOC, gas), 0 }
};
#define NB_SENSORS 4

char title_text[50] = "";

enum MODE
{
  TRAINING,
  INFERENCE,
  WIFI,
  STOP
};
enum MODE mode = INFERENCE;

int latest_inference_idx = -1;
float latest_inference_confidence_level = -1.;

// Allocate a buffer for the values we'll read from the gas sensor
CircularBuffer<float, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE> buffer;

uint64_t next_sampling_tick = micros();

#define INITIAL_FAN_STATE LOW
static int fan_state = INITIAL_FAN_STATE;

static bool debug_nn = false; // Set this to true to see e.g. features generated
                              // from the raw signal
const char ssid[] = MY_SSID;
const char pass[] = MY_PASS;

void connecttowifi();
bool sendtojfc();

void setup()
{

  Serial.begin(115200);
  while (!Serial) {
     // wait for serial port to connect. Needed for native USB port only
  }

  pinMode(D0, OUTPUT);
  digitalWrite(D0, fan_state);

  pinMode(D0, OUTPUT);
  digitalWrite(D0, INITIAL_FAN_STATE);

  connecttowifi();
  IPAddress ip  = WiFi.localIP();
  Serial.print("IP Address: ");
  Serial.println(ip);

  gas->begin(Wire, 0x08); // use the hardware I2C
 
}

int fan = 0;

void loop()
{

  if (Serial.available()) {
    switch (Serial.read()) {
      case 't': mode = TRAINING; break;
      case 'i': mode = INFERENCE; break;
      case 'w': mode = WIFI; break;
      case 's': mode = STOP; break;
    }
  }

  if (mode == TRAINING) {
    strcpy(title_text, "Training mode");
  } else {
    strcpy(title_text, "Inference mode");
  }

  uint64_t new_sampling_tick = -1;
  if (micros() > next_sampling_tick) {
    new_sampling_tick = micros() + (EI_CLASSIFIER_INTERVAL_MS * 1000);
    next_sampling_tick = new_sampling_tick;
  }
  for (int i = NB_SENSORS - 1; i >= 0; i--) {
    uint32_t sensorVal = sensors[i].readFn();
    if (sensorVal > 999) {
      sensorVal = 999;
    }
    sensors[i].last_val = sensorVal;

    if (new_sampling_tick != -1) {
      buffer.unshift(sensorVal);
    }
  }

  /*
        doc["no2"] = sensors[0].last_val;
        doc["co"] = sensors[1].last_val;
        doc["c2h5oh"] = sensors[2].last_val;
        doc["voc"] = sensors[3].last_val;
   */

  if (mode == TRAINING) {
    ei_printf("%d,%d,%d,%d\r\n", sensors[0].last_val, sensors[1].last_val, sensors[2].last_val, sensors[3].last_val);
  } else if (mode == INFERENCE) { // INFERENCE

    if (!buffer.isFull()) {
      ei_printf("Need more samples to start infering.\r\n");
    } else {
      int lineNumber = 60;
      char lineBuffer[60] = "";
      // Turn the raw buffer into a signal which we can then classify
      float buffer2[EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE];

      for (int i = 0; i < buffer.size(); i++) {
        buffer2[i] = buffer[i];
        ei_printf("%f, ", buffer[i]);
      }
      ei_printf("\n");

      signal_t signal;
      int err = numpy::signal_from_buffer(
        buffer2, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE, &signal);
      if (err != 0) {
        ei_printf("Failed to create signal from buffer (%d)\n", err);
        return;
      }

      // Run the classifier
      ei_impulse_result_t result = { 0 };

      err = run_classifier(&signal, &result, debug_nn);
      if (err != EI_IMPULSE_OK) {
        ei_printf("ERR: Failed to run classifier (%d)\r\n", err);
        return;
      }

      // print the predictions
      size_t best_prediction = 0;
      ei_printf("Predictions (DSP: %d ms., Classification: %d ms., Anomaly: %d "
                "ms.): \r\n",
                result.timing.dsp,
                result.timing.classification,
                result.timing.anomaly);

      for (size_t ix = 0; ix < EI_CLASSIFIER_LABEL_COUNT; ix++) {
        if (result.classification[ix].value >=
            result.classification[best_prediction].value) {
          best_prediction = ix;
        }

        sprintf(lineBuffer,
                "    %s: %.5f\r\n",
                result.classification[ix].label,
                result.classification[ix].value);
        ei_printf(lineBuffer);
      }

#if EI_CLASSIFIER_HAS_ANOMALY == 1
      sprintf(lineBuffer, "    anomaly score: %.3f\r\n", result.anomaly);
      ei_printf(lineBuffer);
#endif

      sprintf(title_text,
              "%s (%d%%)",
              result.classification[best_prediction].label,
              (int)(result.classification[best_prediction].value * 100));

      ei_printf("Best prediction: %s\r\n", title_text);

      // check if we need to report a change in detected scent to the IoT platform. 
      // 2 cases: new scent has been detected, or confidence level of a scent previously reported as changed by 5+ percentage points
      if (best_prediction != latest_inference_idx ||
          best_prediction == latest_inference_idx &&
            (result.classification[best_prediction].value -
               latest_inference_confidence_level >
             .05)) {

      latest_inference_idx = best_prediction;
      latest_inference_confidence_level =
        result.classification[best_prediction].value;
      }
    }
  } else if (mode == STOP) { // Do nothing... wait a little
    delay(1000);
  } else { // WIFI
      /* send something to the server */
      if (!sendtojfc()) {
        Serial.print("Something is fishy...");
        // WiFi.end(); not in arduino-esp32 ...
        connecttowifi();
      }
  }

  // spr.pushSprite(0, 0, TFT_MAGENTA);

  // Uncomment block below to dump hex-encoded TFT sprite to serial **/

  /**

    uint16_t width = tft.width(), height = tft.height();
    // Image data: width * height * 2 bytes
    for (int y = 0; y < height ; y++) {
      for (int x=0; x<width; x++) {
        Serial.printf("%04X", tft.readPixel(x,y));
      }
    }

    **/
}

/* For the other part of example  */
char SERVER[] = "jfclere.myddns.me";
char BASE_URI[] = "/webdav/temp.txt";
int READ_TIMEOUT = 60;


void connecttowifi() {
  // attempt to connect to Wifi network:
  int status = WL_IDLE_STATUS;
  WiFi.mode(WIFI_STA);
  while (status != WL_CONNECTED) {

    Serial.print("Attempting to connect to WPA SSID: ");

    Serial.println(ssid);

    // Connect to WPA/WPA2 network:

    WiFi.begin(ssid, pass);

    // wait 10 seconds for connection:

    delay(10000);
    WiFi.waitForConnectResult();
    status = WiFi.status();

  }
}

bool sendtojfc() {
  WiFiClient client;
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
