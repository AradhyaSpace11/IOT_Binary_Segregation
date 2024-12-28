import cv2
import numpy as np
import paho.mqtt.client as mqtt
from flask import Flask, jsonify, render_template_string, request
from flask_cors import CORS
import threading
import json
import os
from ultralytics import YOLO

# Configuration
VIDEO_URL = 'http://192.0.0.4:8080/video'
MQTT_BROKER = "192.168.50.197"
MQTT_PORT = 1883
MQTT_TOPIC = "esp32/commands"
REGION_SIZE = 400
BLACKISH_THRESHOLD = 100  # Threshold for detecting blackish pixels
CONFIDENCE_THRESHOLD = 0.5
JSON_FILE = "counts.json"

# Flask app setup
app = Flask(__name__)
CORS(app)

# Initialize counts JSON
if not os.path.exists(JSON_FILE):
    initial_data = {
        "Bottle Caps": 0,
        "Defective Pieces": 0
    }
    with open(JSON_FILE, 'w') as f:
        json.dump(initial_data, f, indent=4)

# MQTT client setup
mqtt_client = mqtt.Client()
def connect_to_mqtt():
    try:
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        print("Connected to MQTT broker.")
    except Exception as e:
        print(f"Failed to connect to MQTT broker: {e}")
        exit()
connect_to_mqtt()

# Load YOLO model
model = YOLO("best.pt")

# Initialize video capture
cap = cv2.VideoCapture(VIDEO_URL)
if not cap.isOpened():
    print(f"Failed to connect to video stream at {VIDEO_URL}")
    exit()

# Helper functions
def update_json(field, increment=1):
    with open(JSON_FILE, 'r+') as f:
        data = json.load(f)
        data[field] += increment
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()

@app.route('/reset', methods=['POST'])
def reset_counts():
    initial_data = {
        "Bottle Caps": 0,
        "Defective Pieces": 0
    }
    with open(JSON_FILE, 'w') as f:
        json.dump(initial_data, f, indent=4)
    return jsonify({"status": "success"})

@app.route('/counts', methods=['GET'])
def get_counts():
    with open(JSON_FILE, 'r') as f:
        return jsonify(json.load(f))

@app.route('/')
def index():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Cap Counter</title>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; }
            .container { width: 80%; margin: auto; text-align: center; padding: 20px; }
            table { margin: 20px auto; border-collapse: collapse; width: 50%; }
            th, td { border: 1px solid #ddd; padding: 10px; text-align: center; }
            th { background-color: #4CAF50; color: white; }
            button { 
                padding: 10px 20px; 
                background-color: #ff4444; 
                color: white; 
                border: none; 
                border-radius: 4px; 
                cursor: pointer; 
                margin: 20px; 
            }
            button:hover { background-color: #cc0000; }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Cap Counter Dashboard</h1>
            <table>
                <tr><th>Type</th><th>Count</th></tr>
                <tr><td>Bottle Caps</td><td id="bottleCaps">0</td></tr>
                <tr><td>Defective Pieces</td><td id="defectivePieces">0</td></tr>
            </table>
            <button onclick="resetCounts()">Reset Counts</button>
        </div>
        <script>
            function fetchCounts() {
                fetch('/counts')
                    .then(response => response.json())
                    .then(data => {
                        document.getElementById('bottleCaps').textContent = data["Bottle Caps"];
                        document.getElementById('defectivePieces').textContent = data["Defective Pieces"];
                    });
            }

            function resetCounts() {
                fetch('/reset', { method: 'POST' })
                    .then(response => response.json())
                    .then(data => {
                        if(data.status === 'success') {
                            fetchCounts();
                        }
                    });
            }

            setInterval(fetchCounts, 1000);
        </script>
    </body>
    </html>
    """
    return render_template_string(html_content)

# Video processing logic
def process_video_stream():
    last_color = "black"
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Error: Could not read frame.")
            break

        height, width, _ = frame.shape

        # Center pixel color
        center_pixel = frame[height // 2, width // 2]
        is_blackish = np.all(center_pixel < [BLACKISH_THRESHOLD] * 3)

        # Detection region (center square)
        x_start = width // 2 - REGION_SIZE // 2
        y_start = height // 2 - REGION_SIZE // 2
        x_end = x_start + REGION_SIZE
        y_end = y_start + REGION_SIZE
        roi = frame[y_start:y_end, x_start:x_end]
        
        # Run YOLO on ROI for visualization
        results = model(roi)[0]
        detections = [box for box in results.boxes if float(box.conf) >= CONFIDENCE_THRESHOLD]
        
        # Draw detection boxes
        for box in detections:
            # Get coordinates relative to ROI
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            
            # Adjust coordinates to full frame
            x1 += x_start
            y1 += y_start
            x2 += x_start
            y2 += y_start
            
            # Draw bounding box
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Add confidence score
            conf = float(box.conf)
            cv2.putText(frame, f'Cap: {conf:.2f}', (x1, y1 - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
        
        if not is_blackish and last_color == "black":
            # Object detected, use existing detections
            if detections:
                # Bottle cap detected
                update_json("Bottle Caps")
                mqtt_client.publish(MQTT_TOPIC, "o")
                print("Bottle cap detected - MQTT: o")
            else:
                # No bottle cap detected - defective piece
                update_json("Defective Pieces")
                mqtt_client.publish(MQTT_TOPIC, "c")
                print("Defective piece detected - MQTT: c")

        # Update last color
        last_color = "black" if is_blackish else "not_black"

        # Draw detection region and center point
        cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (255, 0, 0), 2)
        cv2.circle(frame, (width // 2, height // 2), 5, (0, 255, 0), -1)
        
        # Add status text
        status = "Status: Conveyor" if is_blackish else "Status: Object Detected"
        cv2.putText(frame, status, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)
        
        cv2.imshow("Detection", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

# Start video processing in a thread
video_thread = threading.Thread(target=process_video_stream, daemon=True)
video_thread.start()

# Start Flask server
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3000)