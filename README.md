# Ultrasonic Sensor Data to PostgreSQL

This project demonstrates how to connect an ultrasonic sensor with an ESP32 microcontroller to send distance data to a PostgreSQL database using a Flask application.

## Table of Contents

- [Introduction](#introduction)
- [Components Required](#components-required)
- [Circuit Diagram](#circuit-diagram)
- [ESP32 Code](#esp32-code)
- [Flask Application](#flask-application)
- [Database Setup](#database-setup)
- [Running the Project](#running-the-project)

## Introduction

This project involves sending distance measurements from an ultrasonic sensor connected to an ESP32 to a PostgreSQL database via a Flask web server. The data is sent using HTTP POST requests and stored in the database for further analysis.

## Components Required

- ESP32 microcontroller
- Ultrasonic sensor (e.g., HC-SR04)
- Wi-Fi network
- Computer with Python installed
- PostgreSQL database

## Circuit Diagram

Connect the ultrasonic sensor to the ESP32 as follows:

- **TRIGGER_PIN (ESP32 GPIO 12)** to **Trigger Pin** of the sensor
- **ECHO_PIN (ESP32 GPIO 14)** to **Echo Pin** of the sensor
- **VCC** to **3.3V**
- **GND** to **GND**

## ESP32 Code

The ESP32 code handles the reading of the ultrasonic sensor and sending the data to the Flask server.

```cpp
#include <WiFi.h>
#include <HTTPClient.h>

#define TRIGGER_PIN  12
#define ECHO_PIN     14

const char* ssid = "your SSID";
const char* password = "your Password";

void setup() {
  Serial.begin(115200);
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
}

void loop() {
  long duration, distance;

  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  
  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2;  // Convert to cm

  if(WiFi.status() == WL_CONNECTED) {
    HTTPClient http;

    http.begin("http://192.168.XXX.XX:8080/sensor-data");  // URL endpoint backend Flask
    http.addHeader("Content-Type", "application/x-www-form-urlencoded");

    String postData = "distance=" + String(distance);
    int httpResponseCode = http.POST(postData);

    Serial.print("HTTP Response code: ");
    Serial.println(httpResponseCode);

    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  delay(10000);  // Kirim data setiap 10 detik
}

```
## Flask Application

The Flask application receives the data sent from the ESP32 and stores it in the PostgreSQL database.

```python
from flask import Flask, request, jsonify
import psycopg2

app = Flask(__name__)

# PostgreSQL connection configuration
conn = psycopg2.connect(
    host="localhost",
    database="sensor_db",
    user="sensor_ultrasonic_user",
    password="qwerty1234"
)
cursor = conn.cursor()

@app.route('/sensor-data', methods=['POST'])
def sensor_data():
    try:
        distance = request.form['distance']
        cursor.execute("INSERT INTO sensor_data (distance) VALUES (%s)", (distance,))
        conn.commit()
        return jsonify({"status": "success", "distance": distance}), 201
    except Exception as e:
        # Log error for debugging
        print(f"Error: {e}")
        conn.rollback()  # Rollback the transaction in case of error
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
```
## Database Setup

To set up the PostgreSQL database for this project, follow these steps:

1. **Install PostgreSQL**: Ensure PostgreSQL is installed on your machine. You can download it from the [official PostgreSQL website](https://www.postgresql.org/download/).

2. **Create the Database**:
   Open a terminal or command prompt and run the following commands to create a new database:
   ```sql
   CREATE DATABASE sensor_db;
   ```
3. **Create a User**:
   Create a new user with the necessary privileges. Replace your_password with your desired password:
```sql
CREATE USER sensor_ultrasonic_user WITH PASSWORD 'qwerty1234';
```
4. **Grant Privileges**: Grant all privileges on the newly created database to the user:
```sql
GRANT ALL PRIVILEGES ON DATABASE sensor_db TO sensor_ultrasonic_user;
```
5. **Create the Table**: Connect to the sensor_db database and create the sensor_data table using the following SQL command:
 ```sql
   CREATE TABLE sensor_data (
    id SERIAL PRIMARY KEY,
    distance DOUBLE PRECISION NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```
6. **Verify the Table**: To ensure the table is created correctly, you can list the tables and view the structure:
```sql
\dt
\d sensor_data
```
This setup will prepare your PostgreSQL database to receive and store the sensor data sent from the ESP32 via the Flask application.

Feel free to adjust the instructions or add any additional setup steps specific to your environment!



