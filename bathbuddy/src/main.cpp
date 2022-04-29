#include <Arduino.h>
#include <ESP8266WiFi.h>
#include <WiFiClient.h>
#include <ESP8266HTTPClient.h>
#include <secrets.h>

// Comment out when compiling for ESP8266-01S
#define NODEMCU

#ifdef NODEMCU
const int PIN_TOOTH = 14; //D5
const int PIN_HAND = 12; //D6
const int PIN_INFINI = 13; //D7
const int STATUS_LED = 2; //internal LED give some feedback
#else
const int PIN_TOOTH = 0;
const int PIN_HAND = 2;
const int PIN_INFINI = 3;
#endif


HTTPClient http;
WiFiClient client;

void wifiSetup() {
  //Setze WIFI-Module auf STA mode
  WiFi.mode(WIFI_STA);

  //Verbinden
  #ifdef NODEMCU
  Serial.println();
  Serial.println("[WIFI] Verbinden mit " + String(WIFI_SSID) );
  #endif
  WiFi.begin(WIFI_SSID, WIFI_PASS);

  //Warten bis Verbindung hergestellt wurde
  while (WiFi.status() != WL_CONNECTED) {
      #ifdef NODEMCU
      Serial.print(".");
      #endif
      delay(500);
  }

  #ifdef NODEMCU
  Serial.println();

  // Connected, blick 3 times and print ifo to serial
  digitalWrite(STATUS_LED, HIGH); // Turn the STATUS_LED off by making the voltage HIGH
  delay(200); // Wait for a second
  digitalWrite(STATUS_LED, LOW); // Turn the STATUS_LED on (Note that LOW is the voltage level)
  delay(200); // Wait for a second
  digitalWrite(STATUS_LED, HIGH); // Turn the STATUS_LED off by making the voltage HIGH
  delay(200); // Wait for a second
  digitalWrite(STATUS_LED, LOW); // Turn the STATUS_LED on (Note that LOW is the voltage level)
  delay(200); // Wait for a second
  digitalWrite(STATUS_LED, HIGH); // Turn the STATUS_LED off by making the voltage HIGH
  delay(200); // Wait for a second
  digitalWrite(STATUS_LED, LOW); // Turn the STATUS_LED on (Note that LOW is the voltage level)

  Serial.println("[WIFI] STATION Mode connected, SSID: " + WiFi.SSID() + ", IP-Adresse: " + WiFi.localIP().toString());
  #endif
}

#ifdef NODEMCU
void pressFeedback() {
  digitalWrite(STATUS_LED, HIGH); // Turn the STATUS_LED off by making the voltage HIGH
  delay(200); // Wait for a second
  digitalWrite(STATUS_LED, LOW); // Turn the STATUS_LED on (Note that LOW is the voltage level)
  delay(200); // Wait for a second
  digitalWrite(STATUS_LED, HIGH); // Turn the STATUS_LED off by making the voltage HIGH
  delay(200); // Wait for a second
  digitalWrite(STATUS_LED, LOW); // Turn the STATUS_LED on (Note that LOW is the voltage level)
}
#endif

void setup() {
  delay(2000);
  // since we use 3 pins, we can only debug when using a nodemcu board
  #ifdef NODEMCU
  Serial.begin(115200);
  // Wait for serial to initialize.
  while(!Serial) { }
  pinMode(STATUS_LED, OUTPUT); // Initialize the LED pin as an output
  digitalWrite(STATUS_LED, LOW); // Let the LED shine
  #endif

  // Connect Wifi
  wifiSetup();

  // Define Input Pins
  pinMode(PIN_TOOTH, INPUT_PULLUP);
  pinMode(PIN_HAND, INPUT_PULLUP);
  pinMode(PIN_INFINI, INPUT_PULLUP);
}

void loop() {
  int btn_tooth = digitalRead(PIN_TOOTH);
  int btn_hand = digitalRead(PIN_HAND);
  int btn_infini = digitalRead(PIN_INFINI);
  if (btn_tooth == LOW) {
    #ifdef NODEMCU
    Serial.println("Sending Request for toothbrush");
    pressFeedback();
    #endif
    http.begin(client, "http://" + String(RASPI_IP) + "/toothbrush");
    http.GET();
    http.end();
  }
  if (btn_hand == LOW) {
    #ifdef NODEMCU
    Serial.println("Sending Request for handwash");
    pressFeedback();
    #endif
    http.begin(client, "http://" + String(RASPI_IP) + "/handwash");
    http.GET();
    http.end();
  }
  if (btn_infini == LOW) {
    #ifdef NODEMCU
    Serial.println("Sending Request for infinite");
    pressFeedback();
    #endif
    http.begin(client, "http://" + String(RASPI_IP) + "/infinite");
    http.GET();
    http.end();
  }

  #ifdef NODEMCU
  Serial.println("I'm awake, but I'm going into deep sleep mode until RESET pin is connected to a LOW signal");
  #endif
  ESP.deepSleep(0);
}