from flask import Blueprint, jsonify, request
from .river_emotion import analyze_emotion
from .drowning_detection import detect_drowning
from .alerts import send_alert
from .suggestions import get_suggestions
from .climate_visualizer import get_climate_data

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def home():
    return {'message': 'Welcome to RiverMind API'}

@main_bp.route('/api/emotion', methods=['POST'])
def emotion_analysis():
    data = request.json
    result = analyze_emotion(data.get('text'))
    return jsonify(result)

@main_bp.route('/api/drowning', methods=['POST'])
def drowning_detection():
    video_file = request.files.get('video')
    if not video_file:
        return jsonify({'error': 'No video file provided'}), 400
    
    result = detect_drowning(video_file)
    return jsonify(result)

@main_bp.route('/api/alerts', methods=['POST'])
def send_emergency_alert():
    data = request.json
    result = send_alert(
        data.get('type'),
        data.get('message'),
        data.get('recipient')
    )
    return jsonify(result)

@main_bp.route('/api/suggestions', methods=['GET'])
def get_ai_suggestions():
    user_id = request.args.get('user_id')
    result = get_suggestions(user_id)
    return jsonify(result)

@main_bp.route('/api/climate', methods=['GET'])
def climate_data():
    result = get_climate_data()
    return jsonify(result) 