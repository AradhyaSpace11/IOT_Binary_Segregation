import cv2
import numpy as np
from ultralytics import YOLO

# Load the YOLOv8 model
model = YOLO("best.pt")

# IP camera URL
ip_camera_url = "http://192.0.0.4:8080/video"
cap = cv2.VideoCapture(ip_camera_url)

if not cap.isOpened():
    print("Error: Could not connect to IP camera.")
    exit()

# Constants
REGION_SIZE = 400
CONFIDENCE_THRESHOLD = 0.4  # Adjust this value between 0 and 1

while True:
    ret, frame = cap.read()
    
    if not ret:
        print("Error: Could not receive frame from IP camera.")
        break

    # Get frame dimensions
    height, width = frame.shape[:2]
    
    # Calculate the coordinates for the center square
    x_start = width//2 - REGION_SIZE//2
    y_start = height//2 - REGION_SIZE//2
    x_end = x_start + REGION_SIZE
    y_end = y_start + REGION_SIZE

    # Extract the region of interest (ROI)
    roi = frame[y_start:y_end, x_start:x_end]

    # Perform inference only on the ROI
    results = model(roi)[0]

    # Filter detections based on confidence threshold
    confident_detections = [box for box in results.boxes if float(box.conf) >= CONFIDENCE_THRESHOLD]
    
    # Get number of confident detections
    num_objects = len(confident_detections)
    print(f"{num_objects} bottlecaps detected with confidence >= {CONFIDENCE_THRESHOLD}")

    # Draw the detection region border
    cv2.rectangle(frame, (x_start, y_start), (x_end, y_end), (255, 0, 0), 2)

    # Draw only the confident detections
    for box in confident_detections:
        # Get box coordinates (relative to ROI)
        x1, y1, x2, y2 = box.xyxy[0]
        
        # Convert coordinates to integers and adjust to full frame coordinates
        x1 = int(x1) + x_start
        y1 = int(y1) + y_start
        x2 = int(x2) + x_start
        y2 = int(y2) + y_start
        
        # Draw bounding box
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
        
        # Add confidence score
        conf = float(box.conf)
        cv2.putText(frame, f'{conf:.2f}', (x1, y1 - 10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

    # Draw text indicating detection region and threshold
    cv2.putText(frame, f"Detection Region (Conf >= {CONFIDENCE_THRESHOLD})", 
                (x_start, y_start - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

    # Display the frame
    cv2.imshow('YOLOv8 IP Camera Inference', frame)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()