# RiverMind

RiverMind is a comprehensive river monitoring and safety system that combines real-time video analysis, emotion tracking, and climate data visualization to promote river safety and conservation.

## Features

- **Live Video Monitoring**: Real-time drowning detection using computer vision
- **Emotion Diary**: Track and analyze emotions related to river experiences
- **Climate Impact**: Visualize river levels and climate data
- **Safety Suggestions**: Get personalized safety tips and conservation advice

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
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details. 