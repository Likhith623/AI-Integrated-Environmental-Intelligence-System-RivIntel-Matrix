# 🌊 River Intel Matrix

**RiverMind** is a revolutionary AI-powered environmental monitoring system that personifies a river’s condition in real time—giving it emotions, voice, and data intelligence. This project fuses environmental science with emotional AI, computer vision, and climate awareness to bring a **living, breathing emotional diary** of rivers to life.

## 🧠 Project Vision

> "What if rivers could feel? What if they could speak to us about their health, pain, or joy?"

RiverMind turns this question into reality by analyzing data, detecting threats, and visualizing a river’s *emotional state*—offering insights into pollution, drowning incidents, ecosystem changes, and climate patterns.

---

## 🎯 Core Features

- 🔬 **Real-Time Environmental Monitoring**  
  Captures key stats about river health: pollution, flow speed, climate patterns, and more.

- 🎭 **Emotional AI Engine**  
  Converts environmental data into emotional personas—visualizing the river’s “feelings” like stress, happiness, danger, or calm.

- 🆘 **Drowning Detection System**  
  Uses OpenCV to monitor river banks or camera feeds for drowning behavior or erratic human movement.

- 🌱 **Eco-Suggestions & Crisis Alerts**  
  Offers actionable advice to communities and sends real-time alerts during critical events like high pollution or water-level surges.

- 📈 **Climate Visualization & Analytics**  
  Shows graphs of seasonal shifts, rainfall impact, pollution levels, and temperature trends using data visualization.

---

## 🧰 Tech Stack

| Technology | Role |
|------------|------|
| `Python` | Core scripting language |
| `OpenCV` | Drowning detection, video processing |
| `MediaPipe` | (Optional) Enhanced human pose tracking |
| `Streamlit` | Beautiful real-time web UI |
| `Matplotlib` / `Plotly` | Interactive climate data visualizations |
| `Pandas` / `NumPy` | Data manipulation and analysis |
| `Custom AI Logic` | Emotion engine to interpret environmental signals |
| `Flask (optional)` | API backend integration |

---

📊 Visual Outputs
📉 Pollution level graphs

🌧️ Rainfall-vs-water-level plots

🌡️ Temperature vs river health trend lines

🎞️ Real-time frame detection of human behavior in the water


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
## 👨‍💻 Author

**Likhith Vasireddy**
- GitHub: [@Likhith623](https://github.com/Likhith623)

  
🤝 Collaborate With Us


Want to add multilingual support, voice narration, or integrate real sensors like Arduino + pH/flow monitors? Contributions are welcome! Let’s build the future of intelligent ecosystems.


