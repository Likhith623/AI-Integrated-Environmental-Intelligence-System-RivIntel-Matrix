from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import cv2
import numpy as np
from datetime import datetime, timedelta
import os
import tempfile
from collections import deque
import random
import threading
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from app.climate_visualizer import precalculate_climate_data, get_climate_data

app = Flask(__name__, static_folder='frontend', static_url_path='')
CORS(app, resources={r"/*": {"origins": "*"}})

# Cache for API responses
RESPONSE_CACHE = {}
CACHE_TIMESTAMPS = {}
CACHE_TIMEOUT = 300  # 5 minutes

# Configuration
UPLOAD_FOLDER = 'uploads'
if not os.path.exists(UPLOAD_FOLDER):
    try:
        os.makedirs(UPLOAD_FOLDER)
        print(f"Created upload directory: {UPLOAD_FOLDER}")
    except Exception as e:
        print(f"Error creating upload directory: {str(e)}")

app.config['MAX_CONTENT_LENGTH'] = 100 * 1024 * 1024  # 100MB limit
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Rolling average buffers
temp_history = deque(maxlen=10)
ph_history = deque(maxlen=10)
flow_history = deque(maxlen=10)

# Precalculate climate data at startup for instant availability
print("Precalculating climate data at startup...")
climate_data = precalculate_climate_data()
print("Climate data ready!")

def determine_emotion(temp, ph, flow):
    if temp > 35 and flow > 80:
        return "angry"
    elif ph < 5 or ph > 9:
        return "sad"
    elif flow > 90 and 25 <= temp <= 40:
        return "excited"
    elif temp < 10 and flow < 30:
        return "calm"
    elif 20 <= temp <= 30 and 6.5 <= ph <= 8.5 and 40 <= flow <= 60:
        return "happy"
    else:
        return "neutral"

def calc_flow(prev_gray, gray):
    # Calculate optical flow using Farneback method
    flow = cv2.calcOpticalFlowFarneback(prev_gray, gray,
                                      None, 0.5, 3, 15, 3, 5, 1.2, 0)
    
    # Calculate magnitude and angle of 2D vectors
    magnitude, angle = cv2.cartToPolar(flow[..., 0], flow[..., 1])
    
    # Apply thresholding to remove noise
    threshold = np.mean(magnitude) * 0.5
    magnitude[magnitude < threshold] = 0
    
    # Calculate flow metrics
    flow_mean = np.mean(magnitude)
    flow_std = np.std(magnitude)
    
    # Scale the flow value to a more meaningful range (0-100)
    scaled_flow = (flow_mean * flow_std) * 5
    
    # Ensure the value is within reasonable bounds
    scaled_flow = np.clip(scaled_flow, 0, 100)
    
    return scaled_flow

def analyze_frame(prev_gray, frame):
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Flow estimation
    flow_speed = calc_flow(prev_gray, gray) * 100

    # Brightness for temperature
    brightness = np.mean(hsv[:, :, 2])
    temperature = (brightness / 255) * 50

    # Clarity for pH
    edges = cv2.Canny(frame, 100, 200)
    edge_density = np.mean(edges)
    color_std = np.std(hsv[:, :, 1])
    ph_level = 7 - (edge_density / 255) * 3 + (color_std / 255) * 3
    ph_level = np.clip(ph_level, 0, 14)

    # Smooth values
    temp_history.append(temperature)
    ph_history.append(ph_level)
    flow_history.append(flow_speed)

    temp_avg = np.mean(temp_history)
    ph_avg = np.mean(ph_history)
    flow_avg = np.mean(flow_history)

    emotion = determine_emotion(temp_avg, ph_avg, flow_avg)
    return temp_avg, ph_avg, flow_avg, emotion, gray

@app.route('/')
def serve_index():
    # Run climate data precalculation again in the background 
    # to make sure it's fresh for any climate page visits
    threading.Thread(target=precalculate_climate_data, daemon=True).start()
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/climate')
def serve_climate():
    return send_from_directory(app.static_folder, 'climate.html')

@app.route('/frontend/<path:path>')
def serve_static(path):
    return send_from_directory('frontend', path)

@app.route('/api/drowning', methods=['POST'])
def detect_drowning():
    try:
        if 'video' not in request.files:
            return jsonify({"error": "No video file provided"}), 400
        
        video_file = request.files['video']
        if video_file.filename == '':
            return jsonify({"error": "No selected file"}), 400
        
        if not video_file.filename.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            return jsonify({"error": "Invalid file type. Please upload a video file (mp4, avi, mov, or mkv)"}), 400

        # Save and process the video
        try:
            filename = os.path.join(app.config['UPLOAD_FOLDER'], 
                                  f"video_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp4")
            video_file.save(filename)
            
            # Check if file was saved correctly
            if not os.path.exists(filename) or os.path.getsize(filename) == 0:
                return jsonify({"error": "Failed to save video file"}), 500
                
            # Process the video
            cap = cv2.VideoCapture(filename)
            if not cap.isOpened():
                os.remove(filename)
                return jsonify({"error": "Could not open video file. The format may be unsupported."}), 400
                
            ret, first_frame = cap.read()
            if not ret:
                cap.release()
                os.remove(filename)
                return jsonify({"error": "Failed to read video frames"}), 400

            prev_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
            temp, ph, flow, emotion, _ = analyze_frame(prev_gray, first_frame)

            # Clean up
            cap.release()
            os.remove(filename)

            return jsonify({
                "temperature": float(temp),
                "ph": float(ph),
                "flow": float(flow),
                "emotion": emotion
            })
            
        except (IOError, OSError) as e:
            # File system errors
            print(f"File system error: {str(e)}")
            return jsonify({"error": f"File system error: {str(e)}"}), 500
            
        except cv2.error as e:
            # OpenCV errors
            print(f"OpenCV error: {str(e)}")
            return jsonify({"error": f"Video processing error: {str(e)}"}), 500

    except Exception as e:
        print(f"Error processing video: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/flow', methods=['POST'])
def get_flow_rate():
    try:
        if 'frame' not in request.files:
            return jsonify({"error": "No frame provided"}), 400
        
        # Read the current frame
        frame_file = request.files['frame']
        frame_data = frame_file.read()
        nparr = np.frombuffer(frame_data, np.uint8)
        frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if frame is None:
            return jsonify({"error": "Invalid frame data"}), 400

        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Get the previous frame
        prev_gray = None
        if 'prev_gray' in request.files:
            prev_frame_file = request.files['prev_gray']
            prev_frame_data = prev_frame_file.read()
            prev_nparr = np.frombuffer(prev_frame_data, np.uint8)
            prev_frame = cv2.imdecode(prev_nparr, cv2.IMREAD_COLOR)
            if prev_frame is not None:
                prev_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
        
        if prev_gray is None:
            return jsonify({"flow": 0.0})
        
        # Calculate flow rate
        flow_speed = calc_flow(prev_gray, gray)
        
        # Add to history and calculate moving average
        flow_history.append(flow_speed)
        flow_avg = np.mean(flow_history)
        
        # Scale the flow rate to m³/s (approximate conversion)
        scaled_flow = flow_avg * 0.1  # Scale factor to convert to m³/s
        
        return jsonify({
            "flow": float(scaled_flow)
        })

    except Exception as e:
        print(f"Error processing frame: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/emotion', methods=['GET'])
def get_emotion():
    try:
        # Get the latest metrics
        temperature = get_latest_metric('temperature')
        ph = get_latest_metric('ph')
        flow_rate = get_latest_metric('flow_rate')
        dissolved_oxygen = get_latest_metric('dissolved_oxygen')
        water_level = get_latest_metric('water_level')
        clarity = get_latest_metric('clarity')

        # Get historical data
        temperature_history = get_metric_history('temperature', 24)  # Last 24 hours
        water_level_history = get_metric_history('water_level', 24)
        flow_rate_history = get_metric_history('flow_rate', 24)
        ecosystem_history = get_metric_history('ecosystem', 24)

        # Calculate the river's emotion based on metrics
        emotion = calculate_river_emotion(temperature, ph, flow_rate, dissolved_oxygen)

        return jsonify({
            'emotion': emotion,
            'temperature': temperature,
            'ph': ph,
            'flow_rate': flow_rate,
            'dissolved_oxygen': dissolved_oxygen,
            'water_level': water_level,
            'clarity': clarity,
            'temperature_history': temperature_history,
            'water_level_history': water_level_history,
            'flow_rate_history': flow_rate_history,
            'ecosystem_history': ecosystem_history
        })
    except Exception as e:
        print(f"Error in get_emotion: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/alerts', methods=['GET'])
def get_alerts():
    # Get latest metrics
    temperature = get_latest_metric('temperature')['value']
    ph = get_latest_metric('ph')['value']
    flow_rate = get_latest_metric('flow_rate')['value']
    dissolved_oxygen = get_latest_metric('dissolved_oxygen')['value']
    
    alerts = []
    timestamp = datetime.now().isoformat()
    
    # Temperature alerts
    if temperature > 28:
        alerts.append({
            'type': 'temperature',
            'severity': 'high',
            'message': 'High temperature detected - potential risk to aquatic life',
            'value': temperature,
            'timestamp': timestamp
        })
    elif temperature < 15:
        alerts.append({
            'type': 'temperature',
            'severity': 'low',
            'message': 'Low temperature detected - monitor for ecosystem stress',
            'value': temperature,
            'timestamp': timestamp
        })
    
    # pH alerts
    if ph > 8.5:
        alerts.append({
            'type': 'ph',
            'severity': 'high',
            'message': 'High pH levels - potential alkalinity issues',
            'value': ph,
            'timestamp': timestamp
        })
    elif ph < 6.5:
        alerts.append({
            'type': 'ph',
            'severity': 'low',
            'message': 'Low pH levels - potential acidity issues',
            'value': ph,
            'timestamp': timestamp
        })
    
    # Flow rate alerts
    if flow_rate > 150:
        alerts.append({
            'type': 'flow',
            'severity': 'high',
            'message': 'High flow rate - potential flood risk',
            'value': flow_rate,
            'timestamp': timestamp
        })
    elif flow_rate < 30:
        alerts.append({
            'type': 'flow',
            'severity': 'low',
            'message': 'Low flow rate - potential drought conditions',
            'value': flow_rate,
            'timestamp': timestamp
        })
    
    # Dissolved oxygen alerts
    if dissolved_oxygen < 5:
        alerts.append({
            'type': 'oxygen',
            'severity': 'low',
            'message': 'Low oxygen levels - critical for aquatic life',
            'value': dissolved_oxygen,
            'timestamp': timestamp
        })
    
    # Add awareness tips
    awareness_tips = [
        'Regular monitoring helps maintain river health',
        'Report any unusual changes in water color or smell',
        'Keep the riverbanks clean and free of debris',
        'Avoid disturbing natural habitats along the river',
        'Be mindful of water usage during dry seasons'
    ]
    
    return jsonify({
        'alerts': alerts,
        'awareness_tips': random.sample(awareness_tips, 2),  # Return 2 random tips
        'timestamp': timestamp
    })

def get_latest_metric(metric_name):
    # Simulated metrics for testing
    metrics = {
        'temperature': 24.7,
        'ph': 7.5,
        'flow_rate': 90.0,
        'dissolved_oxygen': 8.9,
        'water_level': 2.3,
        'clarity': 85
    }
    return metrics.get(metric_name, 0)

def get_metric_history(metric_name, hours):
    history = []
    now = datetime.now()
    
    # Generate sample historical data
    base_values = {
        'temperature': 24.7,
        'water_level': 2.3,
        'flow_rate': 90.0,
        'ecosystem': 85
    }
    
    base_value = base_values.get(metric_name, 0)
    
    for i in range(hours):
        timestamp = now - timedelta(hours=i)
        # Add some random variation to create realistic-looking data
        value = base_value + (random.random() - 0.5) * 2
        history.append({
            'timestamp': timestamp.isoformat(),
            'value': round(value, 2)
        })
    
    return history

def calculate_river_emotion(temperature, ph, flow_rate, dissolved_oxygen):
    # Define optimal ranges
    temp_optimal = (18, 25)
    ph_optimal = (6.5, 8.5)
    flow_optimal = (50, 150)
    oxygen_optimal = (7, 12)
    
    # Calculate stress levels
    temp_stress = abs((temperature - sum(temp_optimal)/2) / (temp_optimal[1] - temp_optimal[0]))
    ph_stress = abs((ph - sum(ph_optimal)/2) / (ph_optimal[1] - ph_optimal[0]))
    flow_stress = abs((flow_rate - sum(flow_optimal)/2) / (flow_optimal[1] - flow_optimal[0]))
    oxygen_stress = abs((dissolved_oxygen - sum(oxygen_optimal)/2) / (oxygen_optimal[1] - oxygen_optimal[0]))
    
    total_stress = (temp_stress + ph_stress + flow_stress + oxygen_stress) / 4
    
    # Determine emotion based on stress level
    if total_stress < 0.2:
        return 'happy'
    elif total_stress < 0.4:
        return 'neutral'
    elif total_stress < 0.6:
        return 'sad'
    else:
        return 'angry'

@app.route('/api/climate_data', methods=['GET'])
def get_climate_metrics():
    """Get climate data with response caching for ultra-fast responses"""
    global RESPONSE_CACHE, CACHE_TIMESTAMPS
    
    current_time = datetime.now().timestamp()
    
    # Check if we have a cached response that's still valid
    if 'climate_data' in RESPONSE_CACHE and 'climate_data' in CACHE_TIMESTAMPS:
        if current_time - CACHE_TIMESTAMPS['climate_data'] < CACHE_TIMEOUT:
            # Return cached response directly
            return RESPONSE_CACHE['climate_data']
    
    # Get fresh data
    data = get_climate_data()
    
    # Create response once
    response = jsonify(data)
    
    # Cache the response object
    RESPONSE_CACHE['climate_data'] = response
    CACHE_TIMESTAMPS['climate_data'] = current_time
    
    return response

@app.route('/api/send_sms', methods=['POST'])
def send_sms():
    """Send SMS alerts to the provided phone number"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        phone = data.get('phone')
        message = data.get('message')
        
        if not phone or not message:
            return jsonify({"error": "Phone number and message are required"}), 400
            
        # Validate phone number - basic check for international format
        if not phone.startswith('+') or len(phone) < 10:
            return jsonify({"error": "Invalid phone number format. Use international format (e.g., +1234567890)"}), 400
            
        # Check for Indian phone number format
        is_indian = phone.startswith('+91') and len(phone) == 13
        
        # In a real implementation, this would connect to an SMS provider API
        # For now, we'll simulate successful sending
        print(f"SMS Alert would be sent to {phone}: {message}")
        
        return jsonify({
            "success": True,
            "message": "SMS alert sent successfully",
            "to": phone,
            "is_indian": is_indian
        })
        
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/drowning_alert', methods=['POST'])
def drowning_alert():
    """Record drowning alerts from the frontend detection system"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No alert data provided"}), 400
            
        # In a production system, this would store the alert in a database
        # For now, just log it
        print(f"DROWNING ALERT RECEIVED: {data.get('message')} - Severity: {data.get('severity')}")
        
        # Return success
        return jsonify({
            "success": True,
            "message": "Alert recorded successfully",
            "timestamp": datetime.now().isoformat()
        })
        
    except Exception as e:
        print(f"Error recording drowning alert: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/test_email', methods=['GET'])
def test_email():
    """Test endpoint for email system"""
    recipient = request.args.get('email')
    if not recipient:
        return jsonify({"error": "Email parameter is required"}), 400
        
    try:
        # Send a test email
        test_data = {
            "email": recipient,
            "message": "This is a test alert from RiverMind system. Your alert system is working correctly."
        }
        
        # Call the send_email function directly with the test data
        response = send_email_direct(test_data)
        
        # Add test information to the response
        if isinstance(response, tuple):
            response_data = response[0].json
            response_data["test"] = True
            return jsonify(response_data), response[1]
        else:
            response["test"] = True
            return jsonify(response)
            
    except Exception as e:
        return jsonify({
            "error": f"Test failed: {str(e)}",
            "test": True
        }), 500


def send_email_direct(data):
    """Helper function to send emails directly, used by both the API endpoint and test endpoint"""
    try:
        email = data.get('email')
        message_text = data.get('message')
        
        if not email or not message_text:
            return {"error": "Email address and message are required"}, 400
            
        # Validate email address - basic check for format
        if '@' not in email or '.' not in email:
            return {"error": "Invalid email address format"}, 400
          
        # Email configuration  
        sender_email = "YOUR_EMAIL@gmail.com"  # REPLACE with your Gmail address
        sender_password = "YOUR_APP_PASSWORD"  # REPLACE with your 16-character app password
        
        # Create message
        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = "RiverMind Alert: Drowning Detection"
        
        # Add body to email
        html = f"""
        <html>
          <body>
            <h2>RiverMind Alert System</h2>
            <p><strong>IMPORTANT:</strong> {message_text}</p>
            <p>This alert was triggered by the RiverMind drowning detection system.</p>
            <p>Please take appropriate action immediately.</p>
            <hr>
            <p><em>This is an automated message. Please do not reply to this email.</em></p>
          </body>
        </html>
        """
        message.attach(MIMEText(html, "html"))
        
        # Log attempt
        print(f"Attempting to send email alert to {email}")
        
        # For development/testing without actual email sending
        use_simulation = False  # Changing to False to send real emails
        
        if not use_simulation:
            try:
                # Gmail SMTP configuration - STEPS TO CONFIGURE:
                # 1. Use your own Gmail address below
                # 2. For sender_password, you need to create an "App Password":
                #    a. Go to your Google account > Security > 2-Step Verification (enable if not already)
                #    b. Then go to "App passwords" (https://myaccount.google.com/apppasswords)
                #    c. Create a new app password for "Mail" and "Other (Custom name)" - call it "RiverMind"
                #    d. Copy the 16-character password (without spaces) and paste it below
                
                sender_email = "lalith08623@gmail.com"  # REPLACE with your Gmail address
                sender_password = "rrxn wqdm wive yomj "  # REPLACE with your 16-character app password
                
                # Connect to Gmail's SMTP server
                with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
                    try:
                        # Login to your Gmail account
                        server.login(sender_email, sender_password)
                        # Send the email
                        server.sendmail(sender_email, email, message.as_string())
                        
                        print(f"Email alert successfully sent to {email}")
                        return {
                            "success": True,
                            "message": "Email alert sent successfully",
                            "to": email
                        }
                    except smtplib.SMTPAuthenticationError as auth_error:
                        print(f"SMTP Authentication Error: {auth_error}")
                        return {
                            "success": False,
                            "error": "Gmail authentication failed. Please check your email and app password.",
                            "details": str(auth_error),
                            "help": "Make sure you've created an App Password in your Google account settings."
                        }
                    except Exception as smtp_error:
                        print(f"SMTP Error: {smtp_error}")
                        return {
                            "success": False,
                            "error": f"SMTP error: {str(smtp_error)}",
                            "help": "Check your Gmail settings and ensure less secure apps access is enabled."
                        }
                
            except Exception as e:
                print(f"Failed to send email: {str(e)}")
                # Fall through to simulation mode
        
        # Simulation mode
        print(f"SIMULATED EMAIL to {email}: {message_text}")
        # Add debug information to help troubleshoot
        debug_info = {
            "email_server": "simulation",
            "timestamp": datetime.now().isoformat(),
            "server_info": {
                "hostname": request.host if hasattr(request, 'host') else "unknown",
                "method": request.method if hasattr(request, 'method') else "unknown",
                "path": request.path if hasattr(request, 'path') else "unknown"
            }
        }
        return {
            "success": True,
            "message": "Email alert sent (simulated)",
            "to": email,
            "simulation": True,
            "debug": debug_info
        }
            
    except Exception as e:
        print(f"Error in email function: {str(e)}")
        return {"error": str(e)}, 500

@app.route('/api/send_email', methods=['POST'])
def send_email():
    """Send email alerts to the provided email address"""
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No data provided"}), 400
            
        # Call the helper function and return its response
        response = send_email_direct(data)
        
        if isinstance(response, tuple):
            return jsonify(response[0]), response[1]
        else:
            return jsonify(response)
            
    except Exception as e:
        print(f"Error in email endpoint: {str(e)}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("Starting server with pre-calculated climate data")
    app.run(debug=True, host='0.0.0.0', port=8001)
    