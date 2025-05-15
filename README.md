# Riv-Intel Matrix

Riv-Intel Matrix is an intelligent river monitoring and conservation system that blends real-time video surveillance, emotional AI, and climate visualization to safeguard lives and ecosystems. It detects emergencies, tracks emotional experiences, and empowers proactive environmental action with intelligent alerts and data-driven insights.

## Features
 Live Video Monitoring: Real-time drowning detection using advanced computer vision techniques.

Emotion Diary: Analyze and archive emotional responses to river environments for behavioral insights and environmental empathy.

Climate Impact Visualization: Track river levels, temperature shifts, and other climate metrics through dynamic visual dashboards.

Smart Safety Suggestions: Get personalized conservation tips and river safety guidance based on current conditions.

Real-Time Alerts: Immediate notifications via Twilio for critical events like drowning detection or environmental hazards.

Actionable Diary Logs: Review emotional and environmental logs to take informed and compassionate action toward river care.

Eco-Awareness Tools: Interactive modules that suggest sustainable practices and highlight climate impact trends.
## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/rivermind.git
cd rivermind
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Running the Application

1. Start the backend server:
```bash
python main.py
```

2. In a separate terminal, serve the frontend:
```bash
cd frontend
python -m http.server 8000
```

3. Open your browser and navigate to:
- Frontend: http://localhost:8000
- Backend API: http://localhost:5000

## API Endpoints

- `POST /api/drowning`: Upload and analyze video for drowning detection
- `POST /api/emotion`: Analyze emotion from text input
- `GET /api/climate`: Get river level and climate data
- `GET /api/suggestions`: Get safety and conservation suggestions

## Project Structure

```
rivermind/
├── frontend/
│   ├── assets/
│   │   ├── css/
│   │   ├── js/
│   │   └── images/
│   ├── index.html
│   ├── monitor.html
│   ├── emotion_diary.html
│   ├── suggestions.html
│   └── climate.html
├── main.py
├── requirements.txt
└── README.md
```

## Contributing

1. Fork the repository
2. Create a feature branc
3. Commit your changes
4. Push to the branch
5. 
6. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
