#include <Arduino.h>

#include <CircularBuffer.hpp>


#include <artificial_nose_inferencing.h>

#include <Multichannel_Gas_GMXXX.h>
#include <Wire.h>

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
  INFERENCE
};
enum MODE mode = INFERENCE;

enum SCREEN_MODE
{
  SENSORS,
  GRAPH,
  INFERENCE_RESULTS
};
enum SCREEN_MODE screen_mode = GRAPH;

int latest_inference_idx = -1;
float latest_inference_confidence_level = -1.;

#define MAX_CHART_SIZE 50
typedef std::queue<double>  doubles;
// CircularBuffer<double,MAX_CHART_SIZE> doubles;
std::vector<doubles> chart_series = std::vector<doubles>(NB_SENSORS, doubles());

// Allocate a buffer for the values we'll read from the gas sensor
CircularBuffer<float, EI_CLASSIFIER_DSP_INPUT_FRAME_SIZE> buffer;

uint64_t next_sampling_tick = micros();

#define INITIAL_FAN_STATE LOW
static int fan_state = INITIAL_FAN_STATE;

static bool debug_nn = false; // Set this to true to see e.g. features generated
                              // from the raw signal

void setup()
{

  Serial.begin(115200);

  pinMode(D0, OUTPUT);
  digitalWrite(D0, fan_state);

  pinMode(D0, OUTPUT);
  digitalWrite(D0, INITIAL_FAN_STATE);

  gas->begin(Wire, 0x08); // use the hardware I2C
 
}

int fan = 0;

void loop()
{

  if (mode == TRAINING) {
    strcpy(title_text, "Training mode");
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

    if (chart_series[i].size() == MAX_CHART_SIZE) {
      chart_series[i].pop();
    }
    chart_series[i].push(sensorVal);
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
  } else { // INFERENCE

    if (!buffer.isFull()) {
      ei_printf("Need more samples to start infering.\r\n");
    } else {
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

      int lineNumber = 60;
      char lineBuffer[60] = "";

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

/*
      if (screen_mode == INFERENCE_RESULTS) {
        if (best_prediction != latest_inference_idx) {
          // clear icon background
          spr.pushSprite(0, 0);
        }
        #if USE_ICONS
        spr.pushImage(30, 35, 130, 130, (uint16_t*)ICONS_MAP[best_prediction]);
        #endif
        spr.setFreeFont(&Roboto_Bold_28);
        spr.setTextDatum(CC_DATUM);
        spr.setTextColor(TEXT_COLOR);
        spr.drawString(title_text, 160, 200, 1);
      }
 */

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
