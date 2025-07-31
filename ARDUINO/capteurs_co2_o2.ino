// CO2 --------------------------------------------------------------------------------
#include <SoftwareSerial.h>

SoftwareSerial swSer(A1, A0);
uint8_t cmd[9] = {0xFF, 0X01, 0x86, 0x00, 0x00, 0x00, 0x00, 0x00, 0x79};
uint8_t reset[9] = {0xFF, 0X01, 0x87, 0x00, 0x00, 0x00, 0x00, 0x00, 0x78};
uint8_t res[9] = {};
uint8_t idx = 0;
bool flag = false;
uint16_t co2 = 0;

// OXYGEN --------------------------------------------------------------------------------
#include "DFRobot_MultiGasSensor.h"

DFRobot_GAS_I2C gas(&Wire ,0x74);

// SCREEN --------------------------------------------------------------------------------
#include <SPI.h>
#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 64
#define SCREEN_HEIGHT 32
#define OLED_RESET -1
#define SCREEN_ADDRESS 0x3C
Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

// TIMING --------------------------------------------------------------------------------
unsigned long previousTime = 0;
bool speedBtnCliked = false;
uint8_t currentSpeedIndex = 0;
uint16_t currentSpeed = 1000;

void setup() {
  Serial.begin(9600);

  initDisplay();
  initPins();
  initCo2();
  initOxygen();
  delay(500);
}

void loop() {
  timing();
  buttons();
  delay(100);
}

void initPins() {
  pinMode(2, INPUT_PULLUP);
}

void initDisplay() {
  if(!display.begin(SSD1306_SWITCHCAPVCC, SCREEN_ADDRESS)) {
    Serial.println(F("SSD1306 allocation failed"));
    for(;;); // Don't proceed, loop forever
  }

  display.setTextSize(1); // Draw 2X-scale text
  display.setTextColor(SSD1306_WHITE);
  display.clearDisplay();
}

void initCo2() {
  swSer.begin(9600);

  delay(1000);

  while (swSer.available() == 0) {
    Serial.println("No CO2 sensor!");
    delay(1000);
  }
}

void initOxygen() {
  while(!gas.begin())
  {
    Serial.println("NO Deivces !");
    delay(500);
  }
  Serial.println("The device is connected successfully!");
  gas.changeAcquireMode(gas.PASSIVITY);
  delay(500);
  gas.setTempCompensation(gas.ON);
}

void timing() {
  if(millis() >= previousTime + currentSpeed) {
    readCo2();
    sendData();
    updateScreen();
    previousTime = millis();
  }
}

void buttons() {
  if(digitalRead(2) == HIGH) {

    if(!speedBtnCliked) {
      speedBtnCliked = true;
      ++currentSpeedIndex;
      previousTime = 0;

      if(currentSpeedIndex > 2) {
        currentSpeedIndex = 0;
      }
      switch (currentSpeedIndex) {
        case 0:
          currentSpeed = 1000;
          break;
        case 1:
          currentSpeed = 5000;
          break;
        case 2:
          currentSpeed = 10000;
          break;
      }
    }
  } else {
    speedBtnCliked = false;
  }
}

void readCo2() {
  uint16_t val = 0;
  float t;

  swSer.write(cmd, 9);

  while (swSer.available() > 0) {
    res[idx++] = swSer.read();
    flag = true;
  }

  idx = 0;
  if(flag) {
    flag = false;
    co2 = 0;
    delay(100);
    co2 += (uint16_t)res[2] <<8;
    delay(100);
    co2 += res[3];
    t = res[4];
  }
}

void updateScreen() {
  display.clearDisplay();
  display.setCursor(0, 0);
  display.println("CO2: " + String(co2));
  display.setCursor(0, 10);
  display.println("O2:  " + String(gas.readGasConcentrationPPM()));
  display.setCursor(0, 20);
  display.println("F:   " + String(currentSpeed));
  display.display();
}

void sendData() {
  Serial.println("CO2:" + String(co2));
  Serial.println("O2:" + String(gas.readGasConcentrationPPM()));
}

















