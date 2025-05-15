/**
 * RiverMind - Global JavaScript Functions
 * Handles common functionality across all pages
 */

// API endpoints
const API_BASE_URL = 'http://localhost:8001';

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

// Mobile menu toggle functionality
document.addEventListener('DOMContentLoaded', function() {
    // Mobile navigation menu
    initMobileMenu();
    
    // Add smooth scrolling to all anchor links
    addSmoothScrolling();
    
    // Add animation classes to elements as they scroll into view
    initScrollAnimations();
});

/**
 * Initialize the mobile menu toggle functionality
 */
function initMobileMenu() {
    const menuToggle = document.querySelector('.menu-toggle');
    const navLinks = document.querySelector('.nav-links');
    
    if (menuToggle && navLinks) {
        // Toggle menu when button is clicked
        menuToggle.addEventListener('click', function(e) {
            e.stopPropagation();
            navLinks.classList.toggle('active');
        });
        
        // Close menu when a link is clicked
        const links = navLinks.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('click', function() {
                navLinks.classList.remove('active');
            });
        });
        
        // Close menu when clicking outside
        document.addEventListener('click', function(e) {
            if (!navLinks.contains(e.target) && !menuToggle.contains(e.target)) {
                navLinks.classList.remove('active');
            }
        });
    }
}

/**
 * Add smooth scrolling to all anchor links
 */
function addSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            const href = this.getAttribute('href');
            
            if (href !== "#") {
                e.preventDefault();
                
                const targetElement = document.querySelector(href);
                if (targetElement) {
                    targetElement.scrollIntoView({
                        behavior: 'smooth'
                    });
                }
            }
        });
    });
}

/**
 * Add animation classes to elements as they scroll into view
 */
function initScrollAnimations() {
    // Add fade-in class to elements with data-animate attribute
    const animatedElements = document.querySelectorAll('[data-animate]');
    
    if (animatedElements.length > 0) {
        // Create IntersectionObserver
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('fade-in');
                    // Stop observing after animation is applied
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1
        });
        
        // Observe each element
        animatedElements.forEach(element => {
            observer.observe(element);
        });
    }
}

/**
 * Check if an element is in the viewport
 * @param {HTMLElement} element - The element to check
 * @returns {boolean} - True if element is in viewport
 */
function isInViewport(element) {
    const rect = element.getBoundingClientRect();
    return (
        rect.top >= 0 &&
        rect.left >= 0 &&
        rect.bottom <= (window.innerHeight || document.documentElement.clientHeight) &&
        rect.right <= (window.innerWidth || document.documentElement.clientWidth)
    );
}

/**
 * Format date strings for display
 * @param {string} dateString - ISO date string
 * @returns {string} - Formatted date string
 */
function formatDate(dateString) {
    const options = { year: 'numeric', month: 'short', day: 'numeric' };
    return new Date(dateString).toLocaleDateString(undefined, options);
}

/**
 * Add loading indicators to elements
 * @param {HTMLElement} element - Element to show loading state
 * @param {boolean} isLoading - Whether element is in loading state
 */
function setLoadingState(element, isLoading) {
    if (isLoading) {
        element.classList.add('loading');
        element.setAttribute('aria-busy', 'true');
    } else {
        element.classList.remove('loading');
        element.setAttribute('aria-busy', 'false');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
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
