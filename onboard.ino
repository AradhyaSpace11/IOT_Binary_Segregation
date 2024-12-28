#include <WiFi.h>
#include <PubSubClient.h>
#include <ESP32Servo.h>

// Wi-Fi credentials
const char* ssid = "";        // Your Wi-Fi SSID
const char* password = ""; // Your Wi-Fi password

// MQTT Broker
const char* mqtt_server = "192.168.50.197"; // Replace with your broker's IP address
const char* mqtt_topic = "esp32/commands";   // Topic to subscribe to
WiFiClient espClient;
PubSubClient client(espClient);

// Servo setup
Servo myServo;
const int servoPin = 15; // GPIO pin connected to the servo motor

// Function to connect to Wi-Fi
void setupWifi() {
  delay(10);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi.");
}

// Function to connect to MQTT broker
void reconnect() {
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");
    if (client.connect("ESP32Client")) {
      Serial.println("Connected to MQTT broker.");
      client.subscribe(mqtt_topic);
    } else {
      Serial.print("Failed, rc=");
      Serial.print(client.state());
      Serial.println(" Try again in 5 seconds.");
      delay(5000);
    }
  }
}

// Callback function to handle received MQTT messages
void callback(char* topic, byte* message, unsigned int length) {
  String receivedMessage;
  for (unsigned int i = 0; i < length; i++) {
    receivedMessage += (char)message[i];
  }
  Serial.print("Message received: ");
  Serial.println(receivedMessage);

  // Actuate servo based on received message
  if (receivedMessage == "c") {
    myServo.write(135); // Move servo to 120 degrees for blue detection
    Serial.println("Servo moved to 120 degrees (blue cap detected).");
  } else if (receivedMessage == "o") {
    myServo.write(180); // Move servo to 180 degrees for red detection
    Serial.println("Servo moved to 180 degrees (red cap detected).");
  }
}

void setup() {
  Serial.begin(115200);

  // Connect to Wi-Fi
  setupWifi();

  // Setup MQTT client
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);

  // Attach the servo
  myServo.attach(servoPin, 500, 2500);
  myServo.write(180); // Start at 0 degrees
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();
}
