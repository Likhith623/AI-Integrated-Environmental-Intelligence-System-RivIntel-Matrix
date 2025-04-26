// API endpoints
const API_BASE_URL = 'http://localhost:8002/api';

// Utility functions
async function fetchData(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE_URL}${endpoint}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...options.headers
            }
        });
        
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        
        return await response.json();
    } catch (error) {
        console.error('Error fetching data:', error);
        throw error;
    }
}

// Emotion Analysis
async function analyzeEmotion(text) {
    try {
        const result = await fetchData('/emotion', {
            method: 'POST',
            body: JSON.stringify({ text })
        });
        return result;
    } catch (error) {
        console.error('Error analyzing emotion:', error);
        return null;
    }
}

// Drowning Detection
async function detectDrowning(videoFile) {
    try {
        const formData = new FormData();
        formData.append('video', videoFile);
        
        const result = await fetch(`${API_BASE_URL}/drowning`, {
            method: 'POST',
            body: formData
        });
        
        return await result.json();
    } catch (error) {
        console.error('Error detecting drowning:', error);
        return null;
    }
}

// Climate Data
async function getClimateData() {
    try {
        const result = await fetchData('/climate');
        return result;
    } catch (error) {
        console.error('Error fetching climate data:', error);
        return null;
    }
}

// Suggestions
async function getSuggestions(userId) {
    try {
        const result = await fetchData(`/suggestions?user_id=${userId}`);
        return result;
    } catch (error) {
        console.error('Error fetching suggestions:', error);
        return null;
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    // Add smooth scrolling for navigation links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            document.querySelector(this.getAttribute('href')).scrollIntoView({
                behavior: 'smooth'
            });
        });
    });
    
    // Initialize any page-specific functionality
    const currentPage = window.location.pathname.split('/').pop();
    switch (currentPage) {
        case 'monitor.html':
            initializeMonitor();
            break;
        case 'emotion_diary.html':
            initializeEmotionDiary();
            break;
        case 'climate.html':
            initializeClimate();
            break;
    }
});

// Page-specific initializers
function initializeMonitor() {
    // Initialize video monitoring
    const videoElement = document.querySelector('#video-feed');
    if (videoElement) {
        // Add video stream handling
    }
}

function initializeEmotionDiary() {
    const emotionForm = document.querySelector('#emotion-form');
    if (emotionForm) {
        emotionForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const text = document.querySelector('#emotion-text').value;
            const result = await analyzeEmotion(text);
            // Update UI with result
        });
    }
}

function initializeClimate() {
    // Initialize climate data visualization
    getClimateData().then(data => {
        // Update charts with data
    });
} 
