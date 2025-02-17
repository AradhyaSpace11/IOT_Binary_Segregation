# IOT Binary Segregation

A computer vision-based IoT project for binary object segregation using ESP32 and MQTT protocol.

## Overview

This project implements a binary segregation system using computer vision and IoT technology. The system uses an ESP32 microcontroller and MQTT protocol for communication between components. For detailed information about the circuit diagram and model architecture, please refer to `Paper.pdf` in the Papers and Docs folder.

## Prerequisites

- ESP32 Development Board
- Mosquitto MQTT Broker
- Python 3.7+
- Git
- IP Camera or Webcam

## Installation and Setup

### 1. Install and Configure Mosquitto

1. Download and install Mosquitto MQTT Broker
2. Configure Mosquitto:
   ```bash
   # Open notepad in administrator mode
   # Navigate to mosquitto.conf (usually in C:\Program Files\mosquitto\)
   # Add the following line:
   listener 1883
   ```

### 2. Clone the Repository

```bash
git clone https://github.com/AradhyaSpace11/IOT_Binary_Segregation
cd IOT_Binary_Segregation
```

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure ESP32

1. Navigate to `ESP32_Onboard_Code` directory
2. Edit the WiFi credentials in the code:
   ```cpp
   const char* ssid = "YOUR_WIFI_SSID";
   const char* password = "YOUR_WIFI_PASSWORD";
   ```
3. Upload the code to your ESP32 using Arduino IDE or your preferred method

### 5. Configure Server Settings

Edit `server.py` and update the following variables:
```python
VIDEO_URL = 'YOUR_CAMERA_URL'  # Example: http://192.0.0.4:8080/video
MQTT_BROKER = "YOUR_COMPUTER_IP"  # Your laptop/PC's IP address
```

## Running the System

1. Start Mosquitto Broker:
   ```bash
   # Open CMD as administrator and run:
   mosquitto -c "C:\Program Files\mosquitto\mosquitto.conf" -v
   ```

2. Start your IP camera webserver or ensure your webcam is connected

3. Run the server:
   ```bash
   python server.py
   ```

4. Open your web browser and navigate to:
   ```
   http://localhost:3000
   ```

You should now see the segregation count and system status in your browser.

## System Architecture

- `ESP32_Onboard_Code/`: Contains the ESP32 firmware
- `server.py`: Main server script handling video processing and MQTT communication
- `Papers and Docs/`: Documentation including circuit diagrams and model details
- `requirements.txt`: Python dependencies

## Troubleshooting

1. If MQTT connection fails:
   - Verify Mosquitto is running
   - Check if the IP addresses are correctly configured
   - Ensure port 1883 is not blocked by firewall

2. If video stream isn't working:
   - Verify camera URL is correct
   - Check if camera is accessible from your network
   - Ensure required video codecs are installed

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## License

[MIT](https://choosealicense.com/licenses/mit/)
