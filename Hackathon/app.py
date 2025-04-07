import cv2
import torch
import torchvision
from flask import Flask, render_template, Response, jsonify

app = Flask(__name__)

# Load PyTorch pre-trained Faster R-CNN model
model = torchvision.models.detection.fasterrcnn_resnet50_fpn(pretrained=True)
model.eval()  # Set to evaluation mode

# COCO class labels (81 classes, including background)
COCO_CLASSES = [
    '__background__', 'person', 'bicycle', 'car', 'motorcycle', 'airplane', 'bus',
    'train', 'truck', 'boat', 'traffic light', 'fire hydrant', 'stop sign',
    'parking meter', 'bench', 'bird', 'cat', 'dog', 'horse', 'sheep', 'cow',
    'elephant', 'bear', 'zebra', 'giraffe', 'backpack', 'umbrella', 'handbag',
    'tie', 'suitcase', 'frisbee', 'skis', 'snowboard', 'sports ball', 'kite',
    'baseball bat', 'baseball glove', 'skateboard', 'surfboard', 'tennis racket',
    'bottle', 'wine glass', 'cup', 'fork', 'knife', 'spoon', 'bowl', 'banana',
    'apple', 'sandwich', 'orange', 'broccoli', 'carrot', 'hot dog', 'pizza',
    'donut', 'cake', 'chair', 'couch', 'potted plant', 'bed', 'dining table',
    'toilet', 'tv', 'laptop', 'mouse', 'remote', 'keyboard', 'cell phone',
    'microwave', 'oven', 'toaster', 'sink', 'refrigerator', 'book', 'clock',
    'vase', 'scissors', 'teddy bear', 'hair drier', 'toothbrush'
]

# Face detection with OpenCV Haar Cascades
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

alert_log = []

def detect_suspicious_activity(frame):
    alerts = []
    
    # Convert frame to RGB (PyTorch expects RGB)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img_tensor = torchvision.transforms.ToTensor()(rgb_frame)
    
    # Run object detection
    with torch.no_grad():
        predictions = model([img_tensor])
    
    # Check for prohibited objects (e.g., cell phone, book)
    prohibited_objects = []
    for box, label, score in zip(predictions[0]['boxes'], predictions[0]['labels'], predictions[0]['scores']):
        if score > 0.5:  # Confidence threshold
            class_name = COCO_CLASSES[label]
            if class_name in ["cell phone", "book", "laptop"]:
                prohibited_objects.append(class_name)
    
    if prohibited_objects:
        alerts.append(f"Prohibited objects: {', '.join(prohibited_objects)}")
    
    # Face detection
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.1, 4)
    
    if len(faces) == 0:
        alerts.append("No face detected")
    elif len(faces) > 1:
        alerts.append("Multiple faces detected")
    
    return alerts, frame

def generate_frames():
    camera = cv2.VideoCapture(0)
    while True:
        success, frame = camera.read()
        if not success:
            break
        
        alerts, processed_frame = detect_suspicious_activity(frame)
        if alerts:
            alert_log.extend(alerts)
            cv2.putText(processed_frame, alerts[0], (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        
        ret, buffer = cv2.imencode('.jpg', processed_frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_alerts')
def get_alerts():
    return jsonify({"alerts": alert_log[-10:]})

if __name__ == '__main__':
    app.run(debug=True)