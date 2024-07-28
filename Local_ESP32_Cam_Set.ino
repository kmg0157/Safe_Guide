/*********
  ESPCAM image to flask with http-client library
  based on:
  Rui Santos
  Complete project details at https://RandomNerdTutorials.com/esp32-cam-take-photo-save-microsd-card
  
  IMPORTANT!!! 
   - Select Board "AI Thinker ESP32-CAM"
   - GPIO 0 must be connected to GND to upload a sketch
   - After connecting GPIO 0 to GND, press the ESP32-CAM on-board RESET button to put your board in flashing mode
  
  Permission is hereby granted, free of charge, to any person obtaining a copy
  of this software and associated documentation files.
  The above copyright notice and this permission notice shall be included in all
  copies or substantial portions of the Software.
*********/

#include "esp_camera.h"
#include "Arduino.h"
#include "FS.h"               // SD Card ESP32
#include "SD_MMC.h"           // SD Card ESP32
#include "soc/soc.h"          // Disable brownour problems
#include "soc/rtc_cntl_reg.h" // Disable brownour problems
#include "driver/rtc_io.h"
#include <EEPROM.h> // read and write from flash memory
#include <HTTPClient.h>
#include <WiFi.h>
// define the number of bytes you want to access
#define EEPROM_SIZE 1

//======================================== CAMERA_MODEL_AI_THINKER GPIO.
#define PWDN_GPIO_NUM 32
#define RESET_GPIO_NUM -1
#define XCLK_GPIO_NUM 0
#define SIOD_GPIO_NUM 26
#define SIOC_GPIO_NUM 27

#define Y9_GPIO_NUM 35
#define Y8_GPIO_NUM 34
#define Y7_GPIO_NUM 39
#define Y6_GPIO_NUM 36
#define Y5_GPIO_NUM 21
#define Y4_GPIO_NUM 19
#define Y3_GPIO_NUM 18
#define Y2_GPIO_NUM 5
#define VSYNC_GPIO_NUM 25
#define HREF_GPIO_NUM 23
#define PCLK_GPIO_NUM 22
//======================================== 

// LED Flash PIN (GPIO 4)
#define FLASH_LED_PIN 4

//농장
// const char *ssid = "SO070VOIP370D";
// const char *password = "726368370C";

//와이파이 설정 필요 & 서버 주소
const char *ssid = "NetDB_408";
const char *password = "netdb3230";
const char *post_url = "http://192.168.1.47:81/imageUp"; // Location where images are POSTED
// const char *post_url = "http://<<<<<<<<<<your-deployment>>>>>>>>>>>.herokuapp.com/upload-image"; // Location where images are POSTED

//======================================== Variables for Timer/Millis.
unsigned long previousMillis = 0; 
const int Interval = 1 * 1 * 300 ; //--> Capture and Send a photo every 60 seconds. => 1sed ,300ms 간격으로 정기적인 이미지 캡쳐

bool internet_connected = false;
#include <ArduinoOTA.h>
#include <ESPmDNS.h>
#include <WiFiUdp.h>

void CamSet();

void setup()
{
  WRITE_PERI_REG(RTC_CNTL_BROWN_OUT_REG, 0); //disable brownout detector

  Serial.begin(115200);
  //Serial.setDebugOutput(true);
  //Serial.println();
  if (init_wifi())
  { // Connected to WiFi
    internet_connected = true;
    Serial.println("Internet connected");
  }

  ///////////////////////////Camera Init//////////
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = Y2_GPIO_NUM;
  config.pin_d1 = Y3_GPIO_NUM;
  config.pin_d2 = Y4_GPIO_NUM;
  config.pin_d3 = Y5_GPIO_NUM;
  config.pin_d4 = Y6_GPIO_NUM;
  config.pin_d5 = Y7_GPIO_NUM;
  config.pin_d6 = Y8_GPIO_NUM;
  config.pin_d7 = Y9_GPIO_NUM;
  config.pin_xclk = XCLK_GPIO_NUM;
  config.pin_pclk = PCLK_GPIO_NUM;
  config.pin_vsync = VSYNC_GPIO_NUM;
  config.pin_href = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn = PWDN_GPIO_NUM;
  config.pin_reset = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  // config.xclk_freq_hz = 2000000;
  config.pixel_format = PIXFORMAT_JPEG;

  if (psramFound())
  {
    config.frame_size = FRAMESIZE_UXGA; // FRAMESIZE_ + QVGA|CIF|VGA|SVGA|XGA|SXGA|UXGA
    config.jpeg_quality = 10;
    config.fb_count = 2;
  }
  else
  {
    config.frame_size = FRAMESIZE_SVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  }

  // Init Camera
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK)
  {
    Serial.printf("Camera init failed with error 0x%x", err);
    delay(1000);
    ESP.restart();
  }
  //////////////////////////////////////////////////////////////////////////////

  CamSet();
}

//캡쳐한 이미지를 서버로 전송
void SendCapturedPhotos(){
  camera_fb_t *fb = NULL;
  digitalWrite(FLASH_LED_PIN, HIGH);
  // sleep(1);
  // pinMode(FLASH_LED_PIN, OUTPUT);
  // Take Picture with Camera
  fb = esp_camera_fb_get();
  if (!fb)
  {
    Serial.println("Camera capture failed");
    return;
  }
  // // initialize EEPROM with predefined size
  // EEPROM.begin(EEPROM_SIZE);
  // pictureNumber = EEPROM.read(0) + 1;


  // Turns off the ESP32-CAM white on-board LED (flash) connected to GPIO 4
  digitalWrite(FLASH_LED_PIN, LOW);
  rtc_gpio_hold_en(GPIO_NUM_4);

  HTTPClient http;

  Serial.print("[HTTP] begin...\n");
  // configure traged server and url

  http.begin(post_url); //HTTP

  Serial.print("[HTTP] POST...\n");
  // start connection and send HTTP header
  int httpCode = http.sendRequest("POST", fb->buf, fb->len); // we simply put the whole image in the post body.

  // httpCode will be negative on error
  if (httpCode > 0)
  {
    // HTTP header has been send and Server response header has been handled
    Serial.printf("[HTTP] POST... code: %d\n", httpCode);

    // file found at server
    if (httpCode == HTTP_CODE_OK)
    {
      String payload = http.getString();
      Serial.println(payload);
    }
  }
  else
  {
    Serial.printf("[HTTP] POST... failed, error: %s\n", http.errorToString(httpCode).c_str());
  }

  http.end();

  esp_camera_fb_return(fb);

  Serial.println("This will never be printed");
  delay(200);
  // // delay(2000);
  // Serial.println("Going to sleep now");
  // // delay(2000);
  // delay(20);
  // esp_deep_sleep_start();
  
}

void CamSet()
{
  sensor_t * s = esp_camera_sensor_get();
  s->set_brightness(s, 0);     // -2 to 2
  s->set_contrast(s, 2);       // -2 to 2
  s->set_saturation(s, -2);     // -2 to 2
  s->set_special_effect(s, 0); // 0 to 6 (0 - No Effect, 1 - Negative, 2 - Grayscale, 3 - Red Tint, 4 - Green Tint, 5 - Blue Tint, 6 - Sepia)
  s->set_whitebal(s, 1);       // 0 = disable , 1 = enable
  s->set_awb_gain(s, 1);       // 0 = disable , 1 = enable
  s->set_wb_mode(s, 0);        // 0 to 4 - if awb_gain enabled (0 - Auto, 1 - Sunny, 2 - Cloudy, 3 - Office, 4 - Home)
  s->set_exposure_ctrl(s, 1);  // 0 = disable , 1 = enable
  s->set_aec2(s, 0);           // 0 = disable , 1 = enable
  s->set_ae_level(s, 0);       // -2 to 2
  s->set_aec_value(s, 300);    // 0 to 1200
  s->set_gain_ctrl(s, 1);      // 0 = disable , 1 = enable
  s->set_agc_gain(s, 0);       // 0 to 30
  s->set_gainceiling(s, (gainceiling_t)0);  // 0 to 6
  s->set_bpc(s, 0);            // 0 = disable , 1 = enable
  s->set_wpc(s, 1);            // 0 = disable , 1 = enable
  s->set_raw_gma(s, 1);        // 0 = disable , 1 = enable
  s->set_lenc(s, 1);           // 0 = disable , 1 = enable
  s->set_hmirror(s, 0);        // 0 = disable , 1 = enable
  s->set_vflip(s, 0);          // 0 = disable , 1 = enable
  s->set_dcw(s, 1);            // 0 = disable , 1 = enable
  s->set_colorbar(s, 0);       // 0 = disable , 1 = enable
}

void loop(){
   // put your main code here, to run repeatedly:

  //---------------------------------------- Timer/Millis to capture and send photos to Google Drive every 20 seconds (see Interval variable).
  unsigned long currentMillis = millis();
  if (currentMillis - previousMillis >= Interval) {
    previousMillis = currentMillis;

    SendCapturedPhotos();
  }
  //---------------------------------------- 
}



bool init_wifi()
{
  int connAttempts = 0;
  Serial.println("\r\nConnecting to: " + String(ssid));
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
    if (connAttempts > 10)
      return false;
    connAttempts++;
  }
  return true;
}